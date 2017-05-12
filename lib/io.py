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
	def write(filename, transactions, notfoundcategory, append=False):
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
				w.writerow(TransactionFormatter.format(t, notfoundcategory))

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
		match = re.match("^(\t*)(.*)$", line)

		if match is None:
			raise IOError("Could not parse line: \"" + line + "\"")

		groups = match.groups()

		if not len(groups) == 2:
			raise IOError("Could not parse line: \"" + line + "\"")

		depth = match.group(1).count("	")
		name = match.group(2).strip()

		while len(self.nodestack) > depth:
			self.nodestack.pop()

		if self.categorytree:
			node = self.nodestack[len(self.nodestack) - 1]
			node = node.append_childnode(data.CategoryTreeNode(name))
		else:
			self.categorytree = data.CategoryTreeNode(name)
			node = self.categorytree

		self.nodestack.append(node)

		return node


class CategoryFormatter:
	def __init__(self):
		pass

	@staticmethod
	def format(category):
		assert(isinstance(category, data.CategoryTreeNode))

		return "\t" * category.get_depth() + category.name


class TransactionParser:
	def __init__(self, categorytree, notfoundcategoryname, dateformat="%Y-%m-%d"):
		self.categorytree = categorytree
		self.dateformat = dateformat
		self.notfoundcategoryname = notfoundcategoryname

		self.autocreatenotfoundcategory = True

	def get_category(self, name):
		nodes = self.categorytree.find_nodes_by_relative_path(name)

		if len(nodes) == 0:
			if self.autocreatenotfoundcategory:
				notfoundcategory = self.get_notfound_category(autocreate=True)
				nodeNames = name.split(".")

				newcategory = notfoundcategory
				for i in range(len(nodeNames)):
					if nodeNames[i] in newcategory.children:
						newcategory = newcategory.children[nodeNames[i]]
					else:
						newcategory = newcategory.append_childnode(data.CategoryTreeNode(nodeNames[i]))
				nodes = [newcategory]
			else:
				raise data.NoSuchCategoryException(name)

		if len(nodes) > 1:
			raise data.AmbiguousCategoryNameException(name)

		return nodes[0]

	def get_notfound_category(self, autocreate=False):
		category = self.categorytree.find_first_node_by_relative_path(self.categorytree.name + "." + self.notfoundcategoryname)

		if category is None and autocreate:
			category = self.categorytree.append_childnode(data.CategoryTreeNode(self.notfoundcategoryname))

		return category

	def parse(self, date, fromcategory, tocategory, amount, comment):
		date = datetime.datetime.strptime(date, self.dateformat).date()
		fromcategory = self.get_category(fromcategory)
		tocategory = self.get_category(tocategory)
		amount = float(amount)
		comment = comment

		return data.Transaction(date, fromcategory, tocategory, amount, comment)


class TransactionFormatter:
	def __init__(self):
		pass

	@staticmethod
	def format(transaction, notfoundcategory):
		if not notfoundcategory is None and transaction.fromcategory.is_contained_in_subtree(notfoundcategory):
			str_fromcategory = transaction.fromcategory.get_relative_name_to(notfoundcategory)
			str_fromcategory = str_fromcategory[len(notfoundcategory.name)+1:]
		else:
			str_fromcategory = transaction.fromcategory.get_unique_name()

		if not notfoundcategory is None and transaction.tocategory.is_contained_in_subtree(notfoundcategory):
			str_tocategory = transaction.tocategory.get_relative_name_to(notfoundcategory)
			str_tocategory = str_tocategory[len(notfoundcategory.name)+1:]
		else:
			str_tocategory = transaction.tocategory.get_unique_name()

		return {"date":			str(transaction.date),
				"fromcategory":	str_fromcategory,
				"tocategory":	str_tocategory,
				"amount":		str(transaction.amount),
				"comment":		transaction.comment}