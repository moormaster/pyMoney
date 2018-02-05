from lib.data import filter
from lib.data import tree


class  MoneyData:
	def __init__(self):
		self.categorytree = CategoryTreeNode("All")
		self.transactions = []

		self.notfoundcategoryname = "NOTFOUND"

	def filter_transactions(self, filter_func):
		return filter.FilterIterator(self.transactions.__iter__(), filter_func)

	def add_transaction(self, str_date, str_fromcategory, str_tocategory, str_amount, str_comment, force=False):
		try:
			self.get_category(str_fromcategory)
			self.get_category(str_tocategory)
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
		from lib.io.parser import TransactionParser
		parser = TransactionParser(self.categorytree, self.notfoundcategoryname, dateformat)
		parser.autocreatenotfoundcategory = autocreatenotfoundcategory

		return parser.parse(str_date, str_categoryin, str_categoryout, str_amount, str_comment)

	def filter_categories(self, filter_func):
		return filter.FilterIterator(self.categorytree.__iter__(), filter_func)

	def get_category(self, name):
		nodes = self.categorytree.find_nodes_by_relative_path(name)

		if len(nodes) == 0:
			raise NoSuchCategoryException(name)

		if len(nodes) > 1:
			raise AmbiguousCategoryNameException(name, list(map(lambda c: c.get_unique_name(), nodes)))

		return nodes[0]

	def get_notfound_category(self):
		try:
			category = self.get_category(self.categorytree.name + "." + self.notfoundcategoryname)
		except NoSuchCategoryException:
			return None

		return category

	def category_is_contained_in_notfound_category(self, category):
		try:
			notfoundcategory = self.get_notfound_category()
		except NoSuchCategoryException:
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

	def create_summary(self, transactionfilter, d_summary = None):
		if d_summary is None:
			d_summary = {}		# resulting map unqique category name -> NodeSummary() object
		d_unique_name = {}		# cached category.get_unique_name() results

		for c in self.categorytree:
			unique_name = c.get_unique_name()
			d_unique_name[id(c)] = unique_name
			if not unique_name in d_summary:
				d_summary[unique_name] = NodeSummary()

		for t in self.transactions:
			if not transactionfilter(t):
				continue

			fromkey = d_unique_name[id(t.fromcategory)]
			tokey = d_unique_name[id(t.tocategory)]

			d_summary[fromkey].amountout -= t.amount
			d_summary[fromkey].amount -= t.amount

			d_summary[tokey].amountin += t.amount
			d_summary[tokey].amount += t.amount

			c = t.fromcategory
			while not c is None:
				key = d_unique_name[id(c)]
				d_summary[key].sumcountout = d_summary[key].sumcountout+1
				d_summary[key].sumcount = d_summary[key].sumcount+1
				d_summary[key].sumout -= t.amount
				d_summary[key].sum -= t.amount
				c = c.parent

			c = t.tocategory
			while not c is None:
				key = d_unique_name[id(c)]
				d_summary[key].sumcountin = d_summary[key].sumcountin+1
				d_summary[key].sumcount = d_summary[key].sumcount+1
				d_summary[key].sumin += t.amount
				d_summary[key].sum += t.amount
				c = c.parent

		return d_summary





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

	def __str__(self):
		return str(self.date) + " " + self.fromcategory.get_unique_name() + " " + self.tocategory.get_unique_name() + " " + str(self.amount) + " " + self.comment

class NodeSummary(object):
	__slots__ = ["amountin", "amountout", "amount", "sumcountin", "sumcountout", "sumcount", "sumin", "sumout", "sum"]
	
	def __init__(self):
		self.amountin = 0
		self.amountout = 0
		self.amount = 0

		self.sumcountin = 0
		self.sumcountout = 0
		self.sumcount = 0

		self.sumin = 0
		self.sumout = 0
		self.sum = 0
	
		pass

class CategoryTreeNode(tree.TreeNode):
	def __init__(self, name):
		tree.TreeNode.__init__(self, name)

	def append_childnode(self, node):
		assert isinstance(node, CategoryTreeNode)

		root_node = self.get_root()

		if node.name == root_node.name:
			raise DuplicateCategoryException(node.name)

		if node.name in self.children:
			raise DuplicateCategoryException(node.name)

		return tree.TreeNode.append_childnode(self, node)

	def format(self, fullname=False):
		_depth = "  "*self.get_depth()

		if fullname:
			_name = self.get_full_name()
		else:
			_name = self.name

		return _depth  + _name


class AmbiguousCategoryNameException(Exception):
	def __init__(self, name, matching_categories):
		Exception.__init__(self, name, matching_categories)

		self.name = name
		self.matching_categories = matching_categories


class DuplicateCategoryException(Exception):
	def __init__(self, name):
		Exception.__init__(self, name)

		self.name = name


class NoSuchCategoryException(tree.NoSuchNodeException):
	def __init__(self, name):
		tree.NoSuchNodeException.__init__(self, name)


class CategoryIsTopCategoryException(Exception):
	def __init__(self, category):
		assert isinstance(category, CategoryTreeNode)

		Exception.__init__(self, category.name)
		self.category = category
