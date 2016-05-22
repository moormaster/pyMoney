from . import io


class MoneyData:
	def __init__(self):
		self.categorytree = CategoryTreeNode("All", 1)
		self.transactions = []

		self.notfoundcategoryname = "NOTFOUND"

	def filter_transactions(self, filter_func):
		return FilterIterator(self.transactions.__iter__(), filter_func)

	def add_transaction(self, str_date, str_category, str_amount, str_comment, force=False):
		node = self.categorytree.find_first_node(str_category)
		if node is None and not force:
			raise NoSuchCategoryException(str_category)

		newtransaction = self.parse_transaction(str_date, str_category, str_amount, str_comment, force)
		self.transactions.append(newtransaction)

		return newtransaction

	def delete_transaction(self, index):
		del self.transactions[index]

	def parse_transaction(	self, str_date, str_category, str_amount, str_comment,
							autocreatenotfoundcategory=False, dateformat="%Y-%m-%d"):
		parser = io.TransactionParser(self.categorytree, self.notfoundcategoryname, dateformat)
		parser.autocreatenotfoundcategory = autocreatenotfoundcategory

		return parser.parse(str_date, str_category, str_amount, str_comment)

	def get_category(self, name):
		nodes = self.categorytree.find_nodes(name)

		if len(nodes) == 0:
			raise NoSuchCategoryException(name)

		if len(nodes) > 1:
			raise AmbiguousCategoryNameException(name)

		return nodes[0]

	def get_notfound_category(self):
		category = self.categorytree.find_first_node(self.notfoundcategoryname)

		return category

	def category_is_contained_in_notfound_category(self, category):
		notfoundcategory = self.get_notfound_category()

		if notfoundcategory is None:
			return False

		return category.is_contained_in_subtree(notfoundcategory)

	def add_category(self, parentname, name, str_sign):
		category = self.categorytree.find_first_node(name)
		parentcategory = self.categorytree.find_first_node(parentname)

		if category and not self.category_is_contained_in_notfound_category(category):
			raise DuplicateCategoryException(category)

		if not parentcategory:
			raise NoSuchCategoryException(parentname)

		if category and self.category_is_contained_in_notfound_category(category):
			category.parent.remove_childnode_by_name(name)

		newcategory = CategoryTreeNode(name, Sign.parse(str_sign))
		parentcategory.append_childnode(newcategory)

		return newcategory

	def delete_category(self, name):
		node = self.categorytree.find_first_node(name)

		if not node:
			raise NoSuchCategoryException(name)

		if not node.parent:
			raise CategoryIsTopCategoryException(node)

		node.parent.remove_childnode(node)

	def rename_category(self, name, newname):
		category = self.categorytree.find_first_node(name)
		newcategory = self.categorytree.find_first_node(newname)

		if not category:
			raise NoSuchCategoryException(name)

		if newcategory and not self.category_is_contained_in_notfound_category(newcategory):
			raise DuplicateCategoryException(newcategory)

		if newcategory and self.category_is_contained_in_notfound_category(newcategory):
			newcategory.parent.remove_childnode_by_name(newname)

		category.rename(newname)

	def setsign_of_category(self, name, str_newsign):
		category = self.categorytree.find_first_node(name)

		if not category:
			raise NoSuchCategoryException(name)

		category.sign = Sign.parse(str_newsign)

	def merge_category(self, name, targetname):
		category = self.categorytree.find_first_node(name)
		targetcategory = self.categorytree.find_first_node(targetname)

		if not category:
			raise NoSuchCategoryException(name)

		if not targetcategory:
			raise NoSuchCategoryException(targetname)

		targetcategory.merge_node(category)

		for t in self.transactions:
			if t.category == category:
				t.category = targetcategory

	def move_category(self, name, newparentname):
		node = self.categorytree.find_first_node(name)
		newparent = self.categorytree.find_first_node(newparentname)

		if not node:
			raise NoSuchCategoryException(name)

		if not newparent:
			raise NoSuchCategoryException(newparentname)

		newparent.move_node(node)

	def create_summary(self, transactionfilter):
		d_summary = {}

		for c in self.categorytree:
			d_summary[c.name] = NodeSummary()

		for t in self.transactions:
			if not transactionfilter(t):
				continue

			d_summary[t.category.name].amount += t.category.sign.value * t.amount

			c = t.category
			while not c is None:
				d_summary[c.name].sum += t.category.get_absolute_sign().value * t.amount
				c = c.parent

		return d_summary


