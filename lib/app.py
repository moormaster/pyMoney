from . import data
import lib.io
import os


class PyMoney:
	def __init__(self, fileprefix="pymoney"):
		self.fileprefix = ""
		self.filenames = []

		self.set_fileprefix(fileprefix)

		self.moneydata = data.MoneyData()

	def set_fileprefix(self, fileprefix):
		self.fileprefix = fileprefix

		self.filenames = {
			"transactions": self.fileprefix + ".transactions",
			"categories": self.fileprefix + ".categories"
		}

	def read(self):
		moneydata = data.MoneyData()

		if os.access(self.filenames["categories"], os.F_OK):
			moneydata.categorytree = lib.io.Categories.read(self.filenames["categories"])

		if os.access(self.filenames["transactions"], os.F_OK):
			transactionparser = lib.io.TransactionParser(moneydata)
			moneydata.transactions = lib.io.Transactions.read(self.filenames["transactions"], transactionparser)

		self.moneydata = moneydata

	def write(self, skipwritetransactions=False):
		lib.io.Categories.write(self.filenames["categories"], self.moneydata.categorytree, self.moneydata.get_notfound_category())

		if not skipwritetransactions:
			lib.io.Transactions.write(self.filenames["transactions"], self.moneydata.transactions)
