# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import moneydata
from lib.data import tree

import unittest
import datetime
import functools


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

        def test_append_by_relative_path_should_create_all_nodes_contained_in_path(self):
                childnode = self.tree.append_by_relative_path("Node.ChildNode")
                node = self.tree.find_first_node_by_relative_path("Node")

                self.assertIsNotNone(childnode)
                self.assertIsNotNone(node)
                self.assertIs(childnode.parent, node)

        def test_append_by_relative_path_should_use_existing_nodes_along_the_path(self):
                node = self.tree.append_childnode(moneydata.CategoryTreeNode("Node"))

                childnode = self.tree.append_by_relative_path("Node.ChildNode")

                self.assertIsNotNone(childnode)
                self.assertIs(childnode.parent, node)

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


class TestMoneyData_Transactions(unittest.TestCase):
        def setUp(self):
                self.moneydata = moneydata.MoneyData()

                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")
                self.moneydata.add_category("All", "Category3")

        def test_filter_transactions(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                self.moneydata.add_transaction("2000-01-01", "Category2", "Category3", "20.0", "")
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category3", "30.0", "")

                filter_func = lambda t: t.fromcategory.name == "Category1"

                l = list(self.moneydata.filter_transactions(filter_func))

                self.assertEqual(len(l), 2)

        def test_add_transaction_should_raise_exception_if_from_category_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory1",
                        self.moneydata.add_transaction, "2000-01-01", "Category1", "UnknownCategory1", "10.0", "")

        def test_add_transaction_should_raise_exception_if_to_category_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory1",
                        self.moneydata.add_transaction, "2000-01-01", "UnknownCategory1", "Category1", "10.0", "")

        def test_add_transaction_should_add_fromcategory_if_forced(self):
                self.moneydata.add_transaction("2000-01-01", "UnknownCategory", "Category1", "10.0", "", True)

                unknowncategory = self.moneydata.get_category("UnknownCategory")
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknowncategory))

        def test_add_transaction_should_add_tocategory_if_forced(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "UnknownCategory", "10.0", "", True)

                unknowncategory = self.moneydata.get_category("UnknownCategory")
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknowncategory))

        def test_add_transaction_should_increase_transaction_list(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "20.0", "")

                self.assertEqual(len(self.moneydata.transactions), 2)

        def test_add_transaction_should_replace_category_strings_with_CategoryTreeNode(self):
                newtransaction = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "40.0", "")

                fromcategory = self.moneydata.get_category("Category1")
                tocategory = self.moneydata.get_category("Category2")

                self.assertEqual(newtransaction.fromcategory, fromcategory)
                self.assertEqual(newtransaction.tocategory, tocategory)

        def test_add_transaction_should_generate_an_unique_index(self):
                transaction1 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                transaction2 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "20.0", "")

                self.assertNotEqual(transaction1.index, transaction2.index)

        def test_add_transaction_should_generate_an_unique_index_after_deletion(self):
                transaction1 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                transaction2 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "20.0", "")

                self.moneydata.delete_transaction(transaction1.index)

                transaction3 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "30.0", "")

                self.assertNotEqual(transaction3.index, transaction2.index)

        def test_edit_transaction_should_raise_exception_for_invalid_index(self):
                self.assertRaisesRegex(IndexError, "list index out of range",
                        self.moneydata.edit_transaction, -1, "2000-01-01", "Category1", "Category2", "20.0", "")

                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")

                self.assertRaisesRegex(IndexError, "list index out of range",
                        self.moneydata.edit_transaction, 1, "2000-01-01", "Category1", "Category2", "20.0", "")

        def test_edit_transaction_should_raise_exception_if_from_category_was_not_found(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory1",
                        self.moneydata.edit_transaction, 0, "2000-01-01", "Category1", "UnknownCategory1", "20.0", "")

        def test_edit_transaction_should_raise_exception_if_to_category_was_not_found(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory1",
                        self.moneydata.edit_transaction, 0, "2000-01-01", "UnknownCategory1", "Category1", "20.0", "")

        def test_edit_transaction_should_replace_category_strings_with_CategoryTreeNode(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")

                newtransaction = self.moneydata.edit_transaction(0, "2000-01-02", "Category2", "Category3", "20.0", "Comment")

                fromcategory = self.moneydata.get_category("Category2")
                tocategory = self.moneydata.get_category("Category3")

                self.assertEqual(newtransaction.date, datetime.date(2000, 1, 2))
                self.assertIs(newtransaction.fromcategory, fromcategory)
                self.assertIs(newtransaction.tocategory, tocategory)
                self.assertEqual(newtransaction.amount, 20.0)
                self.assertEqual(newtransaction.comment, "Comment")

        def test_edit_transaction_should_keep_the_index(self):
                self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")

                newtransaction = self.moneydata.edit_transaction(0, "2000-01-02", "Category2", "Category3", "20.0", "Comment")

                self.assertIs(newtransaction, self.moneydata.transactions[0])
                self.assertEqual(newtransaction.index, 0)

        def test_delete_transaction_should_delete_first_transaction(self):
                transaction1 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                transaction2 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "20.0", "")

                self.moneydata.delete_transaction(transaction1.index)

                self.assertEqual(len(self.moneydata.transactions), 1)
                self.assertEqual(self.moneydata.transactions[0].amount, 20.0, "second transaction should not have been deleted")

        def test_delete_transaction_should_update_indices(self):
                transaction1 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "10.0", "")
                transaction2 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "20.0", "")
                transaction3 = self.moneydata.add_transaction("2000-01-01", "Category1", "Category2", "30.0", "")

                self.moneydata.delete_transaction(transaction1.index)

                self.assertEqual(transaction2.index, 0)
                self.assertEqual(transaction3.index, 1)

        def test_parse_transaction_should_raise_exception_if_fromcategory_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.parse_transaction, "2000-01-01", "Category1", "UnknownCategory", "10.0", "A comment")
 
        def test_parse_transaction_should_raise_exception_if_tocategory_was_not_found(self):
               self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.parse_transaction, "2000-01-01", "UnknownCategory", "Category1", "10.0", "A comment")

        def test_parse_transaction_should_add_fromcategory_if_forced(self):
                self.moneydata.parse_transaction("2000-01-01", "UnknownCategory", "Category1", "10.0", "", True)

                unknowncategory = self.moneydata.get_category("UnknownCategory")
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknowncategory))

        def test_parse_transaction_should_add_tocategory_if_forced(self):
                self.moneydata.parse_transaction("2000-01-01", "Category1", "UnknownCategory", "10.0", "", True)

                unknowncategory = self.moneydata.get_category("UnknownCategory")
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknowncategory))

        def test_parse_transaction(self):
                newtransaction = self.moneydata.parse_transaction("2000-01-01", "Category1", "Category2", "10.0", "A comment")

                self.assertEqual(newtransaction.date, datetime.date(2000, 1, 1))
                self.assertEqual(newtransaction.fromcategory.name, "Category1")
                self.assertEqual(newtransaction.tocategory.name, "Category2")
                self.assertEqual(newtransaction.amount, 10.0)
                self.assertEqual(newtransaction.comment, "A comment")


