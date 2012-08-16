import collections
import datetime

class TreeNode:
	def __init__(self, name):
		self.parent = None
		self.name = name
		self.children = {}

	def __iter__(self):
		return DFSIterator(self)

	def __str__(self):
		res = ""
		
		for node in self:
			_depth = "\t"*node.getDepth() + "+ "*bool(len(node.children)) + "- "*(not len(node.children))
			_name = node.name
			
			res += _depth + _name + "\n"
		
		return res
		
	def appendChildNode(self, node):
		self.children[node.name] = node
		node.parent = self
		
		return self.children[node.name]

	def removeChildNode(self, name):
		node = self.children[name]
		node.parent = None
		self.children.pop(name)
		
	def rename(self, newnodename):
		parent = self.parent
	
		if parent:
			parent.children.pop(self.name)
			parent.children[newnodename] = self
			
		self.name = newnodename	
	
	def getDepth(self):
		if not self.parent:
			return 0
		else:
			return self.parent.getDepth() + 1

	def getRoot(self):
		p = self
		while not p.parent is None:
			p = p.parent
		return p
		
	def findNode(self, name):
		if name == self.name:
			return self
		else:
			for c in self.children.values():
				res = c.findNode(name)
				if res:
					return res
		
		return None
		
	def getFullName(self):
		if self.parent:
			return self.parent.getFullName() + "." + self.name
		else:
			return self.name
	
	def isChildOf(self, node):		
		p = self
		while not p.parent is None:
			p = p.parent
			if node == p:
				return True
		return False

	def isRootOf(self, node):
		return node.isChildOf(self)

class DFSIterator:
	def __init__(self, treenode):
		self.nodestack = [treenode]

	def __iter__(self):
		return self;

	def __next__(self):
		if not len(self.nodestack):
			raise StopIteration
		
		node = self.nodestack.pop(0)
		self.nodestack = list(node.children.values()) + self.nodestack
		
		return node
		
class NodeSummary:
	__slots__ = ["amount", "sum"]
	
	def __init__(self):
		self.amount = 0
		self.sum = 0
	
		pass
		

class Transaction:
	fields = ["date", "category", "amount", "comment"]
	__slots__ = fields
	
	def __init__(self, date, category, amount, comment):
		self.date = date
		self.category = category
		self.amount = amount
		self.comment = comment
		
class TransactionFactory:
	def __init__(self, categorytree, autocreatebasenode=None, dateformat="%Y-%m-%d"):
		self.categorytree = categorytree
		self.autocreatebasenode = autocreatebasenode
		self.dateformat = dateformat
	
	def create(self, date, category, amount, comment):
		_category = self.categorytree.findNode(category)
		if not _category:
			if self.autocreatebasenode:
				_category = self.autocreatebasenode.appendChildNode(TreeNode(category))
			else:
				return None
		
		_date = datetime.datetime.strptime(date, self.dateformat).date()
		_amount = float(amount)
		_comment = comment
		
		return Transaction(_date, _category, _amount, _comment)
		
	def create_string_dict(self, transaction):
		return {	"date":		str(transaction.date),
				"category":	transaction.category.name,
				"amount":	str(transaction.amount),
				"comment":	transaction.comment}
