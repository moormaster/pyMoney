from . import data
from . import io

import errno
import sys

class PyMoney:
	def __init__(self, fileprefix="pymoney"):
		self.set_fileprefix(fileprefix)
	
		self.read_categories()
	
		self.transactionfactory = data.TransactionFactory(self.categorytree, self.notfoundcategory)
		self.read_transactions()
		
	def set_fileprefix(self, fileprefix):
		self.fileprefix = fileprefix
		
		self.filenames = {
			"transactions" : 	self.fileprefix + ".transactions",
			"categories" :		self.fileprefix + ".categories" }
			
	def filter_transactions(self, filter_func):
		return data.FilterIterator(self.transactions.__iter__(), filter_func)

	def add_transaction(self, date, category, amount, comment):
		newtransaction = self.transactionfactory.create(date, category, amount, comment)
		self.transactions.append(newtransaction);
				
	def delete_transaction(self, index):
		del self.transactions[index]
		
	def read_transactions(self):
		try:
			self.transactions = io.read_transactions(self.filenames["transactions"], self.transactionfactory)
		except IOError as e:
			self.transactions = []
			
			if not e.errno == errno.ENOENT:
				raise e			
		
	def write_transactions(self):
		io.write_transactions(self.filenames["transactions"], self.transactionfactory, self.transactions)
		
	def add_category(self, parentname, name):
		node = self.categorytree.findNode(name)
		parentnode = self.categorytree.findNode(parentname)
		
		if node and not node.isChildOf(self.notfoundcategory):
			raise Exception("node already exists: " + name)

		if not parentnode:
			raise Exception("no such node: " + parentname)
			
		if node and node.isChildOf(self.notfoundcategory):
			node.parent.removeChildNode(name)
		
		parentnode.appendChildNode(data.TreeNode(name))
		
	def delete_category(self, name):
		node = self.categorytree.findNode(name)
		
		if not node:
			raise Exception("no such node: " + name)

		if not node.parent:
			raise Exception("cannot remove topnode: " + name)

		node.parent.removeChildNode(node.name)
		
	def rename_category(self, name, newname):
		node = self.categorytree.findNode(name)
		newnode = self.categorytree.findNode(newname)
		
		if not node:
			raise Exception("no such node: " + name)
			
		parent = node.parent
			
		if newnode and not newnode.isChildOf(self.notfoundcategory):
			raise Exception("node already exists: " + newname)

		if newnode and newnode.isChildOf(self.notfoundcategory):
			newnode.parent.removeChildNode(args["newname"])
		
		node.rename(newname)
		
	def merge_category(self, name, newname):
		node = categorytree.findNode(name)
		newnode = categorytree.findNode(newname)
		
		if not node:
			raise Exception("no such node: " + oldname)
			
		parent = node.parent
			
		if not node.parent:
			print("cannot merge root node")
			return
		
		node.parent.removeChildNode(nodename)
		for t in transactions:
			if t.category == node:
				t.category = newnode
				
	def move_category(self, name, newparentname):
		node = self.categorytree.findNode(name)
		newparent = self.categorytree.findNode(newparentname)

		if not node:
			raise Exception("no such node: " + name)

		if not newparent:
			raise Exception("no such node: " + newparentname)

		if newparent.isChildOf(node):
			raise Exception("cannot move node to one of its subnodes: " + name)

		node.parent.removeChildNode(name)
		newparent.appendChildNode(node)
				
	def read_categories(self):
		try:
			self.categorytree = io.read_categories(self.filenames["categories"])
		except IOError as e:
			self.categorytree = data.TreeNode("All")
			
			if not e.errno == errno.ENOENT:
				raise e
				
		self.notfoundcategory = self.categorytree.findNode("NOTFOUND")
		if not self.notfoundcategory:
			self.notfoundcategory = self.categorytree.appendChildNode(data.TreeNode("NOTFOUND"))
			
	def write_categories(self):
		io.write_categories(self.filenames["categories"], self.categorytree, self.notfoundcategory)
		
	def create_summary(self, filter):
		d_summary = {}
	
		for c in self.categorytree:
			d_summary[c.name] = data.NodeSummary()
			
		for t in self.transactions:
			if not filter(t):
				continue
			
			d_summary[t.category.name].amount += t.amount
			
			c = t.category
			while c:
				d_summary[c.name].sum += t.amount
				c = c.parent
				
		return d_summary
