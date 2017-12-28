from lib import data
from lib import io

import os
import unittest


class MoneyDataFactory:
	def __init__(self):
		return

	@staticmethod
	def create():
		moneydata = data.moneydata.MoneyData()

		moneydata.add_category("All", "Cash")
		moneydata.add_category("Cash", "In")
		moneydata.add_category("Cash", "Out")
		moneydata.add_category("All", "External")
		moneydata.add_category("External", "In")
		moneydata.add_category("External", "Out")

		moneydata.add_category("External.Out", "Wages")
		moneydata.add_category("External.In", "Rent")
		moneydata.add_category("External.In", "AnotherCategory")

		return moneydata


class TestTransactions(unittest.TestCase):
	def setUp(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")

		self.moneydata = MoneyDataFactory.create()

		self.moneydata.add_transaction("2000-01-01", "Wages", "Cash.In", "1000.0", "Wages")
		self.moneydata.add_transaction("2000-01-02", "Cash.Out", "Rent", "400.0", "My appartment")
		self.moneydata.add_transaction("2000-01-03", "Cash.Out" ,"AnotherCategory", "100.0", "A comment")

	def tearDown(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")

	def test_read(self):
		io.Transactions.write("pymoney.transactions", self.moneydata.transactions, self.moneydata.get_notfound_category(), False)

		categorycount = len(list(self.moneydata.categorytree))
		self.moneydata.delete_category("AnotherCategory")

		self.assertEqual(categorycount-1, len(list(self.moneydata.categorytree)))

		transactionparser = io.parser.TransactionParser(self.moneydata.categorytree, self.moneydata.notfoundcategoryname)
		t = io.Transactions.read("pymoney.transactions", transactionparser)

		foreigncategory = self.moneydata.get_category("AnotherCategory")
		self.assertTrue(foreigncategory is not None)
		self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(foreigncategory))

		# NOTFOUND base category shall be appeared
		self.assertEqual(categorycount+1, len(list(self.moneydata.categorytree)))

		self.assertEqual(len(t), len(self.moneydata.transactions))

		for i in range(len(self.moneydata.transactions)):
			self.assertEqual(t[i].date, self.moneydata.transactions[i].date)
			self.assertEqual(t[i].fromcategory.name, self.moneydata.transactions[i].fromcategory.name)
			self.assertEqual(t[i].tocategory.name, self.moneydata.transactions[i].tocategory.name)
			self.assertEqual(t[i].amount, self.moneydata.transactions[i].amount)
			self.assertEqual(t[i].comment, self.moneydata.transactions[i].comment)

	def test_write(self):
		# nothing to test here
		return


class TestCategories(unittest.TestCase):
	def setUp(self):
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

		self.moneydata = MoneyDataFactory.create()

	def tearDown(self):
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

	def test_read(self):
		io.Categories.write("pymoney.categories", self.moneydata.categorytree, self.moneydata.get_notfound_category())

		c = io.Categories.read("pymoney.categories")

		self.assertEqual(len(list(c)), len(list(self.moneydata.categorytree)))

		for originalnode in self.moneydata.categorytree:
			node = c.find_first_node_by_relative_path(originalnode.get_unique_name())

			self.assertTrue(originalnode is not None)
			self.assertEqual(node.name, originalnode.name)

			if node.parent:
				self.assertEqual(node.parent.name, originalnode.parent.name)
			else:
				self.assertEqual(node.parent, originalnode.parent)

	def test_write(self):
		# nothing to test here
		return


if __name__ == "__main__":
	unittest.main()