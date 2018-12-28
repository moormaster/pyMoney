# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import moneydata
from lib.io import serialization

import unittest
import os


class TestMoneyDataSerialization(unittest.TestCase):
        def setUp(self):
                if os.access("pymoney.transactions", os.F_OK):
                        os.remove("pymoney.transactions")
                if os.access("pymoney.categories", os.F_OK):
                        os.remove("pymoney.categories")

                self.serialization = serialization.MoneyDataSerialization()

        def tearDown(self):
                if os.access("pymoney.transactions", os.F_OK):
                        os.remove("pymoney.transactions")
                if os.access("pymoney.categories", os.F_OK):
                        os.remove("pymoney.categories")

        def test_set_fileprefix(self):
                self.serialization.set_fileprefix("myprefix")

                self.assertEqual(self.serialization.fileprefix, "myprefix")

                self.assertEqual(self.serialization.filenames["transactions"], "myprefix.transactions")
                self.assertEqual(self.serialization.filenames["categories"], "myprefix.categories")

        def test_read(self):
                originalmoneydata = moneydata.MoneyData()

                originalmoneydata.add_category("All", "Cash")
                originalmoneydata.add_category("Cash", "In")
                originalmoneydata.add_category("Cash", "Out")
                originalmoneydata.add_category("All", "External")
                originalmoneydata.add_category("External", "In")

                originalmoneydata.add_category("External.In", "Category1")
                originalmoneydata.add_category("Category1", "Subcategory1")
                originalmoneydata.add_category("External.In", "Category2")
                originalmoneydata.add_category("External", "Out")

                originalmoneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", 10.0, "A comment")
                originalmoneydata.add_transaction("2000-01-02", "Cash.Out", "Subcategory1", 20.0,
                                                        "A comment")
                originalmoneydata.add_transaction("2000-01-03", "Cash.Out", "Category2", 30.0, "A comment")
                originalmoneydata.add_transaction("2000-02-01", "Cash.Out", "Category1", 40.0, "A comment")
                originalmoneydata.add_transaction("2000-02-02", "Cash.Out", "Subcategory1", 50.0,
                                                        "A comment")
                originalmoneydata.add_transaction("2000-02-03", "Cash.Out", "Category2", 60.0, "A comment")

                originalmoneydata.add_transaction("2001-01-01", "Cash.Out", "Category1", 70.0, "A comment")
                originalmoneydata.add_transaction("2001-01-02", "Cash.Out", "Subcategory1", 80.0,
                                                        "A comment")
                originalmoneydata.add_transaction("2001-01-03", "Cash.Out", "Category2", 90.0, "A comment")

                originalmoneydata.add_transaction("2001-02-01", "Cash.Out", "Category1", 70.0, "A comment")
                originalmoneydata.add_transaction("2001-02-02", "Cash.Out", "Subcategory1", 80.0,
                                                        "A comment")
                originalmoneydata.add_transaction("2001-02-03", "Cash.Out", "Category2", 90.0, "A comment")

                originalmoneydata.add_transaction("2001-02-04", "Cash.Out", "UnknownCategory.UnknownSubCategory", 40.0,
                                                        "A comment", True)

                self.serialization.write(originalmoneydata)

                read_serialization = serialization.MoneyDataSerialization()

                readmoneydata = read_serialization.read()

                self.assertEqual(len(list(readmoneydata.categorytree)), len(list(originalmoneydata.categorytree)))
                self.assertEqual(len(readmoneydata.transactions), len(originalmoneydata.transactions))

                for originalcategory in originalmoneydata.categorytree:
                        category = readmoneydata.get_category(originalcategory.get_unique_name())

                        self.assertIsNotNone(category)
                        self.assertEqual(category.name, originalcategory.name)
                        if category.parent is not None:
                                self.assertEqual(category.parent.name, originalcategory.parent.name)
                        else:
                                self.assertEqual(category.parent, originalcategory.parent)

                for i in range(len(originalmoneydata.transactions)):
                        originaltransaction = originalmoneydata.transactions[i]
                        transaction = readmoneydata.transactions[i]

                        self.assertEqual(transaction.date, originaltransaction.date)
                        self.assertEqual(transaction.fromcategory.name, originaltransaction.fromcategory.name)
                        self.assertEqual(transaction.tocategory.name, originaltransaction.tocategory.name)
                        self.assertEqual(transaction.amount, originaltransaction.amount)
                        self.assertEqual(transaction.comment, originaltransaction.comment)

        def test_read_v1_3(self):
                read_serialization = serialization.MoneyDataSerialization("pymoney_v1_3")
                readmoneydata = read_serialization.read()

                self.assertGreater(len(list(readmoneydata.categorytree.__iter__())), 1)
                self.assertGreater(len(readmoneydata.transactions), 0)

        def test_write_without_transactions_should_write_categories_only(self):
                originalmoneydata = moneydata.MoneyData()

                self.assertFalse(os.access("pymoney.transactions", os.F_OK))
                self.assertFalse(os.access("pymoney.categories", os.F_OK))

                self.serialization.write(originalmoneydata, skipwritetransactions=True)

                self.assertFalse(os.access("pymoney.transactions", os.F_OK))
                self.assertTrue(os.access("pymoney.categories", os.F_OK))

        def test_write_should_write_moneydata_to_files(self):
                originalmoneydata = moneydata.MoneyData()

                self.serialization.write(originalmoneydata)

                self.assertTrue(os.access("pymoney.transactions", os.F_OK))
                self.assertTrue(os.access("pymoney.categories", os.F_OK))

