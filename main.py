from __future__ import annotations
from dataclasses import dataclass
from operator import add, floordiv, mul, sub
from tkinter import Button, Entry, Tk
from typing import Any, Callable, Union

class App:
	def __init__(self):
		self.root = Tk()
		self.root.title("Calculator")
		self.entry = Entry(self.root, width=44)
		self.entry.grid(row=0, column=0, columnspan=5)
		self.lastItem: CalcItem = None

		for i in range(9):
			CalcValBtn(self, 3 - i // 3, i % 3, CalcVal(i + 1))
		CalcValBtn(self, 4, 0, CalcVal(0), 3)

		for e in [(1, 3, add), (1, 4, sub), (2, 3, mul), (2, 4, floordiv)]:
			CalcValBtn(self, e[0], e[1], CalcVal(e[2]))

		EvalBtn(self, 3, 3, 2)

	def addItem(self, val: CalcVal):
		if self.lastItem is None:
			self.lastItem = CalcItem(None, val)
		elif not self.lastItem.appendDigit(val):
			self.lastItem = CalcItem(self.lastItem, val)

	def print(self):
		currItem = self.lastItem

		while currItem is not None:
			print(currItem.val)
			currItem = currItem.prev

	def run(self):
		self.root.mainloop()

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
		self.priority = self.val.priority()

	def appendDigit(self, val: CalcVal) -> bool:
		return self.val.appendDigit(val)

@dataclass
class CalcVal:
	val: Union[int, Operator]

	def __str__(self):
		return str(self.val) if self.isInt() else opInfo[self.val].name

	def appendDigit(self, o: CalcVal) -> bool:
		if self.isInt() and o.isInt():
			self.val = self.val * 10 + o.val
			return True
		return False

	def isInt(self) -> bool:
		return isinstance(self.val, int)

	def priority(self) -> int:
		return 0 if self.isInt() else opInfo[self.val].priority

class CalcValBtn(Btn):
	def __init__(self, app: App, row: int, col: int, val: CalcVal,
		span: int = 1
	):
		super().__init__(app, row, col, span, str(val))
		self.val = val

	def onClick(self):
		self.app.addItem(self.val)

class EvalBtn(Btn):
	def __init__(self, app: App, row: int, col: int, span: int):
		super().__init__(app, row, col, span, "=")

	def onClick(self):
		self.app.print()

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

if __name__ == '__main__':
	App().run()
