from __future__ import annotations
from copy import copy
from dataclasses import dataclass
from operator import add, floordiv, mul, sub
from tkinter import Button, Entry, StringVar, Tk
from typing import Any, Callable, Union

class App:
	def __init__(self):
		self.root = Tk()
		self.root.title("Calculator")
		self.entryVar = StringVar()
		Entry(self.root, width=44, state="readonly", textvariable=self.entryVar
			).grid(row=0, column=0, columnspan=5)
		self.reset()

		for i in range(9):
			CalcValBtn(self, 3 - i // 3, i % 3, CalcVal(i + 1))
		CalcValBtn(self, 4, 0, CalcVal(0), 3)

		for e in [(1, 3, add), (1, 4, sub), (2, 3, mul), (2, 4, floordiv)]:
			CalcValBtn(self, e[0], e[1], CalcVal(e[2]))

		EvalBtn(self, 3, 3, 2)

	def addItem(self, val: CalcVal):
		if self.lastItem is None:
			self.lastItem = CalcItem(None, val)
			self.firstItem = self.lastItem
		elif not self.lastItem.appendDigit(val):
			next = CalcItem(self.lastItem, val)
			self.lastItem.next = next
			self.lastItem = next
		self.updateEntry()

	def genItems(self):
		currItem = self.firstItem

		while currItem is not None:
			yield currItem
			currItem = currItem.next

	def genItemStrs(self):
		for item in self.genItems():
			yield str(item.val)

	def itemsByHighPriority(self):
		return sorted(self.genItems(), key=lambda x: -x.priority)

	def reset(self):
		self.firstItem: CalcItem = None
		self.lastItem: CalcItem = None

	def run(self):
		self.root.mainloop()

	def showRes(self, res: Union[int, RuntimeError, str]):
		self.entryVar.set(str(res))

	def updateEntry(self):
		self.entryVar.set(" ".join(self.genItemStrs()))

class Btn:
	def __init__(self, app: App, row: int, col: int, span: int, name: str):
		self.app = app
		Button(self.app.root, text=name, padx=40 * span, pady=20,
			command=self.onClick
		).grid(row=row, column=col, columnspan=span)

	def onClick(self):
		pass

@dataclass
class CalcItem:
	prev: CalcItem
	val: CalcVal

	def __post_init__(self):
		self.next: CalcItem = None
		self.priority = self.val.priority()

	def appendDigit(self, val: CalcVal):
		return self.val.appendDigit(val)

	def delete(self):
		self.prev = None
		self.next = None

	def deleteOp(self):
		self.prev.delete()
		self.next.delete()
		self.delete()

	def eval(self):
		self.reqOp()
		newNext = self.next.next
		newPrev = self.prev.prev
		new = CalcItem(newPrev, CalcVal(
			self.val(self.prev.toInt(), self.next.toInt())))
		new.next = newNext

		setPrev(newNext, new)
		setNext(newPrev, new)
		self.deleteOp()
		return new

	def isInt(self):
		return self.val.isInt()

	def isOp(self):
		return not self.isInt()

	def reqOp(self):
		if self.isInt():
			raise RuntimeError(f"{self.val} is not an operator.")
		if self.next is None or self.prev is None:
			raise RuntimeError(
				f"Operator {self.val} doesn't have both neighbors.")

	def toInt(self):
		if self.isOp():
			raise RuntimeError(
				f"Operator {self.val} is not a number.")
		return self.val.val

@dataclass
class CalcVal:
	val: Union[int, Operator]

	def __call__(self, a, b) -> int:
		return self.val(a, b)

	def __str__(self):
		return str(self.val) if self.isInt() else opInfo[self.val].name

	def appendDigit(self, o: CalcVal):
		if self.isInt() and o.isInt():
			self.val = self.val * 10 + o.val
			return True
		return False

	def isInt(self):
		return isinstance(self.val, int)

	def priority(self):
		return 0 if self.isInt() else opInfo[self.val].priority

class CalcValBtn(Btn):
	def __init__(self, app: App, row: int, col: int, val: CalcVal,
		span: int = 1
	):
		super().__init__(app, row, col, span, str(val))
		self.val = val

	def onClick(self):
		self.app.addItem(copy(self.val))

def evalItems(items: list[CalcItem]):
	try:
		if not items:
			return "No input."
		if len(items) == 1:
			return f"Sole number: {items[0].toInt()}"

		res = items[0]

		for item in items:
			if item.isInt():
				return res.toInt()
			res = item.eval()
	except RuntimeError as e:
		return e
	except ZeroDivisionError:
		return "Division by zero."

class EvalBtn(Btn):
	def __init__(self, app: App, row: int, col: int, span: int):
		super().__init__(app, row, col, span, "=")

	def onClick(self):
		self.app.showRes(evalItems(self.app.itemsByHighPriority()))
		self.app.reset()

Operator = Callable[[Any, Any], Any]

@dataclass
class OpInfo:
	name: str
	priority: int

opInfo = {
	add: OpInfo("+", 1),
	sub: OpInfo("-", 1),
	mul: OpInfo("*", 2),
	floordiv: OpInfo("/", 2)
}

def setNext(item: CalcItem, next: CalcItem):
	if item is not None:
		item.next = next

def setPrev(item: CalcItem, prev: CalcItem):
	if item is not None:
		item.prev = prev

if __name__ == "__main__":
	App().run()