class TreeNode:
	def __init__(self, name):
		self.parent = None
		self.name = name
		self.children = {}

	def __iter__(self):
		return DFSIterator(self)

	def __str__(self, fullname=False):
		res = ""

		for node in self:
			res += node.format(fullname) + "\n"

		return res

	def format(self, fullname=False):
		_depth = "\t"*self.get_depth()

		if fullname:
			_name = self.get_full_name()
		else:
			_name = self.name

		return _depth + _name


	def append_childnode(self, node):
		assert isinstance(node, TreeNode)

		self.children[node.name] = node
		node.parent = self

		return self.children[node.name]

	def remove_childnode_by_name(self, name):
		if not name in self.children:
			raise NoSuchNodeException(name)

		node = self.children[name]

		self.remove_childnode(node)

	def remove_childnode(self, node):
		if not node.name in self.children or node != self.children[node.name]:
			raise NodeIsNotAChildException(self, node)

		node.parent = None
		self.children.pop(node.name)

	def merge_node(self, sourcenode):
		if self.is_contained_in_subtree(sourcenode):
			raise TargetNodeIsPartOfSourceNodeSubTreeException(sourcenode, self)

		if sourcenode.parent is not None:
			sourcenode.parent.remove_childnode(sourcenode)

		children = []
		for c in sourcenode.children:
			children.append(sourcenode.children[c])

		for c in children:
			sourcenode.remove_childnode(c)
			self.append_childnode(c)

	def move_node(self, sourcenode):
		if self.is_contained_in_subtree(sourcenode):
			raise TargetNodeIsPartOfSourceNodeSubTreeException(sourcenode, self)

		if sourcenode.parent is not None:
			sourcenode.parent.remove_childnode(sourcenode)

		self.append_childnode(sourcenode)

	def rename(self, newnodename):
		parent = self.parent

		if parent:
			parent.children.pop(self.name)
			parent.children[newnodename] = self

		self.name = newnodename

	def get_depth(self):
		if not self.parent:
			return 0
		else:
			return self.parent.get_depth() + 1

	def get_root(self):
		p = self

		while p.parent is not None:
			p = p.parent

		return p

	def find_first_node(self, name):
		if name == self.name:
			return self
		else:
			for c in self.children.values():
				res = c.find_first_node(name)
				if res:
					return res

		return None

	def find_nodes(self, name):
		l = []

		if name == self.name:
			l.append(self)
		else:
			for c in self.children.values():
				l = l + c.find_nodes(name)

		return l

	def get_full_name(self):
		if self.parent:
			return self.parent.get_full_name() + "." + self.name
		else:
			return self.name

	def is_contained_in_subtree(self, node):
		if node == self:
			return True

		p = self
		while not p.parent is None:
			p = p.parent
			if node == p:
				return True
		return False

	def is_root_of(self, node):
		return node.is_contained_in_subtree(self)


class CategoryTreeNode(TreeNode):
	def __init__(self, name, sign):
		TreeNode.__init__(self, name)

		if type(sign) == int:
			self.sign = Sign(sign)
		elif isinstance(sign, Sign):
			self.sign = sign
		else:
			raise TypeError("Can't convert type " + str(type(sign)) + " to " + str(Sign) + " implicitly")

	def append_childnode(self, node):
		assert isinstance(node, CategoryTreeNode)

		if self.find_first_node(node.name):
			raise DuplicateCategoryException(node)

		return TreeNode.append_childnode(self, node)

	def get_absolute_sign(self, root_category=None):
		node = self
		value = node.sign.value
		while not node.parent is None and (root_category is None or not node == root_category):
			node = node.parent

			value = value * node.sign.value

		return Sign(value)

	def format(self, fullname=False):
		_depth = "\t"*self.get_depth()
		_sym = str(self.sign) + " "

		if fullname:
			_name = self.get_full_name()
		else:
			_name = self.name

		return _depth + _sym  + _name


