from lib import app

import unittest
import os


class TestPyMoney(unittest.TestCase):
	def setUp(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

		self.app = app.PyMoney()

		self.app.moneydata.add_category("All", "Cash")
		self.app.moneydata.add_category("Cash", "In")
		self.app.moneydata.add_category("Cash", "Out")
		self.app.moneydata.add_category("All", "External")
		self.app.moneydata.add_category("External", "In")
		self.app.moneydata.add_category("External", "Out")
		self.app.moneydata.add_category("External.In", "Category1")
		self.app.moneydata.add_category("Category1", "Subcategory1")
		self.app.moneydata.add_category("External.In", "Category2")

		self.app.moneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", 10.0, "A comment")
		self.app.moneydata.add_transaction("2000-01-02", "Cash.Out", "Subcategory1", 20.0, "A comment")
		self.app.moneydata.add_transaction("2000-01-03", "Cash.Out", "Category2", 30.0, "A comment")

		self.app.moneydata.add_transaction("2000-01-04", "Cash.Out", "UnknownCategory.UnknownSubCategory", 40.0, "A comment", True)

	def tearDown(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

	def test_set_fileprefix(self):
		self.app.set_fileprefix("myprefix")

		self.assertEqual(self.app.fileprefix, "myprefix")

		self.assertEqual(self.app.filenames["transactions"], "myprefix.transactions")
		self.assertEqual(self.app.filenames["categories"], "myprefix.categories")

	def test_read(self):
		self.app.write()

		read_app = app.PyMoney()

		read_app.read()

		self.assertEqual(len(list(read_app.moneydata.categorytree)), len(list(self.app.moneydata.categorytree)))
		self.assertEqual(len(read_app.moneydata.transactions), len(self.app.moneydata.transactions))

		for originalcategory in self.app.moneydata.categorytree:
			category = read_app.moneydata.get_category(originalcategory.get_unique_name())

			self.assertIsNotNone(category)
			self.assertEqual(category.name, originalcategory.name)
			if category.parent is not None:
				self.assertEqual(category.parent.name, originalcategory.parent.name)
			else:
				self.assertEqual(category.parent, originalcategory.parent)

		for i in range(len(self.app.moneydata.transactions)):
			originaltransaction = self.app.moneydata.transactions[i]
			transaction = read_app.moneydata.transactions[i]

			self.assertEqual(transaction.date, originaltransaction.date)
			self.assertEqual(transaction.fromcategory.name, originaltransaction.fromcategory.name)
			self.assertEqual(transaction.tocategory.name, originaltransaction.tocategory.name)
			self.assertEqual(transaction.amount, originaltransaction.amount)
			self.assertEqual(transaction.comment, originaltransaction.comment)

	def test_write(self):
		self.assertFalse(os.access("pymoney.transactions", os.F_OK))
		self.assertFalse(os.access("pymoney.categories", os.F_OK))

		self.app.write(skipwritetransactions=True)

		self.assertFalse(os.access("pymoney.transactions", os.F_OK))
		self.assertTrue(os.access("pymoney.categories", os.F_OK))

		os.remove("pymoney.categories")

		self.app.write()

		self.assertTrue(os.access("pymoney.transactions", os.F_OK))
		self.assertTrue(os.access("pymoney.categories", os.F_OK))


if __name__ == "__main__":
	unittest.main()
