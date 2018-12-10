# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import tree

import unittest


class TestTreeNode(unittest.TestCase):
        def setUp(self):
                self.tree = tree.TreeNode("All")

                self.childnode1 = tree.TreeNode("Child1")
                self.childnode2 = tree.TreeNode("Child2")
                self.subchildnode1_1 = tree.TreeNode("SubChild1")
                self.subchildnode1_2 = tree.TreeNode("SubChild2")
                self.subchildnode2_1 = tree.TreeNode("SubChild1")
                self.subchildnode2_2 = tree.TreeNode("SubChild2")

                self.tree.append_childnode(self.childnode1)
                self.tree.append_childnode(self.childnode2)

                self.childnode1.append_childnode(self.subchildnode1_1)
                self.childnode1.append_childnode(self.subchildnode1_2)

                self.childnode2.append_childnode(self.subchildnode2_1)
                self.childnode2.append_childnode(self.subchildnode2_2)

        def test___iter___should_iterate_using_in_order(self):
                nodeA = tree.TreeNode("A")
                nodeB = nodeA.append_childnode(tree.TreeNode("B"))
                nodeB.append_childnode(tree.TreeNode("C"))
                nodeB.append_childnode(tree.TreeNode("D"))
                nodeE = nodeA.append_childnode(tree.TreeNode("E"))
                nodeE.append_childnode(tree.TreeNode("F"))
                nodeE.append_childnode(tree.TreeNode("G"))

                expected_order = ["A", "B", "C", "D", "E", "F", "G"]
                order = list(map(lambda node : node.name, nodeA))

                self.assertEqual(expected_order, order)

        def test_format(self):
                self.assertRegex(self.tree.format(), "[\t]{0}[^\t]*")
                self.assertRegex(self.childnode1.format(), "[\t]{1}[^\t]*")
                self.assertRegex(self.childnode2.format(), "[\t]{1}[^\t]*")
                self.assertRegex(self.subchildnode1_1.format(), "[\t]{2}[^\t]*")

        def test_append_childnode_should_raise_an_exception_if_parameter_is_not_a_TreeNode_object(self):
                treeRoot = tree.TreeNode("Root")

                self.assertRaises(AssertionError, treeRoot.append_childnode, object())

        def test_append_childnode_should_set_parent_of_child_node(self):
                treeRoot = tree.TreeNode("Root")
                node = treeRoot.append_childnode(tree.TreeNode("Child"))

                self.assertIs(node.parent, treeRoot)

        def test_append_childnode_should_insert_node_into_children_dictionary(self):
                treeRoot = tree.TreeNode("Root")
                node = treeRoot.append_childnode(tree.TreeNode("Child"))

                self.assertIs(treeRoot.children[node.name], node)
                self.assertIs(treeRoot.find_first_node_by_relative_path("Child"), node)

        def test_remove_childnode_by_name_should_raise_an_exception_if_node_was_not_found(self):
                treeRoot = tree.TreeNode("Root")

                self.assertRaisesRegex(tree.NoSuchNodeException, "Unknown", treeRoot.remove_childnode_by_name, "Unknown")

        def test_remove_childnode_by_name_should_remove_the_given_childnode(self):
                treeRoot = tree.TreeNode("Root")
                childNode = treeRoot.append_childnode(tree.TreeNode("Child"))

                treeRoot.remove_childnode_by_name("Child")

                self.assertIsNone(childNode.parent)
                self.assertIsNone(treeRoot.find_first_node_by_relative_path("Child"))

        def test_remove_childnode_should_raise_an_exception_if_the_given_node_is_not_a_child(self):
                treeRoot = tree.TreeNode("Root")

                self.assertRaisesRegex(tree.NodeIsNotAChildException, "('Root', 'NotAChild')",
                        treeRoot.remove_childnode, tree.TreeNode("NotAChild"))

        def test_remove_childnode_should_remove_the_given_childnode(self):
                treeRoot = tree.TreeNode("Root")
                childNode = treeRoot.append_childnode(tree.TreeNode("Child"))

                treeRoot.remove_childnode(childNode)

                self.assertIsNone(childNode.parent)
                self.assertIsNone(treeRoot.find_first_node_by_relative_path("Child"))

        def test_merge_from_node_should_raise_an_exception_if_targetnode_is_a_descendant_of_self(self):
                treeRoot = tree.TreeNode("Root")
                childNode = treeRoot.append_childnode(tree.TreeNode("Child"))

                self.assertRaisesRegex(tree.TargetNodeIsPartOfSourceNodeSubTreeException, "('Root', 'Child')",
                        childNode.merge_from_node, treeRoot)

        def test_merge_from_node_should_remove_source_node(self):
                treeRoot = tree.TreeNode("Root")
                source = treeRoot.append_childnode(tree.TreeNode("Source"))
                target = treeRoot.append_childnode(tree.TreeNode("Target"))

                target.merge_from_node(source)

                self.assertIsNone(source.parent)
                self.assertIsNone(treeRoot.find_first_node_by_relative_path("Source"))

        def test_merge_from_node_should_merge_all_descendant_categories_of_source_node_with_descendand_categories_of_the_target_node(self):
                treeRoot= tree.TreeNode("Root")
                source = treeRoot.append_childnode(tree.TreeNode("Source"))
                sourcechild = source.append_childnode(tree.TreeNode("SourceChild"))
                sourcecommonchild = source.append_childnode(tree.TreeNode("CommonChild"))
                target = treeRoot.append_childnode(tree.TreeNode("Target"))
                target.append_childnode(tree.TreeNode("TargetChild"))
                target.append_childnode(tree.TreeNode("CommonChild"))

                target.merge_from_node(source)

                self.assertIsNone(source.parent)
                self.assertIs(sourcechild.parent, target)
                self.assertIsNone(sourcecommonchild.parent)
                self.assertIsNotNone(target.find_first_node_by_relative_path("SourceChild"))
                self.assertIsNotNone(target.find_first_node_by_relative_path("CommonChild"))
                self.assertIsNotNone(target.find_first_node_by_relative_path("TargetChild"))

        def test_move_node_to_should_raise_an_exception_if_tried_to_move_node_under_one_of_its_descendants(self):
                treeRoot = tree.TreeNode("Root")
                node = treeRoot.append_childnode(tree.TreeNode("Node"))
                child = node.append_childnode(tree.TreeNode("Child"))

                self.assertRaisesRegex(tree.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child', 'Node')",
                        node.move_node_to, child)

        def test_move_node_to_should_change_parent_to_the_given_one(self):
                treeRoot = tree.TreeNode("Root")
                node1 = treeRoot.append_childnode(tree.TreeNode("Node1"))
                node2 = treeRoot.append_childnode(tree.TreeNode("Node2"))

                node2.move_node_to(node1)

                self.assertIs(node2.parent, node1)

        def test_rename(self):
                self.subchildnode1_1.rename("renamed")

                self.assertEqual(self.subchildnode1_1.name, "renamed")
                self.assertIs(self.tree.find_first_node_by_relative_path("renamed"), self.subchildnode1_1)

        def test_get_depth(self):
                self.assertEqual(self.tree.get_depth(), 0)
                self.assertEqual(self.childnode1.get_depth(), 1)
                self.assertEqual(self.subchildnode1_1.get_depth(), 2)

        def test_get_root(self):
                self.assertIs(self.tree.get_root(), self.tree)
                self.assertIs(self.childnode1.get_root(), self.tree)
                self.assertIs(self.subchildnode1_1.get_root(), self.tree)

        def test_find_first_node_by_relative_path(self):
                node = self.tree.find_first_node_by_relative_path("Child1.SubChild1")
                selfnode = self.subchildnode1_1.find_first_node_by_relative_path("SubChild1")
                notfoundnode = self.tree.find_first_node_by_relative_path("NoChild")

                self.assertIs(node, self.subchildnode1_1)
                self.assertIs(selfnode, self.subchildnode1_1)
                self.assertIs(notfoundnode, None)

        def test_find_nodes_by_relative_path(self):
                nodelist = self.tree.find_nodes_by_relative_path("SubChild1")
                selfnodelist = self.subchildnode1_1.find_nodes_by_relative_path("SubChild1")
                notfoundnodelist = self.tree.find_nodes_by_relative_path("NoChild")

                self.assertEqual(len(nodelist), 2)
                self.assertSetEqual(set(nodelist), {self.subchildnode1_1, self.subchildnode2_1})
                self.assertEqual(len(selfnodelist), 1)
                self.assertIs(selfnodelist[0], self.subchildnode1_1)
                self.assertEqual(len(notfoundnodelist), 0)

        def test_find_nodes(self):
                anode1 = self.tree.append_childnode(tree.TreeNode("ANode"))
                anode2 = self.subchildnode1_1.append_childnode(tree.TreeNode("ANode"))

                l = self.tree.find_nodes("ANode")

                self.assertEqual(set(l), {anode1, anode2})

        def test_get_full_name(self):
                self.assertEqual(self.subchildnode1_1.get_full_name(), "All.Child1.SubChild1")

        def test_is_contained_in_subtree(self):
                self.assertTrue(self.subchildnode1_1.is_contained_in_subtree(self.subchildnode1_1))

                self.assertTrue(self.subchildnode1_1.is_contained_in_subtree(self.childnode1))
                self.assertTrue(self.subchildnode1_2.is_contained_in_subtree(self.childnode1))

                self.assertFalse(self.subchildnode1_1.is_contained_in_subtree(self.childnode2))

                self.assertTrue(self.childnode1.is_contained_in_subtree(self.tree))

        def test_is_root_of(self):
                self.assertTrue(self.tree.is_root_of(self.childnode1))
                self.assertTrue(self.tree.is_root_of(self.subchildnode1_1))

                self.assertTrue(self.childnode1.is_root_of(self.subchildnode1_1))
                self.assertFalse(self.childnode2.is_root_of(self.subchildnode1_1))

                self.assertFalse(self.childnode1.is_root_of(self.childnode2))
                self.assertFalse(self.childnode2.is_root_of(self.childnode1))


if __name__ == '__main__':
        unittest.main()
