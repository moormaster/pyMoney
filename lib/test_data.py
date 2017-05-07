from unittest import TestCase
from lib import data

import unittest
import datetime


class TestMoneyData(TestCase):
    def setUp(self):
        self.moneydata = data.MoneyData()

        self.moneydata.add_category("All", "Category1", "-")
        self.moneydata.add_category("All", "Category2", "+")

        self.moneydata.add_category("Category1", "Subcategory1", "-")
        self.moneydata.add_category("Category2", "Subcategory1", "-")

        self.moneydata.add_transaction("2000-01-01", "Category1", "10.0", "")
        self.moneydata.add_transaction("2000-01-02", "Category1.Subcategory1", "20.0", "")
        self.moneydata.add_transaction("2000-01-03", "Category2", "30.0", "")
        self.moneydata.add_transaction("2000-01-04", "Category2.Subcategory1", "35.0", "")

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

        self.assertEqual(len(self.moneydata.transactions), transactioncount + 2)
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.category))

    def test_delete_transaction(self):
        transactioncount = len(self.moneydata.transactions)

        # delete transaction in Subcategory1
        self.moneydata.delete_transaction(1)

        self.assertEqual(len(self.moneydata.transactions), transactioncount - 1)

        category = self.moneydata.get_category("Category1")
        subcategory = self.moneydata.get_category("Category1.Subcategory1")

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
                               self.moneydata.get_category, "UnknownCategory")

        existingcategory = self.moneydata.get_category("Category1")
        self.assertEqual(existingcategory.name, "Category1")

    def test_category_is_contained_in_notfound_category(self):
        self.assertIsNone(self.moneydata.get_notfound_category())

        self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_category("All")))
        self.assertFalse(
            self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_category("Category1")))
        self.assertFalse(
            self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_category("Category2")))

        self.assertIsNone(self.moneydata.get_notfound_category())
        self.moneydata.add_category("All", self.moneydata.notfoundcategoryname, "+")
        self.assertIsNotNone(self.moneydata.get_notfound_category())

        self.assertTrue(
            self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_notfound_category()))

        newcategory = self.moneydata.add_category(self.moneydata.notfoundcategoryname, "NewCategory1", "+")
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newcategory))

    def test_add_category(self):
        # duplicate category names are allowed if they dont share the same dad
        self.moneydata.add_category("Category1", "SubCategory1", "+")
        self.moneydata.add_category("Category2", "SubCategory1", "+")

        self.assertRaisesRegex(data.DuplicateCategoryException, "SubCategory1",
                               self.moneydata.add_category, "Category2", "SubCategory1", "+")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.add_category, "UnknownCategory", "NewCategory1", "+")

        newcategory = self.moneydata.add_category("All", "NewCategory1", "+")
        self.assertEqual(newcategory.name, "NewCategory1")
        self.assertEqual(newcategory.parent.name, "All")

        newcategory = self.moneydata.add_category("Category1", "NewCategory2", "+")
        self.assertEqual(newcategory.name, "NewCategory2")
        self.assertEqual(newcategory.parent.name, "Category1")

        self.moneydata.add_category("All", self.moneydata.notfoundcategoryname, "+")
        self.moneydata.add_category(self.moneydata.notfoundcategoryname, "NewCategory3", "+")
        newcategory3 = self.moneydata.get_category("NewCategory3")
        self.assertEqual(newcategory3.name, "NewCategory3")
        self.assertEqual(newcategory3.parent.name, self.moneydata.notfoundcategoryname)
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newcategory3))

        newcategory = self.moneydata.add_category("All", "NewCategory3", "+")
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

        self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category1.Subcategory1"))
        self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category1"))

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

        self.moneydata.add_category("All", self.moneydata.notfoundcategoryname, "+")
        newcategory = self.moneydata.add_category(self.moneydata.notfoundcategoryname, "RenamedNewCategory", "+")

        self.moneydata.rename_category("Category2", "RenamedNewCategory")
        self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(newcategory))
        self.assertFalse(
            self.moneydata.category_is_contained_in_notfound_category(
                self.moneydata.get_category("RenamedNewCategory")
            )
        )

    def test_setsign_of_category(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.setsign_of_category, "UnknownCategory", "-")
        self.assertRaisesRegex(data.InvalidSignException, "-1",
                               self.moneydata.setsign_of_category, "Category1", "-1")

        category = self.moneydata.get_category("Category2")

        self.moneydata.setsign_of_category("Category2", "-")
        self.assertEqual(category.sign.value, -1)

        self.moneydata.setsign_of_category("Category2", "+")
        self.assertEqual(category.sign.value, 1)

        self.moneydata.setsign_of_category("Category2", "0")
        self.assertEqual(category.sign.value, 0)

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
            self.assertTrue(transaction.category.is_contained_in_subtree(targetcategory))

    def test_move_category(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.move_category, "UnknownCategory", "Category1")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.move_category, "Category1", "UnknownCategory")

    def test_create_summary(self):
        filter_func = lambda t: True
        summary = self.moneydata.create_summary(filter_func)

        self.assertEqual(summary["All"].amount, 0)
        self.assertEqual(summary["Category1"].amount, -10)
        self.assertEqual(summary["Category1.Subcategory1"].amount, -20)
        self.assertEqual(summary["Category2"].amount, 30)
        self.assertEqual(summary["Category2.Subcategory1"].amount, -35)

        self.assertEqual(summary["All"].sum, 5)
        self.assertEqual(summary["Category1"].sum, 10)
        self.assertEqual(summary["Category1.Subcategory1"].sum, 20)
        self.assertEqual(summary["Category2"].sum, -5)
        self.assertEqual(summary["Category2.Subcategory1"].sum, -35)