class TestMoneyData_Categories(unittest.TestCase):
        def setUp(self):
                self.moneydata = moneydata.MoneyData()

        def test_get_category_should_raise_exception_if_category_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.get_category, "UnknownCategory")

        def test_get_category_should_find_the_CategoryTree_instance(self):
                self.moneydata.add_category("All", "Category")

                existingcategory = self.moneydata.get_category("Category")
                self.assertEqual(existingcategory.name, "Category")

        def test_get_category_should_find_the_CategoryTree_instance_when_mentioning_subpath(self):
                self.moneydata.add_category("All", "Category")
                self.moneydata.add_category("Category", "SubCategory")

                existingcategory = self.moneydata.get_category("Category.SubCategory")
                self.assertEqual(existingcategory.name, "SubCategory")

        def test_get_category_should_raise_exception_if_category_name_was_ambiguous(self):
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")

                self.moneydata.add_category("Category1", "Ambi")
                self.moneydata.add_category("Category2", "Ambi")

                self.assertRaisesRegex(moneydata.AmbiguousCategoryNameException, "Ambi", self.moneydata.get_category, "Ambi")

        def test_regular_category_should_not_be_contained_in_notfound_category(self):
                self.moneydata.add_category("All", "Category")

                category = self.moneydata.get_category("Category")
                self.assertFalse(self.moneydata.category_is_contained_in_notfound_category(category))

        def test_add_category_should_add_a_category_under_the_given_parent(self):
                self.moneydata.add_category("All", "Category")

                category = self.moneydata.get_category("Category")
                self.assertTrue(category.is_contained_in_subtree(self.moneydata.get_category("All")))

        def test_add_category_should_raise_an_exception_if_category_from_notfound_node_was_created(self):
                self.moneydata.add_category("All", "Source")
                transaction = self.moneydata.add_transaction("2000-01-01", "Source", "Unknown.Target", "10.0", "", True)

                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "Target",
                        self.moneydata.add_category, "All", "Target")

        def test_add_category_should_raise_an_exception_when_adding_another_child_having_the_same_name(self):
                self.moneydata.add_category("All", "Category")

                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "Category",
                        self.moneydata.add_category, "All", "Category")

        def test_add_category_should_be_possible_with_equal_names_under_different_parents(self):
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")

                self.assertTrue(self.moneydata.add_category("Category1", "SubCategory1"))
                self.assertTrue(self.moneydata.add_category("Category2", "SubCategory1"))

        def test_delete_category_should_raise_an_exception_if_category_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.delete_category, "UnknownCategory")

        def test_delete_category_should_raise_an_exception_if_top_category_was_given(self):
                self.assertRaisesRegex(moneydata.CategoryIsTopCategoryException, "All",
                        self.moneydata.delete_category, "All")

        def test_delete_category_should_delete_category_and_its_descendants(self):
                self.moneydata.add_category("All", "Category")
                self.moneydata.add_category("Category", "SubCategory")

                self.moneydata.delete_category("Category")

                self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Subcategory"))
                self.assertFalse(self.moneydata.categorytree.find_first_node_by_relative_path("Category"))

        def test_delete_category_should_keep_category_if_transactions_are_attached_to_it(self):
                category1 = self.moneydata.add_category("All", "Category1")
                category2 = self.moneydata.add_category("All", "Category2")

                a1 = self.moneydata.add_category("Category1", "A")
                a2 = self.moneydata.add_category("Category2", "A")

                b1 = self.moneydata.add_category("Category1.A", "B")
                b2 = self.moneydata.add_category("Category2.A", "B")

                c1 = self.moneydata.add_category("Category1.A.B", "C")
                c2 = self.moneydata.add_category("Category2.A.B", "C")

                transaction1 = self.moneydata.add_transaction("2000-01-01", "All", "Category1.A.B", 10.0, "")
                transaction2 = self.moneydata.add_transaction("2000-01-01", "All", "Category1.A.B", 10.0, "")

                self.moneydata.delete_category("Category1.A")

                self.assertIs(self.moneydata.get_category("NOTFOUND.Category1.A.B"), transaction1.tocategory)
                self.assertIs(self.moneydata.get_category("NOTFOUND.Category1.A.B"), transaction2.tocategory)
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "NOTFOUND.Category1.A.B.C", self.moneydata.get_category, "NOTFOUND.Category1.A.B.C")

        def test_rename_category_should_raise_an_exception_if_category_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.rename_category, "UnknownCategory", "RenamedUnknownCategory")

        def test_rename_category_should_raise_an_exception_if_a_sibling_with_equal_name_exists(self):
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")

                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "Category1",
                        self.moneydata.rename_category, "Category2", "Category1")

        def test_rename_category_should_change_the_name_of_a_category(self):
                self.moneydata.add_category("All", "Category")

                category = self.moneydata.get_category("Category")
                self.moneydata.rename_category("Category", "RenamedCategory")

                self.assertEqual(category.name, "RenamedCategory")

        def test_rename_category_should_change_all_transactions_involved(self):
                self.moneydata.add_category("All", "Category")
                self.moneydata.add_category("All", "OtherCategory")

                transaction1 = self.moneydata.add_transaction("2000-01-01", "Category", "OtherCategory", "10.0", "")
                transaction2 = self.moneydata.add_transaction("2000-01-01", "OtherCategory", "Category", "10.0", "")

                self.moneydata.rename_category("Category", "RenamedCategory")

                self.assertEqual(transaction1.fromcategory.name, "RenamedCategory")
                self.assertEqual(transaction2.tocategory.name, "RenamedCategory")

        def test_rename_category_should_raise_an_exception_if_trying_to_renaming_to_a_category_which_is_part_of_the_notfound_node(self):
                self.moneydata.add_category("All", "Source")
                self.moneydata.add_category("All", "Category")
                transaction = self.moneydata.add_transaction("2000-01-01", "Source", "Unknown.Target", "10.0", "", True)

                self.assertRaisesRegex(moneydata.DuplicateCategoryException, "Target",
                        self.moneydata.rename_category, "Category", "Target")

        def test_merge_to_category_should_raise_an_exception_when_source_category_was_not_found(self):
                self.moneydata.add_category("All", "Category")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.merge_to_category, "UnknownCategory", "Category")

        def test_merge_to_category_should_raise_an_exception_when_target_category_was_not_found(self):
                self.moneydata.add_category("All", "Category")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.merge_to_category, "Category", "UnknownCategory")

        def test_merge_to_category_should_remove_source_category(self):
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")

                self.moneydata.merge_to_category("Category1", "Category2")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "Category1",
                        self.moneydata.get_category, "Category1")

        def test_merge_to_category_should_replace_source_category_with_target_category_in_transactions_involved(self):
                self.moneydata.add_category("All", "Assets")
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")

                transactions_from_assets = [
                        self.moneydata.add_transaction("2000-01-01", "Assets", "Category1", "10.0", ""),
                        self.moneydata.add_transaction("2000-01-02", "Assets", "Category2", "20.0", "")
                ]

                transactions_to_assets = [
                        self.moneydata.add_transaction("2000-01-01", "Category1", "Assets", "30.0", ""),
                        self.moneydata.add_transaction("2000-01-02", "Category2", "Assets", "40.0", "")
                ]

                self.moneydata.merge_to_category("Category1", "Category2")

                for transaction in transactions_from_assets:
                        self.assertEqual(transaction.tocategory.name, "Category2")

                for transaction in transactions_to_assets:
                        self.assertEqual(transaction.fromcategory.name, "Category2")

        def test_merge_to_category_should_replace_source_category_with_target_category_in_paymentplans_involved(self):
                self.moneydata.add_category("All", "Assets")
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")

                paymentplans_from_assets = [
                        self.moneydata.add_paymentplan("ToCategory1", "Plans", "Assets", "Category1", "10.0", ""),
                        self.moneydata.add_paymentplan("ToCategory2", "Plans", "Assets", "Category2", "20.0", "")
                ]

                paymentplans_to_assets = [
                        self.moneydata.add_paymentplan("FromCategory1", "Plans", "Category1", "Assets", "30.0", ""),
                        self.moneydata.add_paymentplan("FromCategory2", "Plans", "Category2", "Assets", "40.0", "")
                ]

                self.moneydata.merge_to_category("Category1", "Category2")

                for paymentplan in paymentplans_from_assets:
                        self.assertEqual(paymentplan.tocategory.name, "Category2")

                for paymentplan in paymentplans_to_assets:
                        self.assertEqual(paymentplan.fromcategory.name, "Category2")

        def test_move_category_should_change_parent_of_source_category(self):
                category1 = self.moneydata.add_category("All", "Category1")
                category2 = self.moneydata.add_category("All", "Category2")

                self.moneydata.move_category("Category1", "Category2")

                self.assertEqual(category1.parent.name, "Category2")

        def test_move_category_should_raise_an_exception_if_source_category_was_not_found(self):
                self.moneydata.add_category("All", "Category")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.move_category, "UnknownCategory", "Category")

        def test_move_category_should_raise_an_exception_if_target_category_was_not_found(self):
                self.moneydata.add_category("All", "Category")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "UnknownCategory",
                        self.moneydata.move_category, "Category", "UnknownCategory")

        def test_move_category_should_raise_an_exception_if_target_category_is_contained_in_source_category_subtree(self):
                self.moneydata.add_category("All", "Category")
                self.moneydata.add_category("Category", "SubCategory")

                self.assertRaises(tree.TargetNodeIsPartOfSourceNodeSubTreeException, self.moneydata.move_category, "Category", "SubCategory")


