import lib.data
import lib.data.moneydata
import lib.io
import lib.io.parser
import lib.io.Categories
import lib.io.Transactions

import os


class CategoryNameFormatter:
	STRATEGY_NAME = 0
	STRATEGY_UNIQUE_NAME = 1
	STRATEGY_FULL_NAME = 2

	def __init__(self):
		self.d_namecache = {}
		self.strategy = self.STRATEGY_UNIQUE_NAME
		self.maxLength = None
		self.indentWithTreeLevel = False

		pass


	def set_strategy(self, strategy):
		if not strategy in [self.STRATEGY_NAME, self.STRATEGY_UNIQUE_NAME, self.STRATEGY_FULL_NAME]:
			raise "invalid strategy: " + str(strategy)

		if self.strategy != strategy:
			self.d_namecache = {}

		self.strategy = strategy


	def set_indent_with_tree_level(self, flag):
		if not flag:
			self.indentWithTreeLevel = False
		else:
			self.indentWithTreeLevel = True


	def set_maxlength(self, length):
		assert isinstance(length, int)

		if not length:
			self.maxLength = None
		else:
			self.maxLength = length


	def get_trimmed_value(self, string):
		if not self.maxLength:
			return string

		if len(string) < self.maxLength:
			return string

		return string[0:self.maxLength-4] + "..." + string[-1]


	def format(self, category):
		assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

		if not id(category) in self.d_namecache:
			if self.strategy == self.STRATEGY_NAME:
				self.d_namecache[id(category)] = category.name
			elif self.strategy == self.STRATEGY_UNIQUE_NAME:
				self.d_namecache[id(category)] = category.get_unique_name()
			else:
				self.d_namecache[id(category)] = category.get_full_name()

		formattedvalue = self.d_namecache[id(category)]
		if self.indentWithTreeLevel:
			formattedvalue = "  "*category.get_depth() + formattedvalue
		formattedvalue = self.get_trimmed_value(formattedvalue)

		return formattedvalue


class PyMoney:
	def __init__(self, fileprefix="pymoney"):
		self.fileprefix = ""
		self.filenames = []

		self.set_fileprefix(fileprefix)

		self.moneydata = lib.data.moneydata.MoneyData()

	def set_fileprefix(self, fileprefix):
		self.fileprefix = fileprefix

		self.filenames = {
			"transactions": self.fileprefix + ".transactions",
			"categories": self.fileprefix + ".categories"
		}

	def read(self):
		moneydata = lib.data.moneydata.MoneyData()

		if os.access(self.filenames["categories"], os.F_OK):
			moneydata.categorytree = lib.io.Categories.read(self.filenames["categories"])

		if os.access(self.filenames["transactions"], os.F_OK):
			transactionparser = lib.io.parser.TransactionParser(moneydata.categorytree, moneydata.notfoundcategoryname)
			moneydata.transactions = lib.io.Transactions.read(self.filenames["transactions"], transactionparser)

		self.moneydata = moneydata

	def write(self, skipwritetransactions=False):
		lib.io.Categories.write(self.filenames["categories"], self.moneydata.categorytree, self.moneydata.get_notfound_category())

		if not skipwritetransactions:
			lib.io.Transactions.write(self.filenames["transactions"], self.moneydata.transactions, self.moneydata.get_notfound_category())
