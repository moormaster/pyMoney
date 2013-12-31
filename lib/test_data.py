from unittest import TestCase
from lib import data

import unittest
import datetime


class TestMoneyData(TestCase):
	def setUp(self):
		self.moneydata = data.MoneyData()

		self.moneydata.add_category("All", "Category1")
		self.moneydata.add_category("All", "Category2")

		self.moneydata.add_category("Category1", "Subcategory1")

		self.moneydata.add_transaction("2000-01-01", "Category1", "10.0", "")
		self.moneydata.add_transaction("2000-01-02", "Subcategory1", "20.0", "")
		self.moneydata.add_transaction("2000-01-03", "Category2", "30.0", "")

	def test_filter_transactions(self):
		category = self.moneydata.get_category("Category1")
		filter_func = lambda t: t.category.is_contained_in_subtree(category)

		l = list(self.moneydata.filter_transactions(filter_func))

		self.assertEqual(len(l), 2)

	def test_add_transaction(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory1",
			self.moneydata.add_transaction, "2000-01-01", "UnknownCategory1", "60.0", "")

		transactioncount = len(self.moneydata.transactions)
		category = self.moneydata.get_category("Category1")

		newtransaction = self.moneydata.add_transaction("2000-01-01", "Category1", "40.0", "")

		self.assertEqual(len(self.moneydata.transactions), transactioncount + 1)
		self.assertEqual(newtransaction.category, category)

		newtransaction = self.moneydata.add_transaction("2000-01-01", "UnknownCategory2", "50.0", "", True)

		self.assertEquals(len(self.moneydata.transactions), transactioncount + 2)
		self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.category))

	def test_delete_transaction(self):
		transactioncount = len(self.moneydata.transactions)

		# delete transaction in Subcategory1
		self.moneydata.delete_transaction(1)

		self.assertEqual(len(self.moneydata.transactions), transactioncount - 1)

		category = self.moneydata.get_category("Category1")
		subcategory = self.moneydata.get_category("Subcategory1")

		filter_func = lambda t: t.category == category
		self.assertEqual(len(list(self.moneydata.filter_transactions(filter_func))), 1)

		filter_func = lambda t: t.category == subcategory
		self.assertEqual(len(list(self.moneydata.filter_transactions(filter_func))), 0)

	def test_parse_transaction(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.parse_transaction, "2000-01-01", "UnknownCategory", "10.0", "A comment")

		newtransaction = self.moneydata.parse_transaction("2000-01-01", "Category1", "10.0", "A comment")

		self.assertEqual(newtransaction.date, datetime.date(2000, 1, 1))
		self.assertEqual(newtransaction.category.name, "Category1")
		self.assertEqual(newtransaction.amount, 10.0)
		self.assertEqual(newtransaction.comment, "A comment")

		newtransaction = self.moneydata.parse_transaction("2000-01-01", "UnknownCategory", "10.0", "A comment", True)

		self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.category))

	def test_get_category(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.get_category, "UnknownCategory", False)

		existingcategory = self.moneydata.get_category("Category1")
		self.assertEqual(existingcategory.name, "Category1")

		notexistingcategory = self.moneydata.get_category("UnknownCategory", True)
		self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(notexistingcategory))

	def test_category_is_contained_in_notfound_category(self):
		self.assertIsNone(self.moneydata.get_notfound_category())

		self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_category("All")))
		self.assertFalse(
			self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_category("Category1")))
		self.assertFalse(
			self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_category("Category2")))

		self.assertIsNotNone(self.moneydata.get_notfound_category(autocreate=True))
		self.assertIsNotNone(self.moneydata.get_notfound_category())

		self.assertTrue(
			self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_notfound_category()))

		newcategory = self.moneydata.add_category("NOTFOUND", "NewCategory1")
		self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newcategory))

	def test_add_category(self):
		self.assertRaisesRegex(data.DuplicateCategoryException, "Category1",
			self.moneydata.add_category, "Category2", "Category1")
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.add_category, "UnknownCategory", "NewCategory1")

		newcategory = self.moneydata.add_category("All", "NewCategory1")
		self.assertEqual(newcategory.name, "NewCategory1")
		self.assertEqual(newcategory.parent.name, "All")

		newcategory = self.moneydata.add_category("Category1", "NewCategory2")
		self.assertEqual(newcategory.name, "NewCategory2")
		self.assertEqual(newcategory.parent.name, "Category1")

		self.moneydata.get_notfound_category(autocreate=True)
		self.moneydata.add_category("NOTFOUND", "NewCategory3")
		newcategory3 = self.moneydata.get_category("NewCategory3")
		self.assertEqual(newcategory3.name, "NewCategory3")
		self.assertEqual(newcategory3.parent.name, "NOTFOUND")
		self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newcategory3))

		newcategory = self.moneydata.add_category("All", "NewCategory3")
		self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(newcategory3))
		self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(newcategory))
		self.assertEqual(newcategory.name, "NewCategory3")
		self.assertEqual(newcategory.parent.name, "All")

	def test_delete_category(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.delete_category, "UnknownCategory")
		self.assertRaisesRegex(data.CategoryIsTopCategoryException, "All",
			self.moneydata.delete_category, "All")

		self.moneydata.delete_category("Category1")

		self.assertFalse(self.moneydata.categorytree.find_first_node("Subcategory1"))
		self.assertFalse(self.moneydata.categorytree.find_first_node("Category1"))

	def test_rename_category(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.rename_category, "UnknownCategory", "RenamedUnknownCategory")
		self.assertRaisesRegex(data.DuplicateCategoryException, "Category2",
			self.moneydata.rename_category, "Category1", "Category2")

		filter_func = lambda t: t.category.name == "Category1"
		transactions = self.moneydata.filter_transactions(filter_func)
		category = self.moneydata.get_category("Category1")

		self.moneydata.rename_category("Category1", "RenamedCategory")

		self.assertEqual(category.name, "RenamedCategory")
		for transaction in transactions:
			self.assertEqual(transaction.category, category)

		self.moneydata.get_notfound_category(autocreate=True)
		newcategory = self.moneydata.add_category("NOTFOUND", "RenamedNewCategory")

		self.moneydata.rename_category("Category2", "RenamedNewCategory")
		self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(newcategory))
		self.assertFalse(
			self.moneydata.category_is_contained_in_notfound_category(
				self.moneydata.get_category("RenamedNewCategory")
			)
		)

	def test_merge_category(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.merge_category, "UnknownCategory", "Category1")
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.merge_category, "Category1", "UnknownCategory")

		sourcecategory = self.moneydata.get_category("Category1")
		targetcategory = self.moneydata.get_category("Category2")

		filter_func = lambda t: t.category.is_contained_in_subtree(targetcategory)
		transactions = list(self.moneydata.filter_transactions(filter_func))

		self.moneydata.merge_category(sourcecategory.name, targetcategory.name)

		for transaction in transactions:
			self.assertEqual(transaction.category, targetcategory)

	def test_move_category(self):
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.move_category, "UnknownCategory", "Category1")
		self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
			self.moneydata.move_category, "Category1", "UnknownCategory")

	def test_create_summary(self):
		filter_func = lambda t: True
		summary = self.moneydata.create_summary(filter_func)

		self.assertEqual(summary["All"].amount, 0)
		self.assertEqual(summary["Category1"].amount, 10)
		self.assertEqual(summary["Subcategory1"].amount, 20)
		self.assertEqual(summary["Category2"].amount, 30)

		self.assertEqual(summary["All"].sum, 60)
		self.assertEqual(summary["Category1"].sum, 30)
		self.assertEqual(summary["Subcategory1"].sum, 20)
		self.assertEqual(summary["Category2"].sum, 30)


