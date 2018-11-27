# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import moneydata
from lib.data import tree

import unittest
import datetime


class TestCategoryTreeNode(unittest.TestCase):
        def setUp(self):
                self.tree = moneydata.CategoryTreeNode("All")

        def test_append_childnode_should_raise_exception_for_foreign_tree_node(self):
                self.assertRaises(AssertionError, self.tree.append_childnode, tree.TreeNode("TreeNode"))

        def test_append_childnode_should_raise_exception_for_duplicate_tree_node(self):
                self.tree.append_childnode(moneydata.CategoryTreeNode("Child"))

                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "Child",
                        self.tree.append_childnode, moneydata.CategoryTreeNode("Child"))

        def test_append_childnode_should_return_node(self):
                node = self.tree.append_childnode(moneydata.CategoryTreeNode("Child"))

                self.assertTrue(node is not None)

        def test_format_should_not_increment_root_node(self):
                self.assertEqual(self.tree.format(False), "All")

        def test_format_should_indent_child_node(self):
                child = self.tree.append_childnode(moneydata.CategoryTreeNode("Child"))

                self.assertEqual(child.format(False), "  Child")

        def test_format_should_indent_each_sublevel(self):
                child = self.tree.append_childnode(moneydata.CategoryTreeNode("Child"))
                subchild = child.append_childnode(moneydata.CategoryTreeNode("SubChild"))

                self.assertEqual(subchild.format(False), "    SubChild")

        def test_format_should_return_indented_full_name(self):
                child = self.tree.append_childnode(moneydata.CategoryTreeNode("Child"))
                subchild = child.append_childnode(moneydata.CategoryTreeNode("SubChild"))

                self.assertEqual(subchild.format(True), "    All.Child.SubChild")


