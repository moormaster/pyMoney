from lib.data.moneydata import CategoryTreeNode
from lib.data.moneydata import Transaction
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

		depth = match.group(1).count("	")
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


class TransactionParser:
	def __init__(self, categorytree, notfoundcategoryname, nextfreeindex, dateformat="%Y-%m-%d"):
		self.nextfreeindex = nextfreeindex
		self.categorytree = categorytree
		self.dateformat = dateformat
		self.notfoundcategoryname = notfoundcategoryname

		self.autocreatenotfoundcategory = True

	def get_category(self, name):
		nodes = self.categorytree.find_nodes_by_relative_path(name)

		if len(nodes) == 0:
			if self.autocreatenotfoundcategory:
				notfoundcategory = self.get_notfound_category(autocreate=True)
				node_names = name.split(".")

				newcategory = notfoundcategory
				for i in range(len(node_names)):
					if node_names[i] in newcategory.children:
						newcategory = newcategory.children[node_names[i]]
					else:
						newcategory = newcategory.append_childnode(CategoryTreeNode(node_names[i]))
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

	def parse(self, date, fromcategory, tocategory, amount, comment):
		index = self.nextfreeindex
		date = datetime.datetime.strptime(date, self.dateformat).date()
		fromcategory = self.get_category(fromcategory)
		tocategory = self.get_category(tocategory)
		amount = float(amount)
		comment = comment

		self.nextfreeindex += 1

		return Transaction(index, date, fromcategory, tocategory, amount, comment)