class TestTreeNode(unittest.TestCase):
	def setUp(self):
		self.tree = data.TreeNode("All")

		self.childnode1 = data.TreeNode("Child1")
		self.childnode2 = data.TreeNode("Child2")
		self.subchildnode = data.TreeNode("SubChild1")

		self.tree.append_childnode(self.childnode1)
		self.tree.append_childnode(self.childnode2)

		self.childnode1.append_childnode(self.subchildnode)

	def test___iter__(self):
		l = list(self.tree)
		lcomp1 = [self.tree,
			self.childnode1,
			self.subchildnode,
			self.childnode2]

		lcomp2 = [self.tree,
			self.childnode2,
			self.childnode1,
			self.subchildnode]

		self.assertTrue(l == lcomp1 or l == lcomp2)

	def test_format(self):
		self.assertRegex(self.tree.format(), "[\t]*\+ .*")
		self.assertRegex(self.childnode1.format(), "[\t]*\+ .*")
		self.assertRegex(self.childnode2.format(), "[\t]*\- .*")
		self.assertRegex(self.subchildnode.format(), "[\t]*- .*")

	def test_append_childnode(self):
		self.assertRaises(AssertionError, self.tree.append_childnode, object())

		node = self.tree.append_childnode(data.TreeNode("Child"))

		self.assertTrue(node is not None)
		self.assertEqual(node.parent, self.tree)

		subnode = node.append_childnode(data.TreeNode("SubChild"))

		self.assertTrue(subnode is not None)
		self.assertEqual(subnode.parent, node)

	def test_remove_childnode_by_name(self):
		self.assertRaisesRegex(data.NoSuchNodeException, "NoChild", self.tree.remove_childnode_by_name, "NoChild")

		self.tree.remove_childnode_by_name("Child1")

		self.assertEqual(self.tree.find_first_node("Child1"), None)
		self.assertEqual(self.tree.find_first_node("SubChild1"), None)
		self.assertEqual(self.tree.find_first_node("Child2"), self.childnode2)

	def test_remove_childnode(self):
		self.assertRaisesRegex(data.NodeIsNotAChildException, "('All', 'NoChild')",
			self.tree.remove_childnode, data.TreeNode("NoChild"))

		self.tree.remove_childnode(self.childnode1)

		self.assertEqual(self.tree.find_first_node("Child1"), None)
		self.assertEqual(self.tree.find_first_node("SubChild1"), None)
		self.assertEqual(self.tree.find_first_node("Child2"), self.childnode2)

	def test_merge(self):
		sourcecategory = self.tree.find_first_node("Child1")
		targetcategory = self.tree.find_first_node("SubChild1")

		assert isinstance(sourcecategory, data.TreeNode)
		assert isinstance(targetcategory, data.TreeNode)

		self.assertRaisesRegex(data.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child1', 'SubChild1')",
			targetcategory.merge_node, sourcecategory)

		sourcecategory = self.tree.find_first_node("Child1")
		targetcategory = self.tree.find_first_node("Child2")

		subcategories = sourcecategory.children

		targetcategory.merge_node(sourcecategory)

		for category in subcategories:
			self.assertEqual(subcategories[category].parent, targetcategory)

	def test_move(self):
		sourcecategory = self.tree.find_first_node("Child1")
		targetcategory = self.tree.find_first_node("SubChild1")

		assert isinstance(sourcecategory, data.TreeNode)
		assert isinstance(targetcategory, data.TreeNode)

		self.assertRaisesRegex(data.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child1', 'SubChild1')",
			targetcategory.move_node, sourcecategory)

		sourcecategory = self.tree.find_first_node("Child1")
		targetcategory = self.tree.find_first_node("Child2")

		targetcategory.move_node(sourcecategory)

		self.assertEqual(sourcecategory.parent, targetcategory)

	def test_rename(self):
		self.subchildnode.rename("renamed")

		self.assertEqual(self.subchildnode.name, "renamed")
		self.assertEqual(self.tree.find_first_node("renamed"), self.subchildnode)

	def test_get_depth(self):
		self.assertEqual(self.tree.get_depth(), 0)
		self.assertEqual(self.childnode1.get_depth(), 1)
		self.assertEqual(self.subchildnode.get_depth(), 2)

	def test_get_root(self):
		self.assertEqual(self.tree.get_root(), self.tree)
		self.assertEqual(self.childnode1.get_root(), self.tree)
		self.assertEqual(self.subchildnode.get_root(), self.tree)

	def test_find_first_node(self):
		node = self.tree.find_first_node("SubChild1")
		selfnode = self.subchildnode.find_first_node("SubChild1")
		notfoundnode = self.tree.find_first_node("NoChild")

		self.assertEqual(node, self.subchildnode)
		self.assertEqual(selfnode, self.subchildnode)
		self.assertEqual(notfoundnode, None)

	def test_find_nodes(self):
		anode1 = self.tree.append_childnode(data.TreeNode("ANode"))
		anode2 = self.subchildnode.append_childnode(data.TreeNode("ANode"))

		l = self.tree.find_nodes("ANode")

		self.assertEqual(set(l), {anode1, anode2})

	def test_get_full_name(self):
		self.assertEqual(self.subchildnode.get_full_name(), "All.Child1.SubChild1")

	def test_is_contained_in_subtree(self):
		self.assertTrue(self.subchildnode.is_contained_in_subtree(self.subchildnode))

		self.assertTrue(self.subchildnode.is_contained_in_subtree(self.childnode1))
		self.assertFalse(self.subchildnode.is_contained_in_subtree(self.childnode2))

		self.assertTrue(self.childnode1.is_contained_in_subtree(self.tree))

	def test_is_root_of(self):
		self.assertTrue(self.tree.is_root_of(self.childnode1))
		self.assertTrue(self.tree.is_root_of(self.subchildnode))

		self.assertTrue(self.childnode1.is_root_of(self.subchildnode))
		self.assertFalse(self.childnode2.is_root_of(self.subchildnode))

		self.assertFalse(self.childnode1.is_root_of(self.childnode2))
		self.assertFalse(self.childnode2.is_root_of(self.childnode1))


