from . import io


class MoneyData:
	def __init__(self):
		self.categorytree = CategoryTreeNode("All")
		self.transactions = []

		self.notfoundcategoryname = "NOTFOUND"

	def filter_transactions(self, filter_func):
		return FilterIterator(self.transactions.__iter__(), filter_func)

	def add_transaction(self, str_date, str_fromcategory, str_tocategory, str_amount, str_comment, force=False):
		try:
			fromnode = self.get_category(str_fromcategory)
			tonode = self.get_category(str_tocategory)
		except NoSuchCategoryException as e:
			if not force:
				raise e

		newtransaction = self.parse_transaction(str_date, str_fromcategory, str_tocategory, str_amount, str_comment, force)
		self.transactions.append(newtransaction)

		return newtransaction

	def delete_transaction(self, index):
		del self.transactions[index]

	def parse_transaction(	self, str_date, str_categoryin, str_categoryout, str_amount, str_comment,
							autocreatenotfoundcategory=False, dateformat="%Y-%m-%d"):
		parser = io.TransactionParser(self.categorytree, self.notfoundcategoryname, dateformat)
		parser.autocreatenotfoundcategory = autocreatenotfoundcategory

		return parser.parse(str_date, str_categoryin, str_categoryout, str_amount, str_comment)

	def get_category(self, name):
		nodes = self.categorytree.find_nodes_by_relative_path(name)

		if len(nodes) == 0:
			raise NoSuchCategoryException(name)

		if len(nodes) > 1:
			raise AmbiguousCategoryNameException(name)

		return nodes[0]

	def get_notfound_category(self):
		try:
			category = self.get_category(self.categorytree.name + "." + self.notfoundcategoryname)
		except NoSuchCategoryException as e:
			return None

		return category

	def category_is_contained_in_notfound_category(self, category):
		try:
			notfoundcategory = self.get_notfound_category()
		except NoSuchCategoryException as e:
			return False

		return category.is_contained_in_subtree(notfoundcategory)

	def add_category(self, parentname, name):
		notfoundcategory = self.get_notfound_category()
		category = None
		if not notfoundcategory is None:
			category = notfoundcategory.find_first_node_by_relative_path(name)
		parentcategory = self.get_category(parentname)

		if not category is None:
			category.parent.remove_childnode_by_name(name)

		newcategory = CategoryTreeNode(name)
		parentcategory.append_childnode(newcategory)

		return newcategory

	def delete_category(self, name):
		node = self.get_category(name)

		if not node:
			raise NoSuchCategoryException(name)

		if not node.parent:
			raise CategoryIsTopCategoryException(node)

		node.parent.remove_childnode(node)

	def rename_category(self, name, newname):
		category = self.get_category(name)
		notfoundcategory = self.get_notfound_category()
		newcategory = None
		if not notfoundcategory is None:
			newcategory = notfoundcategory.find_first_node_by_relative_path(newname)
			if not newcategory is None and not newcategory.parent is notfoundcategory:
				newcategory = None

		if newname in category.parent.children:
			raise DuplicateCategoryException(newname)

		if not newcategory is None:
			newcategory.parent.remove_childnode_by_name(newname)

		category.rename(newname)

	def merge_category(self, name, targetname):
		categories = []
		targetcategories = []

		categories.append(self.get_category(name))
		targetcategories.append(self.get_category(targetname))

		i=0
		while i<len(categories):
			category = categories[i]
			targetcategory = targetcategories[i]

			for child in category.children:
				if child in targetcategory.children:
					categories.append(category.children[child])
					targetcategories.append(targetcategory.children[child])

			for t in self.transactions:
				if t.fromcategory == category:
					t.fromcategory = targetcategory
				if t.tocategory == category:
					t.tocategory = targetcategory

			i = i+1

		category = categories[0]
		targetcategory = targetcategories[0]

		targetcategory.merge_node(category)

	def move_category(self, name, newparentname):
		node = self.get_category(name)
		newparent = self.get_category(newparentname)

		newparent.move_node(node)

	def create_summary(self, transactionfilter):
		d_summary = {}

		for c in self.categorytree:
			d_summary[c.get_unique_name()] = NodeSummary()

		for t in self.transactions:
			if not transactionfilter(t):
				continue

			fromkey = t.fromcategory.get_unique_name()
			tokey = t.tocategory.get_unique_name()

			d_summary[fromkey].amountout -= t.amount
			d_summary[fromkey].amount -= t.amount

			d_summary[tokey].amountin += t.amount
			d_summary[tokey].amount += t.amount

			c = t.fromcategory
			while not c is None:
				key = c.get_unique_name()
				d_summary[key].sumout -= t.amount
				d_summary[key].sum -= t.amount
				c = c.parent

			c = t.tocategory
			while not c is None:
				key = c.get_unique_name()
				d_summary[key].sumin += t.amount
				d_summary[key].sum += t.amount
				c = c.parent

		return d_summary


