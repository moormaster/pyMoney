# vim: expandtab softtabstop=0 list listchars=tab\:>-:
import lib.data
import lib.data.filterchain
import lib.data.moneydata
import lib.io
import lib.io.parser
import lib.io.Categories
import lib.io.Transactions

import os


class PyMoney:
        def __init__(self, fileprefix="pymoney"):
                self.fileprefix = ""
                self.filenames = {}

                self.set_fileprefix(fileprefix)

                self.moneydata = lib.data.moneydata.MoneyData()
                self.filterFactory = FilterFactory(self.moneydata)

        def set_fileprefix(self, fileprefix):
                self.fileprefix = fileprefix

                self.filenames = {
                        "transactions": self.fileprefix + ".transactions",
                        "categories": self.fileprefix + ".categories"
                }

        def get_moneydata(self):
                return self.moneydata

        def read(self):
                moneydata = lib.data.moneydata.MoneyData()

                if os.access(self.filenames["categories"], os.F_OK):
                        moneydata.categorytree = lib.io.Categories.read(self.filenames["categories"])

                if os.access(self.filenames["transactions"], os.F_OK):
                        transactionparser = lib.io.parser.TransactionParser(moneydata.categorytree, moneydata.notfoundcategoryname)
                        transactions = lib.io.Transactions.read(self.filenames["transactions"], transactionparser)
                        for t in transactions:
                                moneydata.import_transaction(t)

                self.moneydata = moneydata
                self.filterFactory.set_moneydata(moneydata)

        def write(self, skipwritetransactions=False):
                lib.io.Categories.write(self.filenames["categories"], self.moneydata.categorytree,
                        self.moneydata.get_notfound_category())

                if not skipwritetransactions:
                        lib.io.Transactions.write(self.filenames["transactions"], self.moneydata.transactions,
                                self.moneydata.get_notfound_category())


