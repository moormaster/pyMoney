from . import data
import csv
import os.path
import re
import datetime


class Transactions:
	def __init__(self):
		pass

	@staticmethod
	def read(filename, transactionparser):
		with open(filename) as f:
			r = csv.DictReader(f)

			transactionlist = []
			for d in r:
				transaction = transactionparser.parse(**d)
			
				if transaction:
					transactionlist.append(transaction)

			return sorted(transactionlist, key=lambda t: t.date)

	@staticmethod
	def write(filename, transactions, append=False):
		if append and not os.path.exists(filename):
			append = False

		if append:
			mode = 'a'
		else:
			mode = 'w'

		with open(filename, mode) as f:
			w = csv.DictWriter(f, fieldnames=data.Transaction.fields)

			if not append:
				w.writeheader()

			for t in transactions:
				w.writerow(TransactionFormatter.format(t))

			f.close()


class Categories:
	def __init__(self):
		pass

	@staticmethod
	def read(filename):
		categoryparser = CategoryParser()

		with open(filename, 'r') as f:
			line = f.readline()
			while line:
				categoryparser.parse(line)

				line = f.readline()

		return categoryparser.categorytree

	@staticmethod
	def write(filename, categorytree, notfoundcategory):
		with open(filename, 'w') as f:
			for node in categorytree:
				if not node.is_contained_in_subtree(notfoundcategory):
					f.write(CategoryFormatter.format(node) + "\n")

			f.close()


class CategoryParser:
	def __init__(self):
		self.categorytree = None
		self.nodestack = []

	def parse(self, line):
		match = re.match("^(\t*)([+-0]) (.*)$", line)

		if match is None:
			raise IOError("Could not parse line: \"" + line + "\"")

		groups = match.groups()

		if not len(groups) == 3:
			raise IOError("Could not parse line: \"" + line + "\"")

		depth = match.group(1).count("	")
		str_sign = match.group(2)
		name = match.group(3).strip()

		if str_sign == "+":
			sign = 1
		elif str_sign == "-":
			sign = -1
		elif str_sign == "0":
			sign = 0
		else:
			raise data.InvalidSignException(str_sign)

		while len(self.nodestack) > depth:
			self.nodestack.pop()

		if self.categorytree:
			node = self.nodestack[len(self.nodestack) - 1]
			node = node.append_childnode(data.CategoryTreeNode(name, sign))
		else:
			self.categorytree = data.CategoryTreeNode(name, sign)
			node = self.categorytree

		self.nodestack.append(node)

		return node


class CategoryFormatter:
	def __init__(self):
		pass

	@staticmethod
	def format(category):
		assert(isinstance(category, data.CategoryTreeNode))

		return "	" * category.get_depth() + str(category.sign) + " " + category.name


class TransactionParser:
	def __init__(self, categorytree, notfoundcategoryname, dateformat="%Y-%m-%d"):
		self.categorytree = categorytree
		self.dateformat = dateformat
		self.notfoundcategoryname = notfoundcategoryname

		self.autocreatenotfoundcategory = True

	def get_category(self, name):
		nodes = self.categorytree.find_nodes(name)

		if len(nodes) == 0:
			if self.autocreatenotfoundcategory:
				newcategory = self.get_notfound_category(autocreate=True).append_childnode(data.CategoryTreeNode(name, 1))
				nodes = [newcategory]
			else:
				raise data.NoSuchCategoryException(name)

		if len(nodes) > 1:
			raise data.AmbiguousCategoryNameException(name)

		return nodes[0]

	def get_notfound_category(self, autocreate=False):
		category = self.categorytree.find_first_node(self.notfoundcategoryname)

		if category is None and autocreate:
			category = self.categorytree.append_childnode(data.CategoryTreeNode(self.notfoundcategoryname, 1))

		return category

	def parse(self, date, category, amount, comment):
		date = datetime.datetime.strptime(date, self.dateformat).date()
		category = self.get_category(category)
		amount = float(amount)
		comment = comment

		return data.Transaction(date, category, amount, comment)


class TransactionFormatter:
	def __init__(self):
		pass

	@staticmethod
	def format(transaction):
		return {"date":		str(transaction.date),
				"category":	transaction.category.name,
				"amount":	str(transaction.amount),
				"comment":	transaction.comment}