class TestMoneyData_PaymentPlans(unittest.TestCase):
        def setUp(self):
                self.moneydata = moneydata.MoneyData()

        def test_get_paymentplan_should_raise_an_exeption_if_paymentplan_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "Unknown", self.moneydata.get_paymentplan, "Unknown")

        def test_get_paymentplan_should_return_the_paymentplan_belonging_to_the_given_name(self):
                self.moneydata.add_paymentplan("existingPlan", "group", "All", "All", 10-0, "Example plan")
                self.moneydata.add_paymentplan("otherExistingPlan", "group", "All", "All", 10-0, "Example plan")

                paymentplan = self.moneydata.get_paymentplan("existingPlan")

                self.assertIsNotNone(paymentplan)
                self.assertEqual(paymentplan.name, "existingPlan")

        def test_find_similar_paymentplans_should_return_empty_result_if_no_such_payment_plan_exists(self):
                paymentplans = self.moneydata.find_similar_paymentplans("All", "All", "10.0")

                self.assertEqual(paymentplans, [])

        def test_find_similar_paymentplans_should_return_a_list_of_all_similar_payment_plans(self):
                self.moneydata.add_category("All", "Category1")
                self.moneydata.add_category("All", "Category2")
                self.moneydata.add_category("All", "Category3")

                paymentplan1 = self.moneydata.add_paymentplan("plan1", "group", "Category1", "Category2", "10.0", "First similar plan")
                paymentplan2 = self.moneydata.add_paymentplan("plan2", "group", "Category1", "Category2", "10.0", "Other similar plan")
                paymentplan3 = self.moneydata.add_paymentplan("plan3", "group", "Category2", "Category3", "10.0", "Other plan")

                paymentplans = self.moneydata.find_similar_paymentplans("Category1", "Category2", "10.0")

                self.assertEqual(paymentplans, [paymentplan1, paymentplan2])

        def test_add_paymentplan_should_raise_an_exception_if_a_plan_with_the_given_name_does_already_exist(self):
                self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")

                self.assertRaisesRegex(moneydata.DuplicatePaymentPlanException, "plan", self.moneydata.add_paymentplan, "plan", "group", "All", "All", 10.0, "Example plan")

        def test_add_paymentplan_should_raise_an_exception_if_fromcategory_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "Unknown", self.moneydata.add_paymentplan, "plan", "group", "Unknown", "All", 10.0, "Example plan")

        def test_add_paymentplan_should_raise_an_exception_if_tocategory_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "Unknown", self.moneydata.add_paymentplan, "plan", "group", "All", "Unknown", 10.0, "Example plan")

        def test_add_paymentplan_should_add_fromcategory_if_forced(self):
                self.moneydata.add_paymentplan("plan", "group", "Unknown", "All", 10.0, "Example plan", True)

                unknowncategory = self.moneydata.get_category("Unknown")
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknowncategory))

        def test_add_paymentplan_should_add_tocategory_if_forced(self):
                self.moneydata.add_paymentplan("plan", "group", "All", "Unknown", 10.0, "Example plan", True)

                unknowncategory = self.moneydata.get_category("Unknown")
                self.assertTrue(self.moneydata.category_is_contained_in_notfound_category(unknowncategory))

        def test_add_paymentplan_should_replace_categorystrings_with_categories(self):
                category1 = self.moneydata.add_category("All", "Category1")
                category2 = self.moneydata.add_category("All", "Category2")

                paymentplan = self.moneydata.add_paymentplan("plan", "group", "Category1", "Category2", 10.0, "Example plan")

                self.assertIs(paymentplan.fromcategory, category1)
                self.assertIs(paymentplan.tocategory, category2)

        def test_delete_paymentplan_should_raise_an_exception_if_paymentplan_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "plan", self.moneydata.delete_paymentplan, "plan")

        def test_delete_paymentplan_should_remove_the_given_paymentplan(self):
                self.moneydata.add_paymentplan("plan1", "group", "All", "All", 10.0, "Example plan")
                self.moneydata.add_paymentplan("plan2", "group", "All", "All", 20.0, "Example plan")

                self.moneydata.delete_paymentplan("plan1")

                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "plan1", self.moneydata.get_paymentplan, "plan1")
                self.assertIsNotNone(self.moneydata.get_paymentplan("plan2"))

        def test_delete_paymentplan_should_remove_references_to_transactions(self):
                self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")
                transaction = self.moneydata.execute_paymentplan("plan", "2000-01-01")

                self.moneydata.delete_paymentplan("plan")

                self.assertIsNone(transaction.paymentplan)

        def test_edit_paymentplan_should_raise_an_exception_if_paymentplan_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "plan", self.moneydata.edit_paymentplan, "plan", "group", "All", "All", 10.0, "Example plan")

        def test_edit_paymentplan_should_raise_an_exception_if_fromcategory_was_not_found(self):
                self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "Unknown", self.moneydata.edit_paymentplan, "plan", "group", "Unknown", "All", 10.0, "Example plan")

        def test_edit_paymentplan_should_raise_an_exception_if_fromcategory_was_not_found(self):
                self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")

                self.assertRaisesRegex(moneydata.NoSuchCategoryException, "Unknown", self.moneydata.edit_paymentplan, "plan", "group", "All", "Unknown", 10.0, "Example plan")

        def test_edit_paymentplan_should_change_existing_plan(self):
                category1 = self.moneydata.add_category("All", "Category1")
                category2 = self.moneydata.add_category("All", "Category2")
                self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")

                self.moneydata.edit_paymentplan("plan", "newgroup", "Category1", "Category2", 20.0, "Changed comment")

                paymentplan = self.moneydata.get_paymentplan("plan")

                self.assertEqual(paymentplan.name, "plan")
                self.assertEqual(paymentplan.groupname, "newgroup")
                self.assertIs(paymentplan.fromcategory, category1)
                self.assertIs(paymentplan.tocategory, category2)
                self.assertEqual(paymentplan.amount, 20.0)
                self.assertEqual(paymentplan.comment, "Changed comment")

        def test_edit_paymentplan_should_update_references_on_transactions(self):
                category1 = self.moneydata.add_category("All", "Category1")
                category2 = self.moneydata.add_category("All", "Category2")
                self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")
                transaction = self.moneydata.execute_paymentplan("plan", "2000-01-01")

                paymentplan = self.moneydata.edit_paymentplan("plan", "newgroup", "Category1", "Category2", 20.0, "Changed comment")

                self.assertIs(transaction.paymentplan, paymentplan)

        def test_rename_paymentplan_should_raise_an_exception_if_paymentplan_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "plan", self.moneydata.rename_paymentplan, "plan", "newname")

        def test_rename_paymentplan_should_raise_an_exception_if_a_paymentplan_with_the_new_name_already_exists(self):
                paymentplan = self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")
                paymentplan = self.moneydata.add_paymentplan("existing", "group", "All", "All", 10.0, "Example plan")

                self.assertRaisesRegex(moneydata.DuplicatePaymentPlanException, "existing", self.moneydata.rename_paymentplan, "plan", "existing")

        def test_rename_paymentplan_should_change_name_of_existing_plan(self):
                paymentplan = self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")

                self.moneydata.rename_paymentplan("plan", "newname")

                self.assertEqual(paymentplan.name, "newname")

        def test_rename_paymentplan_should_update_references_on_transactions(self):
                paymentplan = self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")
                transaction = self.moneydata.execute_paymentplan("plan", "2000-01-01")

                self.moneydata.rename_paymentplan("plan", "newname")

                paymentplan = self.moneydata.get_paymentplan("newname")
                self.assertIs(transaction.paymentplan, paymentplan)

        def test_move_paymentplan_should_raise_an_exception_if_paymentplan_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "plan", self.moneydata.move_paymentplan, "plan", "newgroup")

        def test_move_paymentplan_should_change_groupname(self):
                paymentplan = self.moneydata.add_paymentplan("plan", "group", "All", "All", 10.0, "Example plan")

                self.moneydata.move_paymentplan("plan", "newgroup")

                paymentplan = self.moneydata.get_paymentplan("plan")
                self.assertEqual(paymentplan.groupname, "newgroup")

        def test_execute_paymentplan_should_raise_an_exception_if_paymentplan_was_not_found(self):
                self.assertRaisesRegex(moneydata.NoSuchPaymentPlanException, "plan", self.moneydata.execute_paymentplan, "plan", "2000-01-01")

        def test_execute_paymentplan(self):
                category1 = self.moneydata.add_category("All", "Category1")
                category2 = self.moneydata.add_category("All", "Category2")
                self.moneydata.add_paymentplan("planname", "group", "Category1", "Category2", 10.0, "Example plan")

                transaction1 = self.moneydata.execute_paymentplan("planname", "2000-01-01")

                self.assertEqual(transaction1.index, 0)
                self.assertEqual(transaction1.date, datetime.date(2000, 1, 1))
                self.assertIs(transaction1.fromcategory, category1)
                self.assertIs(transaction1.tocategory, category2)
                self.assertEqual(transaction1.amount, 10.0)
                self.assertEqual(transaction1.comment, "Example plan")


