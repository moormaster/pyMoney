# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data.moneydata import PaymentPlan
from lib.io.formatter import PaymentPlanFormatter
from lib.io.parser import PaymentPlanParser

import csv
import os


def read(filename, paymentplanparser):
        with open(filename) as f:
                r = csv.DictReader(f)

                paymentplans = []
                for d in r:
                        paymentplan = paymentplanparser.parse(**d)

                        if paymentplan:
                                paymentplans.append(paymentplan)

                return sorted(paymentplans, key=lambda pp: pp.groupname + pp.name)


def write(filename, paymentplans, notfoundcategory, append=False):
        if append and not os.path.exists(filename):
                append = False

        if append:
                mode = 'a'
        else:
                mode = 'w'

        with open(filename, mode) as f:
                w = csv.DictWriter(f, fieldnames=["name", "groupname", "fromcategory", "tocategory", "amount", "comment"])

                if not append:
                        w.writeheader()

                for pp in paymentplans:
                        w.writerow(PaymentPlanFormatter.format(pp, notfoundcategory))

                f.close()
