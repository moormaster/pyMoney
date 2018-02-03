from lib import app

import unittest
import os


class MoneyDataTestCaseBase(unittest.TestCase):
	def setUp(self):
		self.app = app.PyMoney()

		self.categories_category1 = []
		self.categories_category2 = []
		self.categories_maxlevel_1 = []
		self.categories_all = []

		self.categories_all.append(self.app.moneydata.get_category("All"))
		self.categories_maxlevel_1.append(self.app.moneydata.get_category("All"))

		newcategories = []
		newcategories.append(self.app.moneydata.add_category("All", "Cash"))
		newcategories.append(self.app.moneydata.add_category("Cash", "In"))
		newcategories.append(self.app.moneydata.add_category("Cash", "Out"))
		newcategories.append(self.app.moneydata.add_category("All", "External"))
		newcategories.append(self.app.moneydata.add_category("External", "In"))
		self.categories_all.extend(newcategories)
		self.categories_maxlevel_1.append(newcategories[0])
		self.categories_maxlevel_1.append(newcategories[3])

		newcategories = []
		newcategories.append(self.app.moneydata.add_category("External.In", "Category1"))
		newcategories.append(self.app.moneydata.add_category("Category1", "Subcategory1"))
		self.categories_category1.extend(newcategories)
		self.categories_all.extend(newcategories)

		newcategories = []
		newcategories.append(self.app.moneydata.add_category("External.In", "Category2"))
		self.categories_category2.extend(newcategories)
		self.categories_all.extend(newcategories)

		newcategories = []
		newcategories.append(self.app.moneydata.add_category("External", "Out"))
		self.categories_all.extend(newcategories)

		self.transactions_year_2000 = []
		self.transactions_year_2000_month_jan = []
		self.transactions_year_2000_month_feb = []

		self.transactions_year_2001 = []
		self.transactions_year_2001_month_jan = []

		self.transactions_category_category1 = []
		self.transactions_category_category2 = []
		self.transactions_category_subcategory1 = []

		self.transactions_all = []

		newtransactions = []
		newtransactions.append(self.app.moneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", 10.0, "A comment"))
		newtransactions.append(self.app.moneydata.add_transaction("2000-01-02", "Cash.Out", "Subcategory1", 20.0, "A comment"))
		newtransactions.append(self.app.moneydata.add_transaction("2000-01-03", "Cash.Out", "Category2", 30.0, "A comment"))

		self.transactions_year_2000.extend(newtransactions)
		self.transactions_year_2000_month_jan.extend(newtransactions)
		self.transactions_category_category1.append(newtransactions[0])
		self.transactions_category_category1.append(newtransactions[1])
		self.transactions_category_subcategory1.append(newtransactions[1])
		self.transactions_category_category2.append(newtransactions[2])
		self.transactions_all.extend(newtransactions)

		newtransactions = []
		newtransactions.append(self.app.moneydata.add_transaction("2000-02-01", "Cash.Out", "Category1", 40.0, "A comment"))
		newtransactions.append(self.app.moneydata.add_transaction("2000-02-02", "Cash.Out", "Subcategory1", 50.0, "A comment"))
		newtransactions.append(self.app.moneydata.add_transaction("2000-02-03", "Cash.Out", "Category2", 60.0, "A comment"))

		self.transactions_year_2000.extend(newtransactions)
		self.transactions_year_2000_month_feb.extend(newtransactions)
		self.transactions_category_category1.append(newtransactions[0])
		self.transactions_category_category1.append(newtransactions[1])
		self.transactions_category_subcategory1.append(newtransactions[1])
		self.transactions_category_category2.append(newtransactions[2])
		self.transactions_all.extend(newtransactions)

		newtransactions = []
		newtransactions.append(self.app.moneydata.add_transaction("2001-01-01", "Cash.Out", "Category1", 70.0, "A comment"))
		newtransactions.append(self.app.moneydata.add_transaction("2001-01-02", "Cash.Out", "Subcategory1", 80.0, "A comment"))
		newtransactions.append(self.app.moneydata.add_transaction("2001-01-03", "Cash.Out", "Category2", 90.0, "A comment"))

		self.transactions_year_2001.extend(newtransactions)
		self.transactions_year_2001_month_jan.extend(newtransactions)
		self.transactions_category_category1.append(newtransactions[0])
		self.transactions_category_category1.append(newtransactions[1])
		self.transactions_category_subcategory1.append(newtransactions[1])
		self.transactions_category_category2.append(newtransactions[2])
		self.transactions_all.extend(newtransactions)

		newtransactions = []
		newtransactions.append(self.app.moneydata.add_transaction("2001-01-04", "Cash.Out", "UnknownCategory.UnknownSubCategory", 40.0, "A comment", True))

		self.transactions_year_2001.extend(newtransactions)
		self.transactions_year_2001_month_jan.extend(newtransactions)
		self.transactions_all.extend(newtransactions)

		self.categories_all.append(self.app.moneydata.get_category("NOTFOUND"))
		self.categories_maxlevel_1.append(self.app.moneydata.get_category("NOTFOUND"))
		self.categories_all.append(self.app.moneydata.get_category("UnknownCategory"))
		self.categories_all.append(self.app.moneydata.get_category("UnknownSubCategory"))


class TestPyMoney(MoneyDataTestCaseBase):
	def setUp(self):
		if os.access("pymoney.transactions", os.F_OK):
			os.remove("pymoney.transactions")
		if os.access("pymoney.categories", os.F_OK):
			os.remove("pymoney.categories")

		MoneyDataTestCaseBase.setUp(self)

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


class TestFilterFactory(MoneyDataTestCaseBase):
	def setUp(self):
		MoneyDataTestCaseBase.setUp(self)

		self.filterFactory = app.FilterFactory(self.app.moneydata)

	def test_create_and_date_transactionfilter_year(self):
		filter = self.filterFactory.create_and_date_transactionfilter("2000", None, None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter("<2001", None, None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter("<=2000", None, None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter(">2000", None, None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2001, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter(">=2001", None, None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2001, transactions)

	def test_create_and_date_transactionfilter_year_month(self):
		filter = self.filterFactory.create_and_date_transactionfilter("2000", "01", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000_month_jan, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter("<2000", "02", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000_month_jan, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter("<=2000", "01", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000_month_jan, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter(">2000", "01", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000_month_feb + self.transactions_year_2001, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter(">=2000", "02", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_year_2000_month_feb + self.transactions_year_2001, transactions)

	def test_create_and_date_transactionfilter_year_month_day(self):
		filter = self.filterFactory.create_and_date_transactionfilter("2000", "01", "01")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([self.transactions_year_2000_month_jan[0]], transactions)

		filter = self.filterFactory.create_and_date_transactionfilter("<2000", "01", "02")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([self.transactions_year_2000_month_jan[0]], transactions)

		filter = self.filterFactory.create_and_date_transactionfilter("<=2000", "01", "01")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([self.transactions_year_2000_month_jan[0]], transactions)

		filter = self.filterFactory.create_and_date_transactionfilter(">2000", "01", "01")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([self.transactions_year_2000_month_jan[1], self.transactions_year_2000_month_jan[2]] + self.transactions_year_2000_month_feb + self.transactions_year_2001, transactions)

		filter = self.filterFactory.create_and_date_transactionfilter(">=2000", "01", "02")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([self.transactions_year_2000_month_jan[1], self.transactions_year_2000_month_jan[2]] + self.transactions_year_2000_month_feb + self.transactions_year_2001, transactions)

	def test_create_and_category_transactionfilter(self):
		filter = self.filterFactory.create_and_category_transactionfilter("Cash.In", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([], transactions)

		filter = self.filterFactory.create_and_category_transactionfilter("Cash.Out", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_all, transactions)

		filter = self.filterFactory.create_and_category_transactionfilter(None, "Category1")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_category_category1, transactions)

		filter = self.filterFactory.create_and_category_transactionfilter("Cash.Out", "Category1")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_category_category1, transactions)

		filter = self.filterFactory.create_and_category_transactionfilter("Cash.In", "Category1")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([], transactions)

	def test_create_or_category_transactionfilter(self):
		filter = self.filterFactory.create_or_category_transactionfilter("Cash.In", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual([], transactions)

		filter = self.filterFactory.create_or_category_transactionfilter("Cash.Out", None)
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_all, transactions)

		filter = self.filterFactory.create_or_category_transactionfilter(None, "Category1")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_category_category1, transactions)

		filter = self.filterFactory.create_or_category_transactionfilter("Cash.Out", "Category1")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_all, transactions)

		filter = self.filterFactory.create_or_category_transactionfilter("Cash.In", "Category1")
		transactions = list(self.app.moneydata.filter_transactions(filter))
		self.assertEqual(self.transactions_category_category1, transactions)

	def test_create_maxlevel_categoryfilter(self):
		filter = self.filterFactory.create_maxlevel_categoryfilter(4)
		categories = list(self.app.moneydata.filter_categories(filter))
		self.assertEqual(self.categories_all, categories)

		filter = self.filterFactory.create_maxlevel_categoryfilter(1)
		categories = list(self.app.moneydata.filter_categories(filter))
		self.assertEqual(self.categories_maxlevel_1, categories)

	def test_create_subtree_categoryfilter(self):
		filter = self.filterFactory.create_subtree_categoryfilter("All")
		categories = list(self.app.moneydata.filter_categories(filter))
		self.assertEqual(self.categories_all, categories)

		filter = self.filterFactory.create_subtree_categoryfilter("Category1")
		categories = list(self.app.moneydata.filter_categories(filter))
		self.assertEqual(self.categories_category1, categories)

		filter = self.filterFactory.create_subtree_categoryfilter("Category2")
		categories = list(self.app.moneydata.filter_categories(filter))
		self.assertEqual(self.categories_category2, categories)


if __name__ == "__main__":
	unittest.main()
