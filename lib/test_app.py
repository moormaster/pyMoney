# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib import app

import unittest
import os


class TestFilterFactory(unittest.TestCase):
        def setUp(self):
                self.app = app.PyMoney()

                self.categories_category1 = []
                self.categories_category2 = []
                self.categories_maxlevel_1 = []
                self.categories_all = []

                self.categories_all.append(self.app.moneydata.get_category("All"))
                self.categories_maxlevel_1.append(self.app.moneydata.get_category("All"))

                newcategories = [self.app.moneydata.add_category("All", "Cash"),
                                                 self.app.moneydata.add_category("Cash", "In"),
                                                 self.app.moneydata.add_category("Cash", "Out"),
                                                 self.app.moneydata.add_category("All", "External"),
                                                 self.app.moneydata.add_category("External", "In")]
                self.categories_all.extend(newcategories)
                self.categories_maxlevel_1.append(newcategories[0])
                self.categories_maxlevel_1.append(newcategories[3])

                newcategories = [self.app.moneydata.add_category("External.In", "Category1"),
                                                 self.app.moneydata.add_category("Category1", "Subcategory1")]
                self.categories_category1.extend(newcategories)
                self.categories_all.extend(newcategories)

                newcategories = [self.app.moneydata.add_category("External.In", "Category2")]
                self.categories_category2.extend(newcategories)
                self.categories_all.extend(newcategories)

                newcategories = [self.app.moneydata.add_category("External", "Out")]
                self.categories_all.extend(newcategories)

                self.transactions_year_2000 = []
                self.transactions_year_2000_month_jan = []
                self.transactions_year_2000_month_feb = []

                self.transactions_year_2001 = []
                self.transactions_year_2001_month_jan = []
                self.transactions_year_2001_month_feb = []

                self.transactions_category_category1 = []
                self.transactions_category_category2 = []
                self.transactions_category_subcategory1 = []

                self.transactions_all = []

                newtransactions = [self.app.moneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", 10.0, "A comment"),
                                                   self.app.moneydata.add_transaction("2000-01-02", "Cash.Out", "Subcategory1", 20.0,
                                                           "A comment"),
                                                   self.app.moneydata.add_transaction("2000-01-03", "Cash.Out", "Category2", 30.0, "A comment")]

                self.transactions_year_2000.extend(newtransactions)
                self.transactions_year_2000_month_jan.extend(newtransactions)
                self.transactions_category_category1.append(newtransactions[0])
                self.transactions_category_category1.append(newtransactions[1])
                self.transactions_category_subcategory1.append(newtransactions[1])
                self.transactions_category_category2.append(newtransactions[2])
                self.transactions_all.extend(newtransactions)

                newtransactions = [self.app.moneydata.add_transaction("2000-02-01", "Cash.Out", "Category1", 40.0, "A comment"),
                                                   self.app.moneydata.add_transaction("2000-02-02", "Cash.Out", "Subcategory1", 50.0,
                                                           "A comment"),
                                                   self.app.moneydata.add_transaction("2000-02-03", "Cash.Out", "Category2", 60.0, "A comment")]

                self.transactions_year_2000.extend(newtransactions)
                self.transactions_year_2000_month_feb.extend(newtransactions)
                self.transactions_category_category1.append(newtransactions[0])
                self.transactions_category_category1.append(newtransactions[1])
                self.transactions_category_subcategory1.append(newtransactions[1])
                self.transactions_category_category2.append(newtransactions[2])
                self.transactions_all.extend(newtransactions)

                newtransactions = [self.app.moneydata.add_transaction("2001-01-01", "Cash.Out", "Category1", 70.0, "A comment"),
                                                   self.app.moneydata.add_transaction("2001-01-02", "Cash.Out", "Subcategory1", 80.0,
                                                           "A comment"),
                                                   self.app.moneydata.add_transaction("2001-01-03", "Cash.Out", "Category2", 90.0, "A comment")]

                self.transactions_year_2001.extend(newtransactions)
                self.transactions_year_2001_month_jan.extend(newtransactions)
                self.transactions_category_category1.append(newtransactions[0])
                self.transactions_category_category1.append(newtransactions[1])
                self.transactions_category_subcategory1.append(newtransactions[1])
                self.transactions_category_category2.append(newtransactions[2])
                self.transactions_all.extend(newtransactions)

                newtransactions = [self.app.moneydata.add_transaction("2001-02-01", "Cash.Out", "Category1", 70.0, "A comment"),
                                                   self.app.moneydata.add_transaction("2001-02-02", "Cash.Out", "Subcategory1", 80.0,
                                                           "A comment"),
                                                   self.app.moneydata.add_transaction("2001-02-03", "Cash.Out", "Category2", 90.0, "A comment")]

                self.transactions_year_2001.extend(newtransactions)
                self.transactions_year_2001_month_feb.extend(newtransactions)
                self.transactions_category_category1.append(newtransactions[0])
                self.transactions_category_category1.append(newtransactions[1])
                self.transactions_category_subcategory1.append(newtransactions[1])
                self.transactions_category_category2.append(newtransactions[2])
                self.transactions_all.extend(newtransactions)

                newtransactions = [
                        self.app.moneydata.add_transaction("2001-02-04", "Cash.Out", "UnknownCategory.UnknownSubCategory", 40.0,
                                "A comment", True)]

                self.transactions_year_2001.extend(newtransactions)
                self.transactions_year_2001_month_feb.extend(newtransactions)
                self.transactions_all.extend(newtransactions)

                self.categories_all.append(self.app.moneydata.get_category("NOTFOUND"))
                self.categories_maxlevel_1.append(self.app.moneydata.get_category("NOTFOUND"))
                self.categories_all.append(self.app.moneydata.get_category("UnknownCategory"))
                self.categories_all.append(self.app.moneydata.get_category("UnknownSubCategory"))

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
                filter = self.filterFactory.create_and_date_transactionfilter("2001", "01", None)
                transactions = list(self.app.moneydata.filter_transactions(filter))
                self.assertEqual(self.transactions_year_2001_month_jan, transactions)

                filter = self.filterFactory.create_and_date_transactionfilter("<2001", "02", None)
                transactions = list(self.app.moneydata.filter_transactions(filter))
                self.assertEqual(self.transactions_year_2000 + self.transactions_year_2001_month_jan, transactions)

                filter = self.filterFactory.create_and_date_transactionfilter("<=2001", "01", None)
                transactions = list(self.app.moneydata.filter_transactions(filter))
                self.assertEqual(self.transactions_year_2000 + self.transactions_year_2001_month_jan, transactions)

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
                self.assertEqual([self.transactions_year_2000_month_jan[1], self.transactions_year_2000_month_jan[
                        2]] + self.transactions_year_2000_month_feb + self.transactions_year_2001, transactions)

                filter = self.filterFactory.create_and_date_transactionfilter(">=2000", "01", "02")
                transactions = list(self.app.moneydata.filter_transactions(filter))
                self.assertEqual([self.transactions_year_2000_month_jan[1], self.transactions_year_2000_month_jan[
                        2]] + self.transactions_year_2000_month_feb + self.transactions_year_2001, transactions)

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
                self.assertSetEqual(set(self.categories_all), set(categories))

                filter = self.filterFactory.create_maxlevel_categoryfilter(1)
                categories = list(self.app.moneydata.filter_categories(filter))
                self.assertSetEqual(set(self.categories_maxlevel_1), set(categories))

        def test_create_subtree_categoryfilter(self):
                filter = self.filterFactory.create_subtree_categoryfilter("All")
                categories = list(self.app.moneydata.filter_categories(filter))
                self.assertSetEqual(set(self.categories_all), set(categories))

                filter = self.filterFactory.create_subtree_categoryfilter("Category1")
                categories = list(self.app.moneydata.filter_categories(filter))
                self.assertSetEqual(set(self.categories_category1), set(categories))

                filter = self.filterFactory.create_subtree_categoryfilter("Category2")
                categories = list(self.app.moneydata.filter_categories(filter))
                self.assertSetEqual(set(self.categories_category2), set(categories))


if __name__ == "__main__":
        unittest.main()
