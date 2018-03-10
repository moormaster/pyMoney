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

	def test_format_indented(self):
		self.categorynameformatter.set_strategy(formatter.CategoryNameFormatter.STRATEGY_NAME)
		self.categorynameformatter.set_indent_with_tree_level(True)

		self.assertEqual(self.categorynameformatter.format(self.category), "Root")
		self.assertEqual(self.categorynameformatter.format(self.childcategory), "  Child")
		self.assertEqual(self.categorynameformatter.format(self.ambigiouscategory1), "    AmbiguousCategory")


class TestTableFormatter(unittest.TestCase):
	def setUp(self):
		self.tableformatter = formatter.TableFormatter()

		self.headerdata = ["Name", "Age", "Body-Size"]
		self.data = []
		self.data.append(["Ann", 25, 165.1234])
		self.data.append(["Marie", 21, 170.334])
		self.data.append(["Peter-Jean-Paul", 35, 185.234])

		self.data = self.data

	def test_format(self):
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertEqual(0, len(list(lines)))

	def test_add_column(self):
		column = self.tableformatter.add_column(0)

		self.assertIsInstance(column, formatter.TableFormatterColumn)
		self.assertEqual("{0:<}", column.get_formatstring())
		self.assertEqual("{0:<}", column.get_headerformatstring())

	def test_format_one_column(self):
		self.tableformatter.add_column(0)
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertListEqual(["Name",
							  "Ann",
							  "Marie",
							  "Peter-Jean-Paul"], list(lines))

	def test_format_integer_column(self):
		self.tableformatter.add_column(1)
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertListEqual(["Age",
							  "25",
							  "21",
							  "35"], list(lines))

	def test_format_float_column(self):
		column = self.tableformatter.add_column(2)
		column.set_precision(2)
		column.set_type("f")
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertListEqual(["Body-Size",
							  "165.12",
							  "170.33",
							  "185.23"], list(lines))

	def test_format_right_aligned_column(self):
		column = self.tableformatter.add_column(0)
		column.set_alignment(">")
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertListEqual(["           Name",
							  "            Ann",
							  "          Marie",
							  "Peter-Jean-Paul"], list(lines))

	def test_format_maxwidth_column(self):
		column = self.tableformatter.add_column(0)
		column.set_maxwidth(10)
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertListEqual(["Name",
							  "Ann",
							  "Marie",
							  "Peter-...l"], list(lines))

	def test_format_table(self):
		self.tableformatter.add_column(0)
		self.tableformatter.add_column(1)
		column = self.tableformatter.add_column(2)
		column.set_precision(2)
		column.set_type("f")
		lines = self.tableformatter.get_formatted_lines(self.headerdata, self.data)

		self.assertListEqual(["Name            Age Body-Size",
							  "Ann             25  165.12",
							  "Marie           21  170.33",
							  "Peter-Jean-Paul 35  185.23"], list(lines))


if __name__ == "__main__":
	unittest.main()
