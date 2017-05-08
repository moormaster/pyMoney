from unittest import TestCase
from lib import data

import unittest
import datetime


class TestMoneyData(TestCase):
    def setUp(self):
        self.moneydata = data.MoneyData()

        self.moneydata.add_category("All", "Cash")
        self.moneydata.add_category("Cash", "In")
        self.moneydata.add_category("Cash", "Out")

        self.moneydata.add_category("All", "External")
        self.moneydata.add_category("External", "In")
        self.moneydata.add_category("External", "Out")

        self.moneydata.add_category("External.Out", "Category1")
        self.moneydata.add_category("External.In", "Category2")

        self.moneydata.add_category("Category1", "Subcategory1")
        self.moneydata.add_category("Category2", "Subcategory1")

        self.moneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", "10.0", "")
        self.moneydata.add_transaction("2000-01-02", "Cash.Out", "Category1.Subcategory1", "20.0", "")
        self.moneydata.add_transaction("2000-01-03", "Category2", "Cash.In", "30.0", "")
        self.moneydata.add_transaction("2000-01-04", "Category2.Subcategory1", "Cash.In", "35.0", "")

    def test_filter_transactions(self):
        category = self.moneydata.get_category("Category1")
        filter_func = lambda t: t.fromcategory.is_contained_in_subtree(category) or t.tocategory.is_contained_in_subtree(category)

        l = list(self.moneydata.filter_transactions(filter_func))

        self.assertEqual(len(l), 2)

    def test_add_transaction(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory1",
                               self.moneydata.add_transaction, "2000-01-01", "Cash.Out", "UnknownCategory1", "60.0", "")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory1",
                               self.moneydata.add_transaction, "2000-01-01", "UnknownCategory1", "Cash.In", "60.0", "")

        transactioncount = len(self.moneydata.transactions)
        fromcategory = self.moneydata.get_category("Cash.Out")
        tocategory = self.moneydata.get_category("Category1")

        newtransaction = self.moneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", "40.0", "")

        self.assertEqual(len(self.moneydata.transactions), transactioncount + 1)
        self.assertEqual(newtransaction.fromcategory, fromcategory)
        self.assertEqual(newtransaction.tocategory, tocategory)

        newtransaction = self.moneydata.add_transaction("2000-01-01", "Cash.Out", "UnknownCategory2", "50.0", "", True)
        self.assertEqual(len(self.moneydata.transactions), transactioncount + 2)

        newtransaction = self.moneydata.add_transaction("2000-01-01", "UnknownCategory3", "Cash.In", "50.0", "", True)
        self.assertEqual(len(self.moneydata.transactions), transactioncount + 3)

        newtransaction = self.moneydata.add_transaction("2000-01-01", "UnknownCategory4", "UnknownCategory5", "50.0", "", True)
        self.assertEqual(len(self.moneydata.transactions), transactioncount + 4)

    def test_delete_transaction(self):
        transactioncount = len(self.moneydata.transactions)

        # delete transaction to Subcategory1
        self.moneydata.delete_transaction(1)

        self.assertEqual(len(self.moneydata.transactions), transactioncount - 1)

        category = self.moneydata.get_category("Category1")
        subcategory = self.moneydata.get_category("Category1.Subcategory1")

        filter_func = lambda t: t.fromcategory == category or t.tocategory == category
        self.assertEqual(len(list(self.moneydata.filter_transactions(filter_func))), 1)

        filter_func = lambda t: t.fromcategory == subcategory or t.tocategory == subcategory
        self.assertEqual(len(list(self.moneydata.filter_transactions(filter_func))), 0)

    def test_parse_transaction(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.parse_transaction, "2000-01-01", "Cash.Out", "UnknownCategory", "10.0", "A comment")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.parse_transaction, "2000-01-01", "UnknownCategory", "Cash.In", "10.0", "A comment")

        newtransaction = self.moneydata.parse_transaction("2000-01-01", "Cash.Out", "Category1", "10.0", "A comment")

        self.assertEqual(newtransaction.date, datetime.date(2000, 1, 1))
        self.assertEqual(newtransaction.fromcategory.name, "Out")
        self.assertEqual(newtransaction.tocategory.name, "Category1")
        self.assertEqual(newtransaction.amount, 10.0)
        self.assertEqual(newtransaction.comment, "A comment")

        newtransaction = self.moneydata.parse_transaction("2000-01-01", "Cash.Out", "UnknownCategory1", "10.0", "A comment", True)
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.tocategory))

        newtransaction = self.moneydata.parse_transaction("2000-01-01", "UnknownCategory2", "Cash.In", "10.0", "A comment", True)
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.fromcategory))

        newtransaction = self.moneydata.parse_transaction("2000-01-01", "UnknownCategory3", "UnknownCategory4", "10.0", "A comment", True)
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.fromcategory))
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.tocategory))

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
        self.moneydata.add_category("All", self.moneydata.notfoundcategoryname)
        self.assertIsNotNone(self.moneydata.get_notfound_category())

        self.assertTrue(
            self.moneydata.category_is_contained_in_notfound_category(self.moneydata.get_notfound_category()))

        newcategory = self.moneydata.add_category(self.moneydata.notfoundcategoryname, "NewCategory1")
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newcategory))

    def test_add_category(self):
        # duplicate category names are allowed if they dont share the same dad
        self.moneydata.add_category("Category1", "SubCategory1")
        self.moneydata.add_category("Category2", "SubCategory1")

        self.assertRaisesRegex(data.DuplicateCategoryException, "SubCategory1",
                               self.moneydata.add_category, "Category2", "SubCategory1")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.add_category, "UnknownCategory", "NewCategory1")

        newcategory = self.moneydata.add_category("All", "NewCategory1")
        self.assertEqual(newcategory.name, "NewCategory1")
        self.assertEqual(newcategory.parent.name, "All")

        newcategory = self.moneydata.add_category("Category1", "NewCategory2")
        self.assertEqual(newcategory.name, "NewCategory2")
        self.assertEqual(newcategory.parent.name, "Category1")

        self.moneydata.add_category("All", self.moneydata.notfoundcategoryname)
        self.moneydata.add_category(self.moneydata.notfoundcategoryname, "NewCategory3")
        newcategory3 = self.moneydata.get_category("NewCategory3")
        self.assertEqual(newcategory3.name, "NewCategory3")
        self.assertEqual(newcategory3.parent.name, self.moneydata.notfoundcategoryname)
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

        self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category1.Subcategory1"))
        self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category1"))

    def test_rename_category(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.rename_category, "UnknownCategory", "RenamedUnknownCategory")
        self.assertRaisesRegex(data.DuplicateCategoryException, "In",
                               self.moneydata.rename_category, "External.Out", "In")

        # test renaming to a new category name
        category = self.moneydata.get_category("Category1")
        filter_func_from = lambda t: t.fromcategory == category
        filter_func_to = lambda t: t.tocategory == category
        transactionsfrom = list(self.moneydata.filter_transactions(filter_func_from))
        transactionsto = list(self.moneydata.filter_transactions(filter_func_to))

        self.moneydata.rename_category("Category1", "RenamedCategory")

        self.assertEqual(category.name, "RenamedCategory")
        category = self.moneydata.get_category("RenamedCategory")
        for transaction in transactionsfrom:
            self.assertEqual(transaction.fromcategory, category)
        for transaction in transactionsto:
            self.assertEqual(transaction.tocategory, category)

        # test renaming to an existing unknown subcategory
        self.moneydata.add_transaction("2000-01-05", "Cash.Out", "RenamedNewCategory.RenamedNewSubCategory", 1, "Unknown transaction", True)
        category = self.moneydata.get_category("Category2.Subcategory1")
        renamedsubcategory = self.moneydata.get_category("RenamedNewSubCategory")
        filter_func_from = lambda t: t.fromcategory == renamedsubcategory
        filter_func_to = lambda t: t.tocategory == renamedsubcategory
        transactionsfrom = list(self.moneydata.filter_transactions(filter_func_from))
        transactionsto = list(self.moneydata.filter_transactions(filter_func_to))

        self.moneydata.rename_category("Category2.Subcategory1", "RenamedNewSubCategory")

        
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(renamedsubcategory))
        unknownsubcategory = self.moneydata.get_category("RenamedNewCategory.RenamedNewSubCategory")
        self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknownsubcategory))

        for transaction in transactionsfrom:
            self.assertEqual(transaction.fromcategory, unknownsubcategory)
        for transaction in transactionsto:
            self.assertEqual(transaction.tocategory, unknownsubcategory)

        # test renaming to an existing unknown category
        category = self.moneydata.get_category("Category2")
        newcategory = self.moneydata.get_category("RenamedNewCategory")
        renamedsubcategory = self.moneydata.get_category("RenamedNewCategory.RenamedNewSubCategory")
        filter_func_from = lambda t: t.fromcategory == renamedsubcategory
        filter_func_to = lambda t: t.tocategory == renamedsubcategory
        transactionsfrom = list(self.moneydata.filter_transactions(filter_func_from))
        transactionsto = list(self.moneydata.filter_transactions(filter_func_to))

        self.moneydata.rename_category("Category2", "RenamedNewCategory")
        self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(newcategory))
        self.assertFalse(
            self.moneydata.category_is_contained_in_notfound_category(
                self.moneydata.get_category("RenamedNewCategory")
            )
        )

        for transaction in transactionsfrom:
            self.assertEqual(transaction.fromcategory, renamedsubcategory)
        for transaction in transactionsto:
            self.assertEqual(transaction.tocategory, renamedsubcategory)

    def test_merge_category(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.merge_category, "UnknownCategory", "Category1")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.merge_category, "Category1", "UnknownCategory")

        sourcecategory = self.moneydata.get_category("Category1")
        targetcategory = self.moneydata.get_category("Category2")

        filter_func = lambda t: t.fromcategory.is_contained_in_subtree(targetcategory) or t.tocategory.is_contained_in_subtree(targetcategory)
        transactions = list(self.moneydata.filter_transactions(filter_func))

        self.moneydata.merge_category(sourcecategory.name, targetcategory.name)

        for transaction in transactions:
            self.assertTrue(filter_func(transaction))

    def test_move_category(self):
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.move_category, "UnknownCategory", "Category1")
        self.assertRaisesRegex(data.NoSuchCategoryException, "UnknownCategory",
                               self.moneydata.move_category, "Category1", "UnknownCategory")

    def test_create_summary(self):
        filter_func = lambda t: True
        summary = self.moneydata.create_summary(filter_func)

        self.assertEqual(summary["All"].amountin, 0)
        self.assertEqual(summary["Cash"].amountin, 0)
        self.assertEqual(summary["Cash.In"].amountin, 65)
        self.assertEqual(summary["Cash.Out"].amountin, 0)
        self.assertEqual(summary["External"].amountin, 0)
        self.assertEqual(summary["External.In"].amountin, 0)
        self.assertEqual(summary["Category2"].amountin, 0)
        self.assertEqual(summary["Category2.Subcategory1"].amountin, 0)
        self.assertEqual(summary["External.Out"].amountin, 0)
        self.assertEqual(summary["Category1"].amountin, 10)
        self.assertEqual(summary["Category1.Subcategory1"].amountin, 20)

        self.assertEqual(summary["All"].amountout, 0)
        self.assertEqual(summary["Cash"].amountout, 0)
        self.assertEqual(summary["Cash.In"].amountout, 0)
        self.assertEqual(summary["Cash.Out"].amountout, -30)
        self.assertEqual(summary["External"].amountout, 0)
        self.assertEqual(summary["External.In"].amountout, 0)
        self.assertEqual(summary["Category2"].amountout, -30)
        self.assertEqual(summary["Category2.Subcategory1"].amountout, -35)
        self.assertEqual(summary["External.Out"].amountout, 0)
        self.assertEqual(summary["Category1"].amountout, 0)
        self.assertEqual(summary["Category1.Subcategory1"].amountout, 0)

        self.assertEqual(summary["All"].sumin, 95)
        self.assertEqual(summary["Cash"].sumin, 65)
        self.assertEqual(summary["Cash.In"].sumin, 65)
        self.assertEqual(summary["Cash.Out"].sumin, 0)
        self.assertEqual(summary["External"].sumin, 30)
        self.assertEqual(summary["External.In"].sumin, 0)
        self.assertEqual(summary["Category2"].sumin, 0)
        self.assertEqual(summary["Category2.Subcategory1"].sumin, 0)
        self.assertEqual(summary["External.Out"].sumin, 30)
        self.assertEqual(summary["Category1"].sumin, 30)
        self.assertEqual(summary["Category1.Subcategory1"].sumin, 20)

        self.assertEqual(summary["All"].sumout, -95)
        self.assertEqual(summary["Cash"].sumout, -30)
        self.assertEqual(summary["Cash.In"].sumout, 0)
        self.assertEqual(summary["Cash.Out"].sumout, -30)
        self.assertEqual(summary["External"].sumout, -65)
        self.assertEqual(summary["External.In"].sumout, -65)
        self.assertEqual(summary["Category2"].sumout, -65)
        self.assertEqual(summary["Category2.Subcategory1"].sumout, -35)
        self.assertEqual(summary["External.Out"].sumout, 0)
        self.assertEqual(summary["Category1"].sumout, 0)
        self.assertEqual(summary["Category1.Subcategory1"].sumout, 0)

        for categoryname in summary:
            self.assertEqual(summary[categoryname].amount, summary[categoryname].amountin + summary[categoryname].amountout)
            self.assertEqual(summary[categoryname].sum, summary[categoryname].sumin + summary[categoryname].sumout)

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

        self.assertEqual(self.tree.find_first_node_by_relative_path("Child1"), None)
        self.assertNotEqual(self.tree.find_first_node_by_relative_path("SubChild1"), self.subchildnode1)
        self.assertEqual(self.tree.find_first_node_by_relative_path("Child2"), self.childnode2)

    def test_remove_childnode(self):
        self.assertRaisesRegex(data.NodeIsNotAChildException, "('All', 'NoChild')",
                               self.tree.remove_childnode, data.TreeNode("NoChild"))

        self.tree.remove_childnode(self.childnode1)

        self.assertEqual(self.tree.find_first_node_by_relative_path("Child1"), None)
        self.assertNotEqual(self.tree.find_first_node_by_relative_path("SubChild1"), self.subchildnode1)
        self.assertEqual(self.tree.find_first_node_by_relative_path("Child2"), self.childnode2)

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
        sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
        targetcategory = self.tree.find_first_node_by_relative_path("SubChild1")

        assert isinstance(sourcecategory, data.TreeNode)
        assert isinstance(targetcategory, data.TreeNode)

        self.assertRaisesRegex(data.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child1', 'SubChild1')",
                               targetcategory.move_node, sourcecategory)

        sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
        targetcategory = self.tree.find_first_node_by_relative_path("Child2")

        targetcategory.move_node(sourcecategory)

        self.assertEqual(sourcecategory.parent, targetcategory)

    def test_rename(self):
        self.subchildnode1.rename("renamed")

        self.assertEqual(self.subchildnode1.name, "renamed")
        self.assertEqual(self.tree.find_first_node_by_relative_path("renamed"), self.subchildnode1)

    def test_get_depth(self):
        self.assertEqual(self.tree.get_depth(), 0)
        self.assertEqual(self.childnode1.get_depth(), 1)
        self.assertEqual(self.subchildnode1.get_depth(), 2)

    def test_get_root(self):
        self.assertEqual(self.tree.get_root(), self.tree)
        self.assertEqual(self.childnode1.get_root(), self.tree)
        self.assertEqual(self.subchildnode1.get_root(), self.tree)

    def test_find_first_node_by_relative_path(self):
        node = self.tree.find_first_node_by_relative_path("Child1.SubChild1")
        selfnode = self.subchildnode1.find_first_node_by_relative_path("SubChild1")
        notfoundnode = self.tree.find_first_node_by_relative_path("NoChild")

        self.assertEqual(node, self.subchildnode1)
        self.assertEqual(selfnode, self.subchildnode1)
        self.assertEqual(notfoundnode, None)

    def test_find_nodes_by_relative_path(self):
        nodelist = self.tree.find_nodes_by_relative_path("SubChild1")
        selfnodelist = self.subchildnode1.find_nodes_by_relative_path("SubChild1")
        notfoundnodelist = self.tree.find_nodes_by_relative_path("NoChild")

        self.assertEqual(len(nodelist), 2)
        self.assertEqual(nodelist[0], self.subchildnode1)
        self.assertEqual(nodelist[1], self.subchildnode2)
        self.assertEqual(len(selfnodelist), 1)
        self.assertEqual(selfnodelist[0], self.subchildnode1)
        self.assertEqual(len(notfoundnodelist), 0)

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
        self.tree = data.CategoryTreeNode("All")

    def test_append_childnode(self):
        self.assertRaises(AssertionError, self.tree.append_childnode, data.TreeNode("TreeNode"))
        self.assertRaisesRegex(data.DuplicateCategoryException, "All",
                               self.tree.append_childnode, data.CategoryTreeNode("All"))

        node = self.tree.append_childnode(data.CategoryTreeNode("Child"))

        self.assertTrue(node is not None)

    def test_format(self):
        self.assertEqual(self.tree.format(False), "All")


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.data = []
        self.data.append("A1")
        self.data.append("A2")
        self.data.append("B1")
        self.data.append("B2")

        self.charAFilter = data.Filter(lambda v: v[0] == "A")
        self.num1Filter = data.Filter(lambda v: v[1] == "1")

    def test_filters(self):
        self.assertTrue(self.charAFilter(self.data[0]))
        self.assertTrue(self.charAFilter(self.data[1]))
        self.assertFalse(self.charAFilter(self.data[2]))
        self.assertFalse(self.charAFilter(self.data[3]))

        self.assertTrue(self.num1Filter(self.data[0]))
        self.assertFalse(self.num1Filter(self.data[1]))
        self.assertTrue(self.num1Filter(self.data[2]))
        self.assertFalse(self.num1Filter(self.data[3]))

    def test_or_concat(self):
        transactionfilter = [self.charAFilter.or_concat(self.num1Filter),
                             self.num1Filter.or_concat(self.charAFilter)]

        for f in transactionfilter:
            for d in self.data:
                if self.charAFilter(d) or self.num1Filter(d):
                    self.assertTrue(f(d))
                else:
                    self.assertFalse(f(d))

    def test_and_concat(self):
        transactionfilter = [self.charAFilter.and_concat(self.num1Filter),
                             self.num1Filter.and_concat(self.charAFilter)]

        for f in transactionfilter:
            for d in self.data:
                if self.charAFilter(d) and self.num1Filter(d):
                    self.assertTrue(f(d))
                else:
                    self.assertFalse(f(d))

    def test_negate(self):
        transactionfilter = [self.charAFilter, self.num1Filter]

        for f in transactionfilter:
            nf = f.negate()

            for t in self.data:
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