class TestMoneyData(unittest.TestCase):
        def setUp(self):
                self.moneydata = moneydata.MoneyData()

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
                filter_func = lambda t: t.fromcategory.is_contained_in_subtree(
                        category) or t.tocategory.is_contained_in_subtree(category)

                l = list(self.moneydata.filter_transactions(filter_func))

                self.assertEqual(len(l), 2)

        def test_add_transaction(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory1",
                        self.moneydata.add_transaction, "2000-01-01", "Cash.Out", "UnknownCategory1", "60.0", "")
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory1",
                        self.moneydata.add_transaction, "2000-01-01", "UnknownCategory1", "Cash.In", "60.0", "")

                transactioncount = len(self.moneydata.transactions)
                fromcategory = self.moneydata.get_category("Cash.Out")
                tocategory = self.moneydata.get_category("Category1")

                newtransaction = self.moneydata.add_transaction("2000-01-01", "Cash.Out", "Category1", "40.0", "")

                self.assertEqual(len(self.moneydata.transactions), transactioncount + 1)
                self.assertEqual(newtransaction.fromcategory, fromcategory)
                self.assertEqual(newtransaction.tocategory, tocategory)

                self.moneydata.add_transaction("2000-01-01", "Cash.Out", "UnknownCategory2", "50.0", "", True)
                self.assertEqual(len(self.moneydata.transactions), transactioncount + 2)

                self.moneydata.add_transaction("2000-01-01", "UnknownCategory3", "Cash.In", "50.0", "", True)
                self.assertEqual(len(self.moneydata.transactions), transactioncount + 3)

                self.moneydata.add_transaction("2000-01-01", "UnknownCategory4", "UnknownCategory5", "50.0", "", True)
                self.assertEqual(len(self.moneydata.transactions), transactioncount + 4)

        def test_delete_transaction(self):
                transactioncount = len(self.moneydata.transactions)

                # delete transaction to Subcategory1
                self.moneydata.delete_transaction(1)

                self.assertEqual(len(self.moneydata.transactions), transactioncount - 1)

                category = self.moneydata.get_category("Category1")
                subcategory = self.moneydata.get_category("Category1.Subcategory1")

                filter_func = lambda t: t.fromcategory is category or t.tocategory is category
                self.assertEqual(len(list(self.moneydata.filter_transactions(filter_func))), 1)

                filter_func = lambda t: t.fromcategory is subcategory or t.tocategory is subcategory
                self.assertEqual(len(list(self.moneydata.filter_transactions(filter_func))), 0)

        def test_parse_transaction(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.parse_transaction, "2000-01-01", "Cash.Out", "UnknownCategory", "10.0", "A comment")
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.parse_transaction, "2000-01-01", "UnknownCategory", "Cash.In", "10.0", "A comment")

                newtransaction = self.moneydata.parse_transaction("2000-01-01", "Cash.Out", "Category1", "10.0", "A comment")

                self.assertEqual(newtransaction.date, datetime.date(2000, 1, 1))
                self.assertEqual(newtransaction.fromcategory.name, "Out")
                self.assertEqual(newtransaction.tocategory.name, "Category1")
                self.assertEqual(newtransaction.amount, 10.0)
                self.assertEqual(newtransaction.comment, "A comment")

                newtransaction = self.moneydata.parse_transaction("2000-01-01", "Cash.Out", "UnknownCategory1", "10.0",
                        "A comment", True)
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.tocategory))

                newtransaction = self.moneydata.parse_transaction("2000-01-01", "UnknownCategory2", "Cash.In", "10.0",
                        "A comment", True)
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.fromcategory))

                newtransaction = self.moneydata.parse_transaction("2000-01-01", "UnknownCategory3", "UnknownCategory4", "10.0",
                        "A comment", True)
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.fromcategory))
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(newtransaction.tocategory))

        def test_get_category(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
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

                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "SubCategory1",
                        self.moneydata.add_category, "Category2", "SubCategory1")
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
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
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.delete_category, "UnknownCategory")
                self.assertRaisesRegex(moneydata.CategoryIsTopCategoryException, "All",
                        self.moneydata.delete_category, "All")

                self.moneydata.delete_category("Category1")

                self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category1.Subcategory1"))
                self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category1"))

        def test_rename_category(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.rename_category, "UnknownCategory", "RenamedUnknownCategory")
                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "In",
                        self.moneydata.rename_category, "External.Out", "In")

                # test renaming to a new category name
                category = self.moneydata.get_category("Category1")
                filter_func_from = lambda t: t.fromcategory is category
                filter_func_to = lambda t: t.tocategory is category
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
                self.moneydata.add_transaction("2000-01-05", "Cash.Out", "RenamedNewCategory.RenamedNewSubCategory", 1,
                        "Unknown transaction", True)
                category = self.moneydata.get_category("Category2.Subcategory1")
                renamedsubcategory = self.moneydata.get_category("RenamedNewSubCategory")
                filter_func_from = lambda t: t.fromcategory is renamedsubcategory
                filter_func_to = lambda t: t.tocategory is renamedsubcategory
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
                filter_func_from = lambda t: t.fromcategory is renamedsubcategory
                filter_func_to = lambda t: t.tocategory is renamedsubcategory
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
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.merge_to_category, "UnknownCategory", "Category1")
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.merge_to_category, "Category1", "UnknownCategory")

                sourcecategory = self.moneydata.get_category("Category1")
                targetcategory = self.moneydata.get_category("Category2")

                filter_func = lambda t: t.fromcategory.is_contained_in_subtree(
                        targetcategory) or t.tocategory.is_contained_in_subtree(targetcategory)
                transactions = list(self.moneydata.filter_transactions(filter_func))

                self.moneydata.merge_to_category(sourcecategory.name, targetcategory.name)

                for transaction in transactions:
                        self.assertTrue(filter_func(transaction))

        def test_move_category(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.move_category, "UnknownCategory", "Category1")
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
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

                self.assertEqual(summary["All"].sumcountin, 4)
                self.assertEqual(summary["Cash"].sumcountin, 2)
                self.assertEqual(summary["Cash.In"].sumcountin, 2)
                self.assertEqual(summary["Cash.Out"].sumcountin, 0)
                self.assertEqual(summary["External"].sumcountin, 2)
                self.assertEqual(summary["External.In"].sumcountin, 0)
                self.assertEqual(summary["Category2"].sumcountin, 0)
                self.assertEqual(summary["Category2.Subcategory1"].sumcountin, 0)
                self.assertEqual(summary["External.Out"].sumcountin, 2)
                self.assertEqual(summary["Category1"].sumcountin, 2)
                self.assertEqual(summary["Category1.Subcategory1"].sumcountin, 1)

                self.assertEqual(summary["All"].sumcountout, 4)
                self.assertEqual(summary["Cash"].sumcountout, 2)
                self.assertEqual(summary["Cash.In"].sumcountout, 0)
                self.assertEqual(summary["Cash.Out"].sumcountout, 2)
                self.assertEqual(summary["External"].sumcountout, 2)
                self.assertEqual(summary["External.In"].sumcountout, 2)
                self.assertEqual(summary["Category2"].sumcountout, 2)
                self.assertEqual(summary["Category2.Subcategory1"].sumcountout, 1)
                self.assertEqual(summary["External.Out"].sumcountout, 0)
                self.assertEqual(summary["Category1"].sumcountout, 0)
                self.assertEqual(summary["Category1.Subcategory1"].sumcountout, 0)

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
                        self.assertEqual(summary[categoryname].amount,
                                summary[categoryname].amountin + summary[categoryname].amountout)
                        self.assertEqual(summary[categoryname].sumcount,
                                summary[categoryname].sumcountin + summary[categoryname].sumcountout)
                        self.assertEqual(summary[categoryname].sum, summary[categoryname].sumin + summary[categoryname].sumout)


if __name__ == '__main__':
        unittest.main()
