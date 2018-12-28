# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
import lib.data
import lib.data.moneydata
import lib.io
import lib.io.parser
import lib.io.Categories
import lib.io.Transactions

import os


class MoneyDataSerialization:
        def __init__(self, fileprefix="pymoney"):
                self.fileprefix = ""
                self.filenames = {}

                self.set_fileprefix(fileprefix)

        def set_fileprefix(self, fileprefix):
                self.fileprefix = fileprefix

                self.filenames = {
                        "version": self.fileprefix + ".version",
                        "transactions": self.fileprefix + ".transactions",
                        "categories": self.fileprefix + ".categories"
                }

        def get_moneydata(self):
                return self.moneydata

        def read(self):
                moneydata = lib.data.moneydata.MoneyData()

                version = None
                if os.access(self.filenames["version"], os.F_OK):
                        version = lib.io.Version.read(self.filenames["version"])

                if version is None:
                        version = [1, 3]

                if os.access(self.filenames["categories"], os.F_OK):
                        moneydata.categorytree = lib.io.Categories.read(self.filenames["categories"])

                if os.access(self.filenames["transactions"], os.F_OK):
                        if version[0] == 2 and version[1] >= 0:
                                transactionparser = lib.io.parser.TransactionParser(moneydata.categorytree, moneydata.notfoundcategoryname)
                                transactions = lib.io.Transactions.read(self.filenames["transactions"], transactionparser)
                        elif version[0] == 1 and version[1] == 3:
                                transactionparser = lib.io.parser.TransactionParser(moneydata.categorytree, moneydata.notfoundcategoryname)
                                transactions = lib.io.Transactions_v1_3.read(self.filenames["transactions"], transactionparser)

                        for t in transactions:
                                moneydata.import_transaction(t)

                return moneydata

        def write(self, moneydata, skipwritetransactions=False):
                lib.io.Categories.write(self.filenames["categories"], moneydata.categorytree,
                        moneydata.get_notfound_category())

                if not skipwritetransactions:
                        lib.io.Transactions.write(self.filenames["transactions"], moneydata.transactions,
                                moneydata.get_notfound_category())

