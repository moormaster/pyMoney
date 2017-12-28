from lib import data
from lib import io

import unittest


class TestTransactionParser:
	def setUp(self):
		self.categorytree = data.CategoryTreeNode("All", 1)
		self.parser = io.TransactionParser(self.categorytree, "NOTFOUND")

		self.categorytree.append_childnode("Category1")

	def test_get_category(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
							   self.parser.get_category, "UnknownCategory", False)

		existingcategory = self.parser.get_category("Category1")
		self.assertEqual(existingcategory.name, "Category1")

		notexistingcategory = self.parser.get_category("UnknownCategory", True)
		notfoundcategory = self.parser.get_notfound_category()
		self.assertTrue(notexistingcategory.is_contained_in_subtree(notfoundcategory))

	def test_get_notfound_category(self):
		self.assertIsNone(self.parser.get_notfound_category())
		self.assertIsNotNone(self.parser.get_notfound_category(True))

		notfoundcategory = self.parser.get_notfound_category()
		newcategory = self.categorytree.add_category("NOTFOUND", "NewCategory1")
		self.assertTrue(newcategory.is_contained_in_subtree(notfoundcategory))

if __name__ == "__main__":
	unittest.main()