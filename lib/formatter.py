import lib.data
import lib.data.moneydata
import lib.io
import lib.io.parser
import lib.io.Categories
import lib.io.Transactions


class CategoryNameFormatter:
	STRATEGY_NAME = 0
	STRATEGY_UNIQUE_NAME = 1
	STRATEGY_FULL_NAME = 2

	def __init__(self):
		self.d_namecache = {}
		self.strategy = self.STRATEGY_UNIQUE_NAME
		self.maxLength = None
		self.indentWithTreeLevel = False

		pass


	def set_strategy(self, strategy):
		if not strategy in [self.STRATEGY_NAME, self.STRATEGY_UNIQUE_NAME, self.STRATEGY_FULL_NAME]:
			raise "invalid strategy: " + str(strategy)

		if self.strategy != strategy:
			self.d_namecache = {}

		self.strategy = strategy


	def set_indent_with_tree_level(self, flag):
		if not flag:
			self.indentWithTreeLevel = False
		else:
			self.indentWithTreeLevel = True


	def set_maxlength(self, length):
		assert isinstance(length, int)

		if not length:
			self.maxLength = None
		else:
			self.maxLength = length


	def get_trimmed_value(self, string):
		if not self.maxLength:
			return string

		if len(string) < self.maxLength:
			return string

		return string[0:self.maxLength-4] + "..." + string[-1]


	def format(self, category):
		assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

		if not id(category) in self.d_namecache:
			if self.strategy == self.STRATEGY_NAME:
				self.d_namecache[id(category)] = category.name
			elif self.strategy == self.STRATEGY_UNIQUE_NAME:
				self.d_namecache[id(category)] = category.get_unique_name()
			else:
				self.d_namecache[id(category)] = category.get_full_name()

		formattedvalue = self.d_namecache[id(category)]
		if self.indentWithTreeLevel:
			formattedvalue = "  "*category.get_depth() + formattedvalue
		formattedvalue = self.get_trimmed_value(formattedvalue)

		return formattedvalue