class TestCategoryTreeNode(unittest.TestCase):
	def setUp(self):
		self.tree = data.CategoryTreeNode("All")

	def test_append_childnode(self):
		self.assertRaises(AssertionError, self.tree.append_childnode, data.TreeNode("TreeNode"))
		self.assertRaisesRegex(data.DuplicateCategoryException, "All",
			self.tree.append_childnode, data.CategoryTreeNode("All"))

		node = self.tree.append_childnode(data.CategoryTreeNode("Child"))

		self.assertTrue(node is not None)


class TestFilter(unittest.TestCase):
	def setUp(self):
		self.transaction1 = data.Transaction(datetime.date(2000, 1, 1), "Category1", 100.0, None)
		self.transaction2 = data.Transaction(datetime.date(2000, 12, 1), "Category1", 100.0, None)
		self.transaction3 = data.Transaction(datetime.date(2000, 1, 1), "Category2", 100.0, None)
		self.transaction4 = data.Transaction(datetime.date(2000, 12, 1), "Category2", 100.0, None)

		self.transactions = [self.transaction1, self.transaction2, self.transaction3, self.transaction4]

		self.datefilter = data.Filter(lambda t: t.date.month > 8)
		self.categoryfilter = data.Filter(lambda t: t.category == "Category1")

	def test_filters(self):
		self.assertFalse(self.datefilter(self.transaction1))
		self.assertTrue(self.datefilter(self.transaction2))
		self.assertFalse(self.datefilter(self.transaction3))
		self.assertTrue(self.datefilter(self.transaction4))

		self.assertTrue(self.categoryfilter(self.transaction1))
		self.assertTrue(self.categoryfilter(self.transaction2))
		self.assertFalse(self.categoryfilter(self.transaction3))
		self.assertFalse(self.categoryfilter(self.transaction4))

	def test_or_concat(self):
		transactionfilter = [self.datefilter.or_concat(self.categoryfilter),
			self.categoryfilter.or_concat(self.datefilter)]

		for f in transactionfilter:
			for t in self.transactions:
				if self.datefilter(t) or self.categoryfilter(t):
					self.assertTrue(f(t))
				else:
					self.assertFalse(f(t))

	def test_and_concat(self):
		transactionfilter = [self.datefilter.and_concat(self.categoryfilter),
			self.categoryfilter.and_concat(self.datefilter)]

		for f in transactionfilter:
			for t in self.transactions:
				if self.datefilter(t) and self.categoryfilter(t):
					self.assertTrue(f(t))
				else:
					self.assertFalse(f(t))

	def test_negate(self):
		transactionfilter = [self.datefilter, self.categoryfilter]
		transactions = [self.transaction1, self.transaction2, self.transaction3, self.transaction4]

		for f in transactionfilter:
			nf = f.negate()

			for t in transactions:
				if not f(t):
					self.assertTrue(nf(t))
				else:
					self.assertFalse(nf(t))


class TestFilterIterator(unittest.TestCase):
	def setUp(self):
		self.list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

	def test_filteriterator(self):
		filter_func = lambda n: n > 5
		filteriter = data.FilterIterator(self.list.__iter__(), filter_func)

		l = list(filteriter)

		self.assertEqual(l, [6, 7, 8, 9, 10])


if __name__ == '__main__':
	unittest.main()
