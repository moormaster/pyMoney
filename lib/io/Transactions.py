# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data.moneydata import Transaction
from lib.io.formatter import TransactionFormatter

import csv
import os


def read(filename, transactionparser):
    with open(filename) as f:
        r = csv.DictReader(f)

        transactionlist = []
        for d in r:
            transaction = transactionparser.parse(**d)

            if transaction:
                transactionlist.append(transaction)

        return sorted(transactionlist, key=lambda t: t.date)


def write(filename, transactions, notfoundcategory, append=False):
    if append and not os.path.exists(filename):
        append = False

    if append:
        mode = 'a'
    else:
        mode = 'w'

    with open(filename, mode) as f:
        w = csv.DictWriter(f, fieldnames=["date", "fromcategory", "tocategory", "paymentplan", "amount", "comment"])

        if not append:
            w.writeheader()

        for t in transactions:
            w.writerow(TransactionFormatter.format(t, notfoundcategory))

        f.close()