class TreeNode:
	def __init__(self, name):
		self.parent = None
		self.name = name
		self.children = {}

		if "." in name:
			raise Exception("name may not contain character .")

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

		if node.name in self.children:
			raise DuplicateNodeException(self, node.name)

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
			if c.name in  self.children:
				self.children[c.name].merge_node(c)
			else:
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
			if newnodename in parent.children:
				raise DuplicateNodeException(parent, newnodename)

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

	def find_nodes(self, name):
		l = []

		if name == self.name:
			l.append(self)
		else:
			for c in self.children.values():
				l = l + c.find_nodes(name)

		return l

	def find_nodes_by_relative_path(self, path):
		names = path.split(".")
		l = self.find_nodes(names[-1])

		for i in range(len(l)).__reversed__():
			match = True

			node = l[i]
			for j in range(len(names)).__reversed__():
				if node is None or node.name != names[j]:
					match = False

				if not node is None:
					node = node.parent

			if not match:
				l.pop(i)

		return l

	def find_first_node_by_relative_path(self, path):
		l = self.find_nodes_by_relative_path(path)

		if len(l) > 0:
			return l[0]

		return None

	def get_full_name(self):
		if self.parent:
			return self.parent.get_full_name() + "." + self.name
		else:
			return self.name

	def get_relative_name_to(self, ancestor):
		assert isinstance(ancestor, TreeNode)

		node = self
		name = self.name
		while not node is ancestor:
			node = node.parent
			name = node.name + "." + name

		return name

	def get_unique_name(self):
		root_node = self.get_root()

		matching_nodes = root_node.find_nodes(self.name)
		namestart_nodes = matching_nodes.copy()

		namestart_node = self
		has_duplicates = len(matching_nodes) > 1

		while has_duplicates:
			names = []

			has_duplicates = False
			for i in range(len(namestart_nodes)):
				namestart_nodes[i] = namestart_nodes[i].parent
				nodename = matching_nodes[i].get_relative_name_to(namestart_nodes[i])
				if matching_nodes[i] is self:
					namestart_node = namestart_nodes[i]

				if nodename in names:
					has_duplicates = True
				names.append(nodename)

		return self.get_relative_name_to(namestart_node)

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
	def __init__(self, name):
		TreeNode.__init__(self, name)

	def append_childnode(self, node):
		assert isinstance(node, CategoryTreeNode)

		root_node = self.get_root()

		if node.name == root_node.name:
			raise DuplicateCategoryException(node.name)

		if node.name in self.children:
			raise DuplicateCategoryException(node.name)

		return TreeNode.append_childnode(self, node)

	def format(self, fullname=False):
		_depth = "  "*self.get_depth()

		if fullname:
			_name = self.get_full_name()
		else:
			_name = self.name

		return _depth  + _name


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
	fields = ["date", "fromcategory", "tocategory", "amount", "comment"]
	__slots__ = fields

	def __init__(self, date, fromcategory, tocategory, amount, comment):
		assert(isinstance(fromcategory, CategoryTreeNode))
		assert(isinstance(tocategory, CategoryTreeNode))

		self.date = date
		self.fromcategory = fromcategory
		self.tocategory = tocategory
		self.amount = amount
		self.comment = comment


class NodeSummary(object):
	__slots__ = ["amountin", "amountout", "amount", "sumin", "sumout", "sum"]
	
	def __init__(self):
		self.amountin = 0
		self.amountout = 0
		self.amount = 0
		self.sumin = 0
		self.sumout = 0
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


class DuplicateNodeException(Exception):
	def __init__(self, parentnode, name):
		assert isinstance(parentnode, TreeNode)

		Exception.__init__(self, name)
		self.parentnode = parentnode
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
	def __init__(self, name):
		Exception.__init__(self, name)

		self.name = name


class NoSuchCategoryException(NoSuchNodeException):
	def __init__(self, name):
		NoSuchNodeException.__init__(self, name)


class CategoryIsTopCategoryException(Exception):
	def __init__(self, category):
		assert isinstance(category, CategoryTreeNode)

		Exception.__init__(self, category.name)
		self.category = category
