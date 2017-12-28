import lib.data
import lib.data.moneydata
import lib.io
import lib.io.parser
import lib.io.Categories
import lib.io.Transactions

import os


class CategoryNameFormatter:
	def __init__(self):
		self.d_namecache = {}
		self.isFullName = False

		pass

	def set_fullname(self, flag):
		if (not not flag) != self.isFullName:
			self.d_namecache = {}

		if not flag:
			self.isFullName = False
		else:
			self.isFullName = True

	def format(self, category):
		assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

		if not id(category) in self.d_namecache:
			if self.isFullName:
				self.d_namecache[id(category)] = category.get_full_name()
			else:
				self.d_namecache[id(category)] = category.get_unique_name()

		return self.d_namecache[id(category)]


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