class TestTreeNode(unittest.TestCase):
    def setUp(self):
        self.tree = data.TreeNode("All")

        self.childnode1 = data.TreeNode("Child1")
        self.childnode2 = data.TreeNode("Child2")
        self.subchildnode1 = data.TreeNode("SubChild1")
        self.subchildnode2 = data.TreeNode("SubChild1")

        self.tree.append_childnode(self.childnode1)
        self.tree.append_childnode(self.childnode2)

        self.childnode1.append_childnode(self.subchildnode1)
        self.childnode2.append_childnode(self.subchildnode2)

    def test___iter__(self):
        l = list(self.tree)
        lcomp1 = [self.tree,
                  self.childnode1,
                  self.subchildnode1,
                  self.childnode2,
                  self.subchildnode2]

        lcomp2 = [self.tree,
                  self.childnode2,
                  self.subchildnode2,
                  self.childnode1,
                  self.subchildnode1]

        self.assertTrue(l == lcomp1 or l == lcomp2)

    def test_format(self):
        self.assertRegex(self.tree.format(), "[\t]{0}[^\t]*")
        self.assertRegex(self.childnode1.format(), "[\t]{1}[^\t]*")
        self.assertRegex(self.childnode2.format(), "[\t]{1}[^\t]*")
        self.assertRegex(self.subchildnode1.format(), "[\t]{2}[^\t]*")

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
        self.assertNotEqual(self.tree.find_first_node("SubChild1"), self.subchildnode1)
        self.assertEqual(self.tree.find_first_node("Child2"), self.childnode2)

    def test_remove_childnode(self):
        self.assertRaisesRegex(data.NodeIsNotAChildException, "('All', 'NoChild')",
                               self.tree.remove_childnode, data.TreeNode("NoChild"))

        self.tree.remove_childnode(self.childnode1)

        self.assertEqual(self.tree.find_first_node("Child1"), None)
        self.assertNotEqual(self.tree.find_first_node("SubChild1"), self.subchildnode1)
        self.assertEqual(self.tree.find_first_node("Child2"), self.childnode2)

    def test_merge(self):
        sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
        targetcategory = self.tree.find_first_node_by_relative_path("Child1.SubChild1")

        assert isinstance(sourcecategory, data.TreeNode)
        assert isinstance(targetcategory, data.TreeNode)

        self.assertRaisesRegex(data.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child1', 'SubChild1')",
                               targetcategory.merge_node, sourcecategory)

        sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
        targetcategory = self.tree.find_first_node_by_relative_path("Child2")

        subcategories = targetcategory.children

        targetcategory.merge_node(sourcecategory)

        self.assertEqual(len(subcategories), 1)
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
        self.subchildnode1.rename("renamed")

        self.assertEqual(self.subchildnode1.name, "renamed")
        self.assertEqual(self.tree.find_first_node("renamed"), self.subchildnode1)

    def test_get_depth(self):
        self.assertEqual(self.tree.get_depth(), 0)
        self.assertEqual(self.childnode1.get_depth(), 1)
        self.assertEqual(self.subchildnode1.get_depth(), 2)

    def test_get_root(self):
        self.assertEqual(self.tree.get_root(), self.tree)
        self.assertEqual(self.childnode1.get_root(), self.tree)
        self.assertEqual(self.subchildnode1.get_root(), self.tree)

    def test_find_first_node(self):
        node = self.tree.find_first_node("SubChild1")
        selfnode = self.subchildnode1.find_first_node("SubChild1")
        notfoundnode = self.tree.find_first_node("NoChild")

        self.assertEqual(node, self.subchildnode1)
        self.assertEqual(selfnode, self.subchildnode1)
        self.assertEqual(notfoundnode, None)

    def test_find_nodes(self):
        anode1 = self.tree.append_childnode(data.TreeNode("ANode"))
        anode2 = self.subchildnode1.append_childnode(data.TreeNode("ANode"))

        l = self.tree.find_nodes("ANode")

        self.assertEqual(set(l), {anode1, anode2})

    def test_get_full_name(self):
        self.assertEqual(self.subchildnode1.get_full_name(), "All.Child1.SubChild1")

    def test_is_contained_in_subtree(self):
        self.assertTrue(self.subchildnode1.is_contained_in_subtree(self.subchildnode1))

        self.assertTrue(self.subchildnode1.is_contained_in_subtree(self.childnode1))
        self.assertFalse(self.subchildnode1.is_contained_in_subtree(self.childnode2))

        self.assertTrue(self.childnode1.is_contained_in_subtree(self.tree))

    def test_is_root_of(self):
        self.assertTrue(self.tree.is_root_of(self.childnode1))
        self.assertTrue(self.tree.is_root_of(self.subchildnode1))

        self.assertTrue(self.childnode1.is_root_of(self.subchildnode1))
        self.assertFalse(self.childnode2.is_root_of(self.subchildnode1))

        self.assertFalse(self.childnode1.is_root_of(self.childnode2))
        self.assertFalse(self.childnode2.is_root_of(self.childnode1))


