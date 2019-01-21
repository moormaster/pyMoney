# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
import pyMoney
from lib import app

import unittest
import os


class PymoneySafetyNet(unittest.TestCase):
        def setUp(self):
                self.fileprefix = "safetynet_run"

                self.outputfile = self.fileprefix + ".log"
                self.categoriesfile = self.fileprefix + ".categories"
                self.paymentplansfile = self.fileprefix + ".paymentplans"
                self.transactionsfile = self.fileprefix + ".transactions"
                self.versionfile = self.fileprefix + ".version"

                self.fileprefixcompare = "safetynet"

                self.outputfilecompare = self.fileprefixcompare + ".log"
                self.categoriesfilecompare = self.fileprefixcompare + ".categories"
                self.paymentplansfilecompare = self.fileprefixcompare + ".paymentplans"
                self.transactionsfilecompare = self.fileprefixcompare + ".transactions"
                self.versionfilecompare = self.fileprefixcompare + ".version"

                if os.access(self.outputfile, os.F_OK):
                        os.remove(self.outputfile)
                if os.access(self.categoriesfile, os.F_OK):
                        os.remove(self.categoriesfile)
                if os.access(self.paymentplansfile, os.F_OK):
                        os.remove(self.paymentplansfile)
                if os.access(self.transactionsfile, os.F_OK):
                        os.remove(self.transactionsfile)
                if os.access(self.versionfile, os.F_OK):
                        os.remove(self.versionfile)

                self.outputfilestream = open(self.outputfile, "w")
                self.execute()
                self.outputfilestream.close()

        def tearDown(self):
                if os.access(self.outputfile, os.F_OK):
                        os.remove(self.outputfile)
                if os.access(self.categoriesfile, os.F_OK):
                        os.remove(self.categoriesfile)
                if os.access(self.paymentplansfile, os.F_OK):
                        os.remove(self.paymentplansfile)
                if os.access(self.transactionsfile, os.F_OK):
                        os.remove(self.transactionsfile)
                if os.access(self.versionfile, os.F_OK):
                        os.remove(self.versionfile)

        def execute(self):
                self.pymoney(["category", "add", "All", "Equity"])
                self.pymoney(["category", "add", "Equity", "OpeningBalance"])
                self.pymoney(["category", "add", "All", "Assets"])
                self.pymoney(["category", "add", "Assets", "Cash"])
                self.pymoney(["category", "add", "Assets", "DayMoney"])
                self.pymoney(["category", "add", "Assets", "Giro"])
                self.pymoney(["category", "add", "All", "Income"])
                self.pymoney(["category", "add", "Income", "Wages"])
                self.pymoney(["category", "add", "Income", "Interests"])
                self.pymoney(["category", "add", "Income", "Misc"])
                self.pymoney(["category", "add", "All", "Expenses"])
                self.pymoney(["category", "add", "Expenses", "Frequent"])
                self.pymoney(["category", "add", "Frequent", "Rent"])
                self.pymoney(["category" ,"add", "Frequent", "Energy"])
                self.pymoney(["category" ,"add", "Frequent", "Internet"])
                self.pymoney(["category", "add", "Expenses", "OnDemand"])
                self.pymoney(["category", "add", "OnDemand", "Break"])
                self.pymoney(["category", "add", "Break", "Breakfast"])
                self.pymoney(["category", "add", "Break", "Lunch"])
                self.pymoney(["category", "add", "OnDemand", "Life"])
                self.pymoney(["category", "add", "OnDemand", "Clothes"])
                self.pymoney(["category", "add", "OnDemand", "Media"])
                self.pymoney(["category", "add", "OnDemand", "Misc"])
                self.pymoney(["category", "add", "All", "Liabilities"])

                self.pymoney(["category", "tree"])
                self.pymoney(["category", "tree", "--fullnamecategories"])
                self.pymoney(["category", "list"])
                self.pymoney(["category", "list", "--fullnamecategories"])

                self.pymoney(["paymentplan", "add", "Energy", "Monthly", "Giro", "Energy", "50"])
                self.pymoney(["paymentplan", "add", "Internet", "Monthly", "Giro", "Internet", "30"])
                self.pymoney(["paymentplan", "add", "Rent", "Monthly", "Giro", "Rent", "600"])
                self.pymoney(["paymentplan", "add", "Save", "Monthly", "Giro", "DayMoney", "500", "Monthly saving"])

                self.pymoney(["paymentplan", "list"])

                self.pymoney(["transaction", "add", "2000-01-01", "OpeningBalance", "Cash", "400.01"])
                self.pymoney(["transaction", "add", "2000-01-01", "OpeningBalance", "Giro", "3000"])
                self.pymoney(["transaction", "add", "2000-01-01", "OpeningBalance", "DayMoney", "10000"])

                self.pymoney(["transaction", "edit", "0", "2000-01-01", "OpeningBalance", "Cash", "400"])

                self.pymoney(["paymentplan", "execute", "Energy", "2000-01-03"])
                self.pymoney(["transaction", "add", "2000-01-03", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-03", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-04", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-04", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-05", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-05", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-06", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-06", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-07", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-07", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-10", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-10", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-11", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-11", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-12", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-12", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-13", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-13", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-14", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-14", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-17", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-17", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-18", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-18", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-19", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-19", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-20", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-20", "Cash", "Lunch", "8"])

                self.pymoney(["summary", "categories", "2000", "01", "--category", "Frequent", "--showempty"])
                self.pymoney(["summary", "categories", "2000", "01", "--paymentplangroup", "Monthly", "--category", "Expenses", "--showempty"])

                self.pymoney(["transaction", "add", "2000-01-21", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-21", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-24", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-24", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-25", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-25", "Cash", "Lunch", "8"])
                self.pymoney(["paymentplan", "execute", "Rent", "2000-01-25"])
                self.pymoney(["paymentplan", "execute", "Internet", "2000-01-25"])
                self.pymoney(["transaction", "add", "2000-01-26", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-26", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-27", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-27", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-28", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-28", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-28", "Wages", "Giro", "2000"])
                self.pymoney(["paymentplan", "execute", "Save", "2000-01-28"])
                self.pymoney(["transaction", "add", "2000-01-28", "Giro", "Cash", "400"])
                self.pymoney(["transaction", "add", "2000-01-31", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-01-31", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-01-31", "Income.Misc", "Cash", "10", "Found"])
                self.pymoney(["summary", "categories", "--category", "Assets"])

                self.pymoney(["category", "add", "Assets", "DayMoneyAccounts"])
                self.pymoney(["category", "move", "DayMoney", "DayMoneyAccounts"])
                self.pymoney(["category", "add", "DayMoneyAccounts", "OtherDayMoney"])
                self.pymoney(["paymentplan", "edit", "Save", "Monthly", "Giro", "OtherDayMoney", "500", "Monthly saving now happening to other account"])

                self.pymoney(["paymentplan", "execute", "Energy", "2000-02-01"])
                self.pymoney(["transaction", "add", "2000-02-01", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-01", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-02", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-02", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-03", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-03", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-04", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-04", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-07", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-07", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-08", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-08", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-09", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-09", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-10", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-10", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-11", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-11", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-14", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-14", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-15", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-15", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-16", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-16", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-17", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-17", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-18", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-18", "Cash", "Lunch", "8"])

                self.pymoney(["summary", "categories", "2000", "02", "--category", "Frequent", "--showempty"])
                self.pymoney(["summary", "categories", "2000", "02", "--paymentplangroup", "Monthly", "--category", "Expenses", "--showempty"])

                self.pymoney(["transaction", "add", "2000-02-21", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-21", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-22", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-22", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-23", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-23", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-24", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-24", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-25", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-25", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-25", "Giro", "Rent", "600", "Accidentally manually transferring money of payment plan"])
                self.pymoney(["paymentplan", "execute", "Internet", "2000-02-25"])
                self.pymoney(["transaction", "add", "2000-02-28", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-28", "Cash", "Lunch", "8"])
                self.pymoney(["transaction", "add", "2000-02-28", "Wages", "Giro", "2000"])
                self.pymoney(["paymentplan", "execute", "Save", "2000-01-28"])
                self.pymoney(["transaction", "add", "2000-02-28", "Giro", "Cash", "400"])
                self.pymoney(["transaction", "add", "2000-02-29", "Cash", "Breakfast", "2.00", "Bakery"])
                self.pymoney(["transaction", "add", "2000-02-29", "Cash", "Lunch", "8"])
                self.pymoney(["summary", "categories", "--category", "Assets"])

                self.pymoney(["summary", "categories", "2000", "01"])
                self.pymoney(["summary", "categories", "2000", "02"])

                self.pymoney(["summary", "categories", "2000", "01", "--maxlevel", "2"])
                self.pymoney(["summary", "categories", "2000", "01", "--cashflowcategory", "Rent"])

                self.pymoney(["summary", "categories", "2000", "01", "--paymentplangroup", "Monthly", "--category", "Expenses"])
                self.pymoney(["summary", "categories", "2000", "02", "--paymentplangroup", "Monthly", "--category", "Expenses"])

                self.pymoney(["summary", "monthly", "--balance", "Giro"])
                self.pymoney(["summary", "monthly", "--paymentplangroup", "Monthly", "Expenses"])
                self.pymoney(["summary", "monthly", "Expenses"])
                self.pymoney(["summary", "yearly", "Expenses"])

                self.pymoney(["transaction", "list", "2000", "01"])
                self.pymoney(["transaction", "list", "2000", "02"])
                self.pymoney(["transaction", "list", "<=2000", "02", "15"])
                self.pymoney(["transaction", "list", "<2000", "02", "16"])
                self.pymoney(["transaction", "list", ">=2000", "01", "15"])
                self.pymoney(["transaction", "list", ">2000", "01", "14"])

                self.pymoney(["transaction", "list", "--category", "Rent"])

                self.pymoney(["category", "delete", "Rent"])
                self.pymoney(["category", "tree"])
                self.pymoney(["category", "list"])
                self.pymoney(["transaction", "list"])

                self.pymoney(["category", "rename", "Income.Misc", "IncomingMisc"])
                self.pymoney(["category", "tree"])
                self.pymoney(["category", "list"])
                self.pymoney(["transaction", "list"])

                self.pymoney(["category", "move", "Break", "Life"])
                self.pymoney(["category", "tree"])
                self.pymoney(["category", "list"])
                self.pymoney(["transaction", "list"])

                self.pymoney(["category", "merge", "DayMoney", "Giro"])
                self.pymoney(["category", "tree"])
                self.pymoney(["category", "list"])
                self.pymoney(["transaction", "list"])

                self.pymoney(["transaction", "delete", "12"])
                self.pymoney(["transaction", "delete", "11"])
                self.pymoney(["transaction", "delete", "10"])
                self.pymoney(["transaction", "list"])

                self.pymoney(["export", "2000","01"])
                self.pymoney(["export"])

        def pymoney(self, argv):
                print("$ ./pyMoney.py " + " ".join(argv), file=self.outputfilestream)

                argv = ["--fileprefix", self.fileprefix] + argv
                pymoneyconsole = pyMoney.PyMoneyConsole(argv)
                pymoneyconsole.set_print_streams(self.outputfilestream, self.outputfilestream)
                pymoneyconsole.main()
                
                print("", file=self.outputfilestream)

        def assertFileEqual(self, expectedfile, actualfile, msg=None):
                f = open(expectedfile)
                expected = f.readlines()
                f.close()

                f = open(actualfile)
                actual = f.readlines()
                f.close()

                self.assertListEqual(expected, actual, msg)

        def test_compare_safetynet(self):
                self.assertFileEqual(self.outputfilecompare, self.outputfile, "output differs from " + self.outputfilecompare)
                self.assertFileEqual(self.categoriesfilecompare, self.categoriesfile, "output differs from " + self.categoriesfilecompare)
                self.assertFileEqual(self.paymentplansfilecompare, self.paymentplansfile, "output differs from " + self.paymentplansfilecompare)
                self.assertFileEqual(self.transactionsfilecompare, self.transactionsfile, "transactions file differs from " + self.transactionsfilecompare)
                self.assertFileEqual(self.versionfilecompare, self.versionfile, "output differs from " + self.versionfilecompare)


if __name__ == "__main__":
        unittest.main()
