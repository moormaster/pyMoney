from . import data
import csv
import os.path


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
		depth = line.count("	")
		name = line.strip()

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
		return "	" * category.get_depth() + category.name


class TransactionParser:
	def __init__(self, moneydata, dateformat="%Y-%m-%d"):
		self.moneydata = moneydata
		self.dateformat = dateformat

	def parse(self, date, category, amount, comment):
		return self.moneydata.parse_transaction(date, category, amount, comment, True, self.dateformat)


class TransactionFormatter:
	def __init__(self):
		pass

	@staticmethod
	def format(transaction):
		return {"date":		str(transaction.date),
				"category":	transaction.category.name,
				"amount":	str(transaction.amount),
				"comment":	transaction.comment}