class TestCategoryTreeNode(unittest.TestCase):
    def setUp(self):
        self.tree = data.CategoryTreeNode("All", 1)

    def test_append_childnode(self):
        self.assertRaises(AssertionError, self.tree.append_childnode, data.TreeNode("TreeNode"))
        self.assertRaisesRegex(data.DuplicateCategoryException, "All",
                               self.tree.append_childnode, data.CategoryTreeNode("All", 1))

        node = self.tree.append_childnode(data.CategoryTreeNode("Child", 1))

        self.assertTrue(node is not None)


class TestSign(unittest.TestCase):
    def test_parse(self):
        self.assertRaisesRegex(data.InvalidSignException, "-1",
                               data.Sign.parse, "-1")

        pos = data.Sign.parse("+")
        neg = data.Sign.parse("-")
        zero = data.Sign.parse("0")

        self.assertEqual(pos.value, 1)
        self.assertEqual(neg.value, -1)
        self.assertEqual(zero.value, 0)


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.category1 = data.CategoryTreeNode("Category1", data.Sign(1))
        self.category2 = data.CategoryTreeNode("Category1", data.Sign(0))

        self.transaction1 = data.Transaction(datetime.date(2000, 1, 1), self.category1, 100.0, None)
        self.transaction2 = data.Transaction(datetime.date(2000, 12, 1), self.category1, 100.0, None)
        self.transaction3 = data.Transaction(datetime.date(2000, 1, 1), self.category2, 100.0, None)
        self.transaction4 = data.Transaction(datetime.date(2000, 12, 1), self.category2, 100.0, None)

        self.transactions = [self.transaction1, self.transaction2, self.transaction3, self.transaction4]

        self.datefilter = data.Filter(lambda t: t.date.month > 8)
        self.categoryfilter = data.Filter(lambda t: t.category == self.category1)

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
