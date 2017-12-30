from lib import formatter
from lib.data import moneydata

import unittest


class TestCategoryNameFormatter(unittest.TestCase):
	def setUp(self):
		self.category = moneydata.CategoryTreeNode("Root")
		self.childcategory = moneydata.CategoryTreeNode("Child")
		self.longnamechildcategory = moneydata.CategoryTreeNode("LongnameChild")
		self.ambigiouscategory1 = moneydata.CategoryTreeNode("AmbiguousCategory")
		self.ambigiouscategory2 = moneydata.CategoryTreeNode("AmbiguousCategory")

		self.category.append_childnode(self.childcategory)
		self.childcategory.append_childnode(self.ambigiouscategory1)

		self.category.append_childnode(self.longnamechildcategory)
		self.longnamechildcategory.append_childnode(self.ambigiouscategory2)

		self.categorynameformatter = formatter.CategoryNameFormatter()

	def test_format_unique_name(self):
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "Child.AmbiguousCategory")

	def test_format_name(self):
		self.categorynameformatter.set_strategy(formatter.CategoryNameFormatter.STRATEGY_NAME)
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "AmbiguousCategory")

	def test_format_fullname(self):
		self.categorynameformatter.set_strategy(formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "Root.Child.AmbiguousCategory")

	def test_format_maxlength(self):
		self.categorynameformatter.set_maxlength(22)
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "Child.AmbiguousCat...y")

	def test_format_indented(self):
		self.categorynameformatter.set_strategy(formatter.CategoryNameFormatter.STRATEGY_NAME)
		self.categorynameformatter.set_indent_with_tree_level(True)

		self.assertEqual(self.categorynameformatter.format(self.category), "Root")
		self.assertEqual(self.categorynameformatter.format(self.childcategory), "  Child")
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "    AmbiguousCategory")

	def test_format_indented_maxlength(self):
		self.categorynameformatter.set_strategy(formatter.CategoryNameFormatter.STRATEGY_NAME)
		self.categorynameformatter.set_maxlength(20)
		self.categorynameformatter.set_indent_with_tree_level(True)

		self.assertEqual(self.categorynameformatter.format(self.category), "Root")
		self.assertEqual(self.categorynameformatter.format(self.childcategory), "  Child")
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "    AmbiguousCat...y")


if __name__ == "__main__":
	unittest.main()
