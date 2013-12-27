import datetime


class MoneyData:
	def __init__(self):
		self.categorytree = CategoryTreeNode("All")
		self.transactions = []

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
		date = datetime.datetime.strptime(str_date, dateformat).date()
		category = self.get_category(str_category, autocreatenotfoundcategory)
		amount = float(str_amount)
		comment = str_comment

		return Transaction(date, category, amount, comment)

	def get_category(self, name, autocreatenotfoundcategory=False):
		nodes = self.categorytree.find_nodes(name)

		if len(nodes) == 0:
			if autocreatenotfoundcategory:
				newcategory = self.get_notfound_category(autocreate=True).append_childnode(CategoryTreeNode(name))
				nodes = [newcategory]
			else:
				raise NoSuchCategoryException(name)

		if len(nodes) > 1:
			raise AmbiguousCategoryNameException(name)

		return nodes[0]

	def get_notfound_category(self, autocreate=False):
		category = self.categorytree.find_first_node("NOTFOUND")

		if category is None and autocreate:
			category = self.categorytree.append_childnode(CategoryTreeNode("NOTFOUND"))

		return category

	def category_is_contained_in_notfound_category(self, category):
		notfoundcategory = self.get_notfound_category(False)

		if notfoundcategory is None:
			return False

		return category.is_contained_in_subtree(notfoundcategory)

	def add_category(self, parentname, name):
		category = self.categorytree.find_first_node(name)
		parentcategory = self.categorytree.find_first_node(parentname)

		if category and not self.category_is_contained_in_notfound_category(category):
			raise DuplicateCategoryException(category)

		if not parentcategory:
			raise NoSuchCategoryException(parentname)

		if category and self.category_is_contained_in_notfound_category(category):
			category.parent.remove_childnode_by_name(name)

		newcategory = CategoryTreeNode(name)
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

			d_summary[t.category.name].amount += t.amount

			c = t.category
			while c:
				d_summary[c.name].sum += t.amount
				c = c.parent

		return d_summary


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
			_depth = "\t"*node.get_depth() + "+ "*bool(len(node.children)) + "- "*(not len(node.children))
			_name = node.name

			res += _depth + _name + "\n"

		return res

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


class CategoryTreeNode(TreeNode):
	def __init__(self, name):
		TreeNode.__init__(self, name)

	def append_childnode(self, node):
		assert isinstance(node, CategoryTreeNode)

		if self.find_first_node(node.name):
			raise DuplicateCategoryException(node)

		return TreeNode.append_childnode(self, node)


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


