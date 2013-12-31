import pyMoney
from lib import app

import unittest
import os


class PymoneyTestBase(unittest.TestCase):
	def setUp(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

		self.setUp_categories()
		self.setUp_transactions()

	def tearDown(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

	@staticmethod
	def pymoney_main(argv):
		pymoneyconsole = pyMoney.PyMoneyConsole(argv)
		pymoneyconsole.main()

	def setUp_categories(self):
		PymoneyTestBase.pymoney_main(["category", "add", "All", "Category1"])
		PymoneyTestBase.pymoney_main(["category", "add", "Category1", "Subcategory1"])
		PymoneyTestBase.pymoney_main(["category", "add", "All", "Category2"])

	def setUp_transactions(self):
		PymoneyTestBase.pymoney_main(["transaction", "add", "2000-01-01", "Category1", "10.0", "A comment"])
		PymoneyTestBase.pymoney_main(["transaction", "add", "2000-01-01", "Subcategory1", "20.0", "A comment"])
		PymoneyTestBase.pymoney_main(["transaction", "add", "2000-01-01", "Category2", "30.0", "A comment"])

	def get_app(self):
		read_app = app.PyMoney()
		read_app.read()

		return read_app


class TransactionsTest(PymoneyTestBase):
	def test_transaction_add(self):
		read_app = self.get_app()
		self.assertEqual(len(list(read_app.moneydata.categorytree)), 4)
		self.assertEqual(len(read_app.moneydata.transactions), 3)

	def test_transaction_delete(self):
		PymoneyTestBase.pymoney_main(["transaction", "delete", "2"])

		read_app = self.get_app()
		filter_func = lambda t: t.category.name == "Category2"
		self.assertEqual(len(list(read_app.moneydata.filter_transactions(filter_func))), 0)
		self.assertEqual(len(read_app.moneydata.transactions), 2)

	def test_transaction_list(self):
		PymoneyTestBase.pymoney_main(["transaction", "list"])
		PymoneyTestBase.pymoney_main(["transaction", "list", "2000"])
		PymoneyTestBase.pymoney_main(["transaction", "list", "2000", "01"])
		PymoneyTestBase.pymoney_main(["transaction", "list", "2000", "01"])
		PymoneyTestBase.pymoney_main(["transaction", "list", "2000", "01", "--category=Category1"])
		PymoneyTestBase.pymoney_main(["transaction", "--fullnamecategories", "list", "2000", "01"])


class CategoriesTest(PymoneyTestBase):
	def test_category_add(self):
		PymoneyTestBase.pymoney_main(["category", "add", "All", "NewCategory"])

		read_app = self.get_app()
		self.assertEqual(len(list(read_app.moneydata.categorytree)), 5)

		category = read_app.moneydata.categorytree.find_first_node("NewCategory")
		self.assertIsNotNone(category)
		self.assertEqual(category.name, "NewCategory")
		self.assertEqual(category.parent.name, "All")

	def test_category_delete(self):
		PymoneyTestBase.pymoney_main(["category", "delete", "Category1"])

		read_app = self.get_app()

		notfoundcategory = read_app.moneydata.get_notfound_category()
		self.assertIsNotNone(notfoundcategory)
		self.assertTrue("Category1" in notfoundcategory.children)

		PymoneyTestBase.pymoney_main(["transaction", "delete", "1"])
		PymoneyTestBase.pymoney_main(["transaction", "delete", "0"])

		read_app = self.get_app()

		self.assertEqual(len(list(read_app.moneydata.categorytree)), 2)
		category = read_app.moneydata.categorytree.find_first_node("Category1")
		self.assertIsNone(category)

	def test_category_merge(self):
		PymoneyTestBase.pymoney_main(["category", "merge", "Category1", "Category2"])

		read_app = self.get_app()
		self.assertEqual(len(list(read_app.moneydata.categorytree)), 3)

		category1 = read_app.moneydata.categorytree.find_first_node("Category1")
		category2 = read_app.moneydata.categorytree.find_first_node("Category2")
		subcategory1 = read_app.moneydata.categorytree.find_first_node("Subcategory1")

		filter_func = lambda t: t.category.is_contained_in_subtree(category2)
		self.assertEqual(len(list(read_app.moneydata.filter_transactions(filter_func))), 3)

		filter_func = lambda t: t.category.is_contained_in_subtree(subcategory1)
		self.assertEqual(len(list(read_app.moneydata.filter_transactions(filter_func))), 1)

		self.assertIsNone(category1)
		self.assertIsNotNone(category2)
		self.assertIsNotNone(subcategory1)

		self.assertEqual(category2.parent.name, "All")
		self.assertEqual(subcategory1.parent.name, "Category2")

	def test_category_move(self):
		PymoneyTestBase.pymoney_main(["category", "move", "Subcategory1", "Category2"])

		read_app = self.get_app()
		category1 = read_app.moneydata.categorytree.find_first_node("Category1")
		subcategory1 = read_app.moneydata.categorytree.find_first_node("Subcategory1")

		self.assertEqual(subcategory1.parent.name, "Category2")
		self.assertEqual(len(category1.children), 0)

	def test_category_rename(self):
		PymoneyTestBase.pymoney_main(["category", "rename", "Category1", "RenamedCategory"])

		read_add = self.get_app()
		category1 = read_add.moneydata.categorytree.find_first_node("Category1")
		renamedcategory = read_add.moneydata.categorytree.find_first_node("RenamedCategory")

		self.assertIsNone(category1)
		self.assertIsNotNone(renamedcategory)
		self.assertEqual(renamedcategory.name, "RenamedCategory")
		self.assertEqual(renamedcategory.parent.name, "All")

	def test_category_list(self):
		PymoneyTestBase.pymoney_main(["category", "list"])

	def test_category_listnames(self):
		PymoneyTestBase.pymoney_main(["category", "listnames"])


class SummaryTest(PymoneyTestBase):
	def test_summary_categories(self):
		PymoneyTestBase.pymoney_main(["summary", "categories"])
		PymoneyTestBase.pymoney_main(["summary", "categories", "2000"])
		PymoneyTestBase.pymoney_main(["summary", "categories", "2000", "01"])

	def test_summary_monthly(self):
		PymoneyTestBase.pymoney_main(["summary", "monthly", "Category1"])


if __name__ == "__main__":
	unittest.main()