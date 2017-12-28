import lib.data
import lib.data.moneydata
import lib.io
import lib.io.parser

import unittest


class TestTransactionParser(unittest.TestCase):
	def setUp(self):
		self.categorytree = lib.data.moneydata.CategoryTreeNode("All")
		self.parser = lib.io.parser.TransactionParser(self.categorytree, "NOTFOUND")

		self.categorytree.append_childnode(lib.data.moneydata.CategoryTreeNode("Category1"))

	def test_get_category_unkown_category(self):
		self.parser.autocreatenotfoundcategory = False
		self.assertRaisesRegex(lib.data.moneydata.NoSuchCategoryException, "UnknownCategory",
			self.parser.get_category, "UnknownCategory")

	def test_get_category(self):
		existingcategory = self.parser.get_category("Category1")
		self.assertEqual(existingcategory.name, "Category1")

		notexistingcategory = self.parser.get_category("UnknownCategory")
		notfoundcategory = self.parser.get_notfound_category(autocreate=True)
		self.assertTrue(notexistingcategory.is_contained_in_subtree(notfoundcategory))

	def test_get_notfound_category(self):
		self.assertIsNone(self.parser.get_notfound_category())
		self.assertIsNotNone(self.parser.get_notfound_category(True))

		notfoundcategory = self.parser.get_notfound_category()
		newcategory = notfoundcategory.append_childnode(lib.data.moneydata.CategoryTreeNode("NewCategory1"))
		self.assertTrue(newcategory.is_contained_in_subtree(notfoundcategory))

if __name__ == "__main__":
	unittest.main()