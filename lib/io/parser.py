# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data.moneydata import CategoryTreeNode
from lib.data.moneydata import Transaction
from lib.data.moneydata import PaymentPlan
from lib.data.moneydata import AmbiguousCategoryNameException
from lib.data.moneydata import NoSuchCategoryException

import datetime
import re


class CategoryParser:
        def __init__(self):
                self.categorytree = None
                self.nodestack = []

        def parse(self, line):
                match = re.match("^(\t*)(.*)$", line)

                if match is None:
                        raise IOError("Could not parse line: \"" + line + "\"")

                groups = match.groups()

                if not len(groups) == 2:
                        raise IOError("Could not parse line: \"" + line + "\"")

                depth = match.group(1).count("\t")
                name = match.group(2).strip()

                while len(self.nodestack) > depth:
                        self.nodestack.pop()

                if self.categorytree:
                        node = self.nodestack[len(self.nodestack) - 1]
                        node = node.append_childnode(CategoryTreeNode(name))
                else:
                        self.categorytree = CategoryTreeNode(name)
                        node = self.categorytree

                self.nodestack.append(node)

                return node


class CategoryFinder:
        def __init__(self, categorytree, notfoundcategoryname):
                self.categorytree = categorytree
                self.notfoundcategoryname = notfoundcategoryname

                self.autocreatenotfoundcategory = True

        def set_autocreatenotfoundcategory(self, autocreatenotfoundcategory):
                self.autocreatenotfoundcategory = autocreatenotfoundcategory

        def get_category(self, name):
                nodes = self.categorytree.find_nodes_by_relative_path(name)

                if len(nodes) == 0:
                        if self.autocreatenotfoundcategory:
                                notfoundcategory = self.get_notfound_category(autocreate=True)
                                newcategory = notfoundcategory.append_by_relative_path(name)

                                nodes = [newcategory]
                        else:
                                raise NoSuchCategoryException(name)

                if len(nodes) > 1:
                        raise AmbiguousCategoryNameException(name, nodes)

                return nodes[0]

        def get_notfound_category(self, autocreate=False):
                category = self.categorytree.find_first_node_by_relative_path(
                        self.categorytree.name + "." + self.notfoundcategoryname)

                if category is None and autocreate:
                        category = self.categorytree.append_childnode(CategoryTreeNode(self.notfoundcategoryname))

                return category



class TransactionParser_v1_3:
        def __init__(self, categorytree, notfoundcategoryname, dateformat="%Y-%m-%d"):
                self.categoryfinder = CategoryFinder(categorytree, notfoundcategoryname)
                self.dateformat = dateformat

        def set_autocreatenotfoundcategory(self, autocreatenotfoundcategory):
                self.categoryfinder.set_autocreatenotfoundcategory(autocreatenotfoundcategory)

        def parse(self, date, fromcategory, tocategory, amount, comment):
                index = None
                date = datetime.datetime.strptime(date, self.dateformat).date()
                fromcategory = self.categoryfinder.get_category(fromcategory)
                tocategory = self.categoryfinder.get_category(tocategory)
                paymentplan = None
                amount = float(amount)
                comment = comment

                return Transaction(index, date, fromcategory, tocategory, amount, comment)

class TransactionParser:
        def __init__(self, categorytree, notfoundcategoryname, paymentplans, dateformat="%Y-%m-%d"):
                assert(isinstance(paymentplans,dict))

                self.categoryfinder = CategoryFinder(categorytree, notfoundcategoryname)
                self.paymentplans = paymentplans
                self.dateformat = dateformat

        def set_autocreatenotfoundcategory(self, autocreatenotfoundcategory):
                self.categoryfinder.set_autocreatenotfoundcategory(autocreatenotfoundcategory)

        def parse(self, date, fromcategory, tocategory, paymentplan, amount, comment):
                index = None
                date = datetime.datetime.strptime(date, self.dateformat).date()
                fromcategory = self.categoryfinder.get_category(fromcategory)
                tocategory = self.categoryfinder.get_category(tocategory)
                if len(paymentplan) == 0:
                        paymentplan = None
                else:
                        paymentplan = self.paymentplans[paymentplan]
                amount = float(amount)
                comment = comment

                transaction = Transaction(index, date, fromcategory, tocategory, amount, comment)
                transaction.paymentplan = paymentplan

                return transaction


class PaymentPlanParser:
        def __init__(self, categorytree, notfoundcategoryname):
                self.categoryfinder = CategoryFinder(categorytree, notfoundcategoryname)

        def set_autocreatenotfoundcategory(self, autocreatenotfoundcategory):
                self.categoryfinder.set_autocreatenotfoundcategory(autocreatenotfoundcategory)

        def parse(self, name, groupname, fromcategory, tocategory, amount, comment):
                name = name
                groupname = groupname
                fromcategory = self.categoryfinder.get_category(fromcategory)
                tocategory = self.categoryfinder.get_category(tocategory)
                amount = float(amount)
                comment = comment

                return PaymentPlan(name, groupname, fromcategory, tocategory, amount, comment)