class TestMoneyData_Summary(unittest.TestCase):
        def setUp(self):
                self.moneydata = moneydata.MoneyData()

        def test_create_summary_should_accumulate_transactions_of_a_category(self):
                self.moneydata.add_category("All", "Source")
                self.moneydata.add_category("All", "Target")

                self.moneydata.add_paymentplan("plan1", "group", "Source", "Target", "10.0", "")
                self.moneydata.add_paymentplan("plan2", "group", "Source", "Target", "20.0", "")
                self.moneydata.add_paymentplan("plan3", "group", "Source", "Target", "30.0", "")

                self.moneydata.execute_paymentplan("plan1", "2000-01-01")
                self.moneydata.execute_paymentplan("plan2", "2000-01-01")
                self.moneydata.execute_paymentplan("plan3", "2000-01-01")

                filter_func = lambda t: True
                summary = self.moneydata.create_summary(filter_func, filter_func)

                self.assertEqual(summary["Source"].amountin, 0.0)
                self.assertEqual(summary["Source"].amountout, -60.0)
                self.assertEqual(summary["Source"].amount, -60.0)

                self.assertEqual(summary["Source"].sumcountin, 0)
                self.assertEqual(summary["Source"].sumcountout, 3)
                self.assertEqual(summary["Source"].sumcount, 3)

                self.assertEqual(summary["Source"].paymentplancountin, 0)
                self.assertEqual(summary["Source"].paymentplancountout, 3)
                self.assertEqual(summary["Source"].paymentplancount, 3)

                self.assertEqual(summary["Source"].sumin, 0.0)
                self.assertEqual(summary["Source"].sumout, -60.0)
                self.assertEqual(summary["Source"].sum, -60.0)


                self.assertEqual(summary["Target"].amountin, 60.0)
                self.assertEqual(summary["Target"].amountout, 0.0)
                self.assertEqual(summary["Target"].amount, 60.0)

                self.assertEqual(summary["Target"].sumcountin, 3)
                self.assertEqual(summary["Target"].sumcountout, 0)
                self.assertEqual(summary["Target"].sumcount, 3)

                self.assertEqual(summary["Target"].paymentplancountin, 3)
                self.assertEqual(summary["Target"].paymentplancountout, 0)
                self.assertEqual(summary["Target"].paymentplancount, 3)

                self.assertEqual(summary["Target"].sumin, 60.0)
                self.assertEqual(summary["Target"].sumout, 0.0)
                self.assertEqual(summary["Target"].sum, 60.0)

        def test_create_summary_should_not_accumulate_floating_point_errors(self):
                self.moneydata.add_category("All", "Source")
                self.moneydata.add_category("All", "Target")

                self.moneydata.add_paymentplan("plan", "group", "Source", "Target", "0.01", "")
                self.moneydata.add_paymentplan("plan6", "group", "Target", "Source", "0.06", "")

                for i in range(6):
                        self.moneydata.execute_paymentplan("plan", "2000-01-01")
                self.moneydata.execute_paymentplan("plan6", "2000-01-01")

                almostZero = functools.reduce( lambda sum, val: sum+val, [0.01]*6 ) - 0.06
                self.assertNotEqual(almostZero, 0, "python floating point arithmetic should fail to exactly sum up 0.01 six times")

                filter_func = lambda t: True
                summary = self.moneydata.create_summary(filter_func, filter_func)

                self.assertEqual(summary["Target"].amount, 0, "create_summary() should make sure that adding 0.01 six times and subtracting 0.06 equals exactly 0")

        def test_create_summary_should_accumulate_values_of_subcategories(self):
                self.moneydata.add_category("All", "Source")
                self.moneydata.add_category("All", "Target")

                self.moneydata.add_paymentplan("plan1", "group", "Source", "Target", "10.0", "")
                self.moneydata.add_paymentplan("plan2", "group", "Source", "Target", "20.0", "")
                self.moneydata.add_paymentplan("plan3", "group", "Source", "Target", "30.0", "")

                self.moneydata.execute_paymentplan("plan1", "2000-01-01")
                self.moneydata.execute_paymentplan("plan2", "2000-01-01")
                self.moneydata.execute_paymentplan("plan3", "2000-01-01")

                filter_func = lambda t: True
                summary = self.moneydata.create_summary(filter_func, filter_func)

                self.assertEqual(summary["All"].amountin, 0)
                self.assertEqual(summary["All"].amountout, 0)
                self.assertEqual(summary["All"].amount, 0)

                self.assertEqual(summary["All"].sumin, 60.0)
                self.assertEqual(summary["All"].sumout, -60.0)
                self.assertEqual(summary["All"].sum, 0.0)

                self.assertEqual(summary["All"].sumcountin, 3)
                self.assertEqual(summary["All"].sumcountout, 3)
                self.assertEqual(summary["All"].sumcount, 6)

                self.assertEqual(summary["All"].paymentplancountin, 3)
                self.assertEqual(summary["All"].paymentplancountout, 3)
                self.assertEqual(summary["All"].paymentplancount, 6)

        def test_create_summary_should_use_the_given_initial_sums_based_on_previous_result(self):
                self.moneydata.add_category("All", "Source")
                self.moneydata.add_category("All", "Target")

                self.moneydata.add_paymentplan("plan", "group", "Source", "Target", "10.0", "")

                self.moneydata.execute_paymentplan("plan", "2000-01-01")

                d_previous_summary = {"All": moneydata.NodeSummary()}

                d_previous_summary["All"].amount = 0.0
                d_previous_summary["All"].amountin = 10.0
                d_previous_summary["All"].amountout = -10.0

                d_previous_summary["All"].sum = 0.0
                d_previous_summary["All"].sumin = 10.0
                d_previous_summary["All"].sumout = -10.0


                filter_func = lambda t: True
                summary = self.moneydata.create_summary(filter_func, filter_func, d_previous_summary)

                self.assertEqual(summary["All"].amountin, 10.0)
                self.assertEqual(summary["All"].amountout, -10.0)
                self.assertEqual(summary["All"].amount, 0)

                self.assertEqual(summary["All"].sumin, 20.0)
                self.assertEqual(summary["All"].sumout, -20.0)
                self.assertEqual(summary["All"].sum, 0.0)


if __name__ == '__main__':
        unittest.main()