class FilterFactory:
        def __init__(self, moneydata):
                assert isinstance(moneydata, lib.data.moneydata.MoneyData)
                self.moneydata = moneydata

        def set_moneydata(self, moneydata):
                assert isinstance(moneydata, lib.data.moneydata.MoneyData)
                self.moneydata = moneydata

        def create_and_date_transactionfilter(self, filter_year, filter_month, filter_day):
                transactionfilter = lib.data.filterchain.Filter(lambda t: True)

                greater_or_equal = False
                greater = False
                equal = True
                lower = False
                lower_or_equal = False

                if filter_year:
                        equal = False

                        if filter_year[0:2] == ">=":
                                year = int(filter_year[2:])
                                greater_or_equal = True
                        elif filter_year[0:2] == "<=":
                                year = int(filter_year[2:])
                                lower_or_equal = True
                        elif filter_year[0:1] == ">":
                                year = int(filter_year[1:])
                                greater = True
                        elif filter_year[0:1] == "<":
                                year = int(filter_year[1:])
                                lower = True
                        else:
                                equal = True

                        if greater_or_equal:
                                year = int(filter_year[2:])
                                transactionfilter = transactionfilter.and_concat(lambda t: t.date.year >= year)
                        if lower_or_equal:
                                year = int(filter_year[2:])
                                transactionfilter = transactionfilter.and_concat(lambda t: t.date.year <= year)
                        if greater:
                                year = int(filter_year[1:])
                                if filter_month or filter_day:
                                        transactionfilter = transactionfilter.and_concat(lambda t: t.date.year >= year)
                                else:
                                        transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year)
                        if lower:
                                year = int(filter_year[1:])
                                if filter_month or filter_day:
                                        transactionfilter = transactionfilter.and_concat(lambda t: t.date.year <= year)
                                else:
                                        transactionfilter = transactionfilter.and_concat(lambda t: t.date.year < year)
                        if equal:
                                year = int(filter_year)
                                transactionfilter = transactionfilter.and_concat(lambda t: t.date.year == year)

                if filter_month:
                        month = int(filter_month)

                        if greater_or_equal:
                                transactionfilter = transactionfilter.and_concat(
                                        lambda t: t.date.year > year or t.date.year == year and t.date.month >= month)
                        if lower_or_equal:
                                transactionfilter = transactionfilter.and_concat(
                                        lambda t: t.date.year < year or t.date.year == year and t.date.month <= month)
                        if greater:
                                if filter_day:
                                        transactionfilter = transactionfilter.and_concat(
                                                lambda t: t.date.year > year or t.date.year == year and t.date.month >= month)
                                else:
                                        transactionfilter = transactionfilter.and_concat(
                                                lambda t: t.date.year > year or t.date.year == year and t.date.month > month)
                        if lower:
                                if filter_day:
                                        transactionfilter = transactionfilter.and_concat(
                                                lambda t: t.date.year < year or t.date.year == year and t.date.month <= month)
                                else:
                                        transactionfilter = transactionfilter.and_concat(
                                                lambda t: t.date.year < year or t.date.year == year and t.date.month < month)
                        if equal:
                                transactionfilter = transactionfilter.and_concat(lambda t: t.date.month == month)

                if filter_day:
                        day = int(filter_day)

                        if greater_or_equal:
                                transactionfilter = transactionfilter.and_concat(lambda
                                                t: t.date.year > year or t.date.year == year and t.date.month > month or t.date.year == year and t.date.month == month and t.date.day >= day)
                        if lower_or_equal:
                                transactionfilter = transactionfilter.and_concat(lambda
                                                t: t.date.year < year or t.date.year == year and t.date.month < month or t.date.year == year and t.date.month == month and t.date.day <= day)
                        if greater:
                                transactionfilter = transactionfilter.and_concat(lambda
                                                t: t.date.year > year or t.date.year == year and t.date.month > month or t.date.year == year and t.date.month == month and t.date.day > day)
                        if lower:
                                transactionfilter = transactionfilter.and_concat(lambda
                                                t: t.date.year < year or t.date.year == year and t.date.month < month or t.date.year == year and t.date.month == month and t.date.day < day)
                        if equal:
                                transactionfilter = transactionfilter.and_concat(lambda t: t.date.day == day)

                return transactionfilter

        def create_or_category_transactionfilter(self, filter_from_category, filter_to_category):
                transactionfilter = lib.data.filterchain.Filter(lambda t: False)

                if filter_from_category:
                        fromcategory = self.moneydata.get_category(filter_from_category)

                        if not fromcategory:
                                raise lib.data.moneydata.NoSuchCategoryException(filter_from_category)

                        transactionfilter = transactionfilter.or_concat(
                                lambda t: t.fromcategory is fromcategory or t.fromcategory.is_contained_in_subtree(fromcategory)
                        )

                if filter_to_category:
                        tocategory = self.moneydata.get_category(filter_to_category)

                        if not tocategory:
                                raise lib.data.moneydata.NoSuchCategoryException(filter_to_category)

                        transactionfilter = transactionfilter.or_concat(
                                lambda t: t.tocategory is tocategory or t.tocategory.is_contained_in_subtree(tocategory)
                        )

                return transactionfilter

        def create_and_category_transactionfilter(self, filter_from_category, filter_to_category):
                transactionfilter = lib.data.filterchain.Filter(lambda t: True)

                if filter_from_category:
                        fromcategory = self.moneydata.get_category(filter_from_category)

                        if not fromcategory:
                                raise lib.data.moneydata.NoSuchCategoryException(filter_from_category)

                        transactionfilter = transactionfilter.and_concat(
                                lambda t: t.fromcategory is fromcategory or t.fromcategory.is_contained_in_subtree(fromcategory)
                        )

                if filter_to_category:
                        tocategory = self.moneydata.get_category(filter_to_category)

                        if not tocategory:
                                raise lib.data.moneydata.NoSuchCategoryException(filter_to_category)

                        transactionfilter = transactionfilter.and_concat(
                                lambda t: t.tocategory is tocategory or t.tocategory.is_contained_in_subtree(tocategory)
                        )

                return transactionfilter

        def create_maxlevel_categoryfilter(self, maxlevel):
                categoryfilter = lib.data.filterchain.Filter(lambda c: True)

                if maxlevel:
                        categoryfilter = categoryfilter.and_concat(lambda c: c.get_depth() <= maxlevel)

                return categoryfilter

        def create_subtree_categoryfilter(self, filter_rootcategory):
                categoryfilter = lib.data.filterchain.Filter(lambda c: True)

                rootcategory = self.moneydata.get_category(filter_rootcategory)

                if not rootcategory:
                        raise lib.data.moneydata.NoSuchCategoryException(filter_rootcategory)

                categoryfilter = categoryfilter.and_concat(
                        lambda c: c is rootcategory or c.is_contained_in_subtree(rootcategory)
                )

                return categoryfilter