class Sign:
	def __init__(self, value):
		self.value = value

	def __str__(self):
		if self.value == -1:
			return "-"
		elif self.value == 0:
			return "0"
		elif self.value == 1:
			return "+"
		else:
			raise InvalidSignException(self.value)

	def parse(str_sign):
		if str_sign == "+":
			value = 1
		elif str_sign == "-":
			value = -1
		elif str_sign == "0":
			value = 0
		else:
			raise InvalidSignException(str_sign)

		return Sign(value)


class DFSIterator:
	def __init__(self, treenode):
		self.treenode = treenode
		self.nodestack = [treenode]

	def __iter__(self):
		return DFSIterator(self.treenode)

	def __next__(self):
		if not len(self.nodestack):
			raise StopIteration
		
		node = self.nodestack.pop(0)
		self.nodestack = list(node.children.values()) + self.nodestack
		
		return node


class Transaction(object):
	fields = ["date", "category", "amount", "comment"]
	__slots__ = fields

	def __init__(self, date, category, amount, comment):
		assert(isinstance(category, CategoryTreeNode))

		self.date = date
		self.category = category
		self.amount = amount
		self.comment = comment


class NodeSummary(object):
	__slots__ = ["amount", "sum"]
	
	def __init__(self):
		self.amount = 0
		self.sum = 0
	
		pass


class FilterIterator:
	def __init__(self, iterator, filter_func):
		self.iterator = iterator
		self.filter_func = filter_func
		self.index = None

	def __iter__(self):
		return self

	def __next__(self):
		if self.index is None:
			self.index = -1

		nextitem = self.iterator.__next__()
		self.index += 1

		while nextitem is not None and not self.filter_func(nextitem):
			nextitem = self.iterator.__next__()
			self.index += 1

		return nextitem


class Filter:
	def __init__(self, filter_func):
		self.filter_func = filter_func

	def __call__(self, item):
		return self.filter_func(item)

	def or_concat(self, filter_func):
		return Filter(lambda item: self(item) or filter_func(item))

	def and_concat(self, filter_func):
		return Filter(lambda item: self(item) and filter_func(item))

	def negate(self):
		return Filter(lambda item: not self(item))


class NoSuchNodeException(Exception):
	def __init__(self, name):
		Exception.__init__(self, name)
		self.name = name


class NodeIsNotAChildException(Exception):
	def __init__(self, parentnode, node):
		assert isinstance(parentnode, TreeNode)
		assert isinstance(node, TreeNode)

		Exception.__init__(self, parentnode.name, node.name)
		self.parentnode = parentnode
		self.node = node


class TargetNodeIsPartOfSourceNodeSubTreeException(Exception):
	def __init__(self, sourcenode, targetnode):
		assert isinstance(sourcenode, TreeNode)
		assert isinstance(targetnode, TreeNode)

		Exception.__init__(self, sourcenode.name, targetnode.name)
		self.sourcenode = sourcenode
		self.targetnode = targetnode

class AmbiguousCategoryNameException(Exception):
	def __init__(self, name):
		Exception.__init__(self, name)

		self.name = name


class DuplicateCategoryException(Exception):
	def __init__(self, category):
		assert isinstance(category, CategoryTreeNode)

		Exception.__init__(self, category.name)
		self.category = category


class NoSuchCategoryException(NoSuchNodeException):
	def __init__(self, name):
		NoSuchNodeException.__init__(self, name)


class CategoryIsTopCategoryException(Exception):
	def __init__(self, category):
		assert isinstance(category, CategoryTreeNode)

		Exception.__init__(self, category.name)
		self.category = category


class InvalidSignException(Exception):
	def __init__(self, str_sign):
		Exception.__init__(self, str_sign)

		self.str_sign = str_sign