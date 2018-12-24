# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import tree

import unittest


class TestTreeNode(unittest.TestCase):
        def setUp(self):
            self.treeRoot = tree.TreeNode("Root")

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
                child1 = self.treeRoot.append_childnode(tree.TreeNode("Child1"))
                child2 = self.treeRoot.append_childnode(tree.TreeNode("Child2"))
                node = child1.append_childnode(tree.TreeNode("Node"))

                self.assertRegex(self.treeRoot.format(), "[\t]{0}[^\t]*")
                self.assertRegex(child1.format(), "[\t]{1}[^\t]*")
                self.assertRegex(child2.format(), "[\t]{1}[^\t]*")
                self.assertRegex(node.format(), "[\t]{2}[^\t]*")

        def test_append_childnode_should_raise_an_exception_if_parameter_is_not_a_TreeNode_object(self):

                self.assertRaises(AssertionError, self.treeRoot.append_childnode, object())

        def test_append_childnode_should_set_parent_of_child_node(self):
                node = self.treeRoot.append_childnode(tree.TreeNode("Child"))

                self.assertIs(node.parent, self.treeRoot)

        def test_append_childnode_should_insert_node_into_children_dictionary(self):
                node = self.treeRoot.append_childnode(tree.TreeNode("Child"))

                self.assertIs(self.treeRoot.children[node.name], node)
                self.assertIs(self.treeRoot.find_first_node_by_relative_path("Child"), node)

        def test_remove_childnode_by_name_should_raise_an_exception_if_node_was_not_found(self):

                self.assertRaisesRegex(tree.NoSuchNodeException, "Unknown", self.treeRoot.remove_childnode_by_name, "Unknown")

        def test_remove_childnode_by_name_should_remove_the_given_childnode(self):
                childNode = self.treeRoot.append_childnode(tree.TreeNode("Child"))

                self.treeRoot.remove_childnode_by_name("Child")

                self.assertIsNone(childNode.parent)
                self.assertIsNone(self.treeRoot.find_first_node_by_relative_path("Child"))

        def test_remove_childnode_should_raise_an_exception_if_the_given_node_is_not_a_child(self):

                self.assertRaisesRegex(tree.NodeIsNotAChildException, "('Root', 'NotAChild')",
                        self.treeRoot.remove_childnode, tree.TreeNode("NotAChild"))

        def test_remove_childnode_should_remove_the_given_childnode(self):
                childNode = self.treeRoot.append_childnode(tree.TreeNode("Child"))

                self.treeRoot.remove_childnode(childNode)

                self.assertIsNone(childNode.parent)
                self.assertIsNone(self.treeRoot.find_first_node_by_relative_path("Child"))

        def test_merge_from_node_should_raise_an_exception_if_targetnode_is_a_descendant_of_self(self):
                childNode = self.treeRoot.append_childnode(tree.TreeNode("Child"))

                self.assertRaisesRegex(tree.TargetNodeIsPartOfSourceNodeSubTreeException, "('Root', 'Child')",
                        childNode.merge_from_node, self.treeRoot)

        def test_merge_from_node_should_remove_source_node(self):
                source = self.treeRoot.append_childnode(tree.TreeNode("Source"))
                target = self.treeRoot.append_childnode(tree.TreeNode("Target"))

                target.merge_from_node(source)

                self.assertIsNone(source.parent)
                self.assertIsNone(self.treeRoot.find_first_node_by_relative_path("Source"))

        def test_merge_from_node_should_merge_all_descendant_categories_of_source_node_with_descendand_categories_of_the_target_node(self):
                self.treeRoot= tree.TreeNode("Root")
                source = self.treeRoot.append_childnode(tree.TreeNode("Source"))
                sourcechild = source.append_childnode(tree.TreeNode("SourceChild"))
                sourcecommonchild = source.append_childnode(tree.TreeNode("CommonChild"))
                target = self.treeRoot.append_childnode(tree.TreeNode("Target"))
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
                node = self.treeRoot.append_childnode(tree.TreeNode("Node"))
                child = node.append_childnode(tree.TreeNode("Child"))

                self.assertRaisesRegex(tree.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child', 'Node')",
                        node.move_node_to, child)

        def test_move_node_to_should_change_parent_to_the_given_one(self):
                node1 = self.treeRoot.append_childnode(tree.TreeNode("Node1"))
                node2 = self.treeRoot.append_childnode(tree.TreeNode("Node2"))

                node2.move_node_to(node1)

                self.assertIs(node2.parent, node1)

        def test_rename(self):
                node = self.treeRoot.append_childnode(tree.TreeNode("Node"))

                node.rename("renamed")

                self.assertEqual(node.name, "renamed")
                self.assertIs(self.treeRoot.find_first_node_by_relative_path("renamed"), node)

        def test_get_depth(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                subchild = child.append_childnode(tree.TreeNode("SubChild"))

                self.assertEqual(self.treeRoot.get_depth(), 0)
                self.assertEqual(child.get_depth(), 1)
                self.assertEqual(subchild.get_depth(), 2)

        def test_get_root(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                subchild = child.append_childnode(tree.TreeNode("SubChild"))

                self.assertIs(self.treeRoot.get_root(), self.treeRoot)
                self.assertIs(child.get_root(), self.treeRoot)
                self.assertIs(subchild.get_root(), self.treeRoot)

        def test_find_first_node_by_relative_path_should_find_itself(self):
                node = self.treeRoot.find_first_node_by_relative_path("Root")

                self.assertIs(node, self.treeRoot)

        def test_find_first_node_by_relative_path_should_find_a_node_by_unique_path(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                subchild = child.append_childnode(tree.TreeNode("SubChild"))

                node = self.treeRoot.find_first_node_by_relative_path("Child.SubChild")

                self.assertIs(node, subchild)

        def test_find_first_node_by_relative_path_should_return_None_when_a_node_was_not_found(self):
                node = self.treeRoot.find_first_node_by_relative_path("Unknown")

                self.assertIsNone(node)

        def test_find_nodes_by_relative_path_should_return_all_nodes_whose_paths_ends_with_the_given_relative_path(self):
                child1 = self.treeRoot.append_childnode(tree.TreeNode("Child1"))
                child2 = self.treeRoot.append_childnode(tree.TreeNode("Child2"))
                ambiguous1 = child1.append_childnode(tree.TreeNode("Ambiguous"))
                ambiguous2 = child2.append_childnode(tree.TreeNode("Ambiguous"))
                path1 = ambiguous1.append_childnode(tree.TreeNode("Path"))
                path2 = ambiguous2.append_childnode(tree.TreeNode("Path"))

                nodelist = self.treeRoot.find_nodes_by_relative_path("Ambiguous.Path")

                self.assertSetEqual(set(nodelist), {path1, path2})

        def test_find_nodes_by_relative_path_should_return_an_empty_list_for_not_existing_node(self):
                nodelist = self.treeRoot.find_nodes_by_relative_path("Unknown")

                self.assertEqual(nodelist, [])

        def test_find_nodes_should_return_an_empty_list_for_not_existing_node(self):
                nodelist = self.treeRoot.find_nodes("Unknown")

                self.assertEqual(nodelist, [])

        def test_find_nodes_should_return_list_of_matching_nodes(self):
                child1 = self.treeRoot.append_childnode(tree.TreeNode("Child1"))
                child2 = self.treeRoot.append_childnode(tree.TreeNode("Child2"))
                node1 = child1.append_childnode(tree.TreeNode("Node"))
                node2= child2.append_childnode(tree.TreeNode("Node"))

                nodelist = self.treeRoot.find_nodes("Node")

                self.assertSetEqual(set(nodelist), {node1, node2})

        def test_get_full_name_should_return_absolute_path(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                node = child.append_childnode(tree.TreeNode("Node"))

                self.assertEqual(node.get_full_name(), "Root.Child.Node")

        def test_is_contained_in_subtree_should_return_false_for_sibling(self):
                child1 = self.treeRoot.append_childnode(tree.TreeNode("Child1"))
                child2 = self.treeRoot.append_childnode(tree.TreeNode("Child2"))

                self.assertFalse(child1.is_contained_in_subtree(child2))

        def test_is_contained_in_subtree_shoud_return_false_for_one_of_its_descendants(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                node = child.append_childnode(tree.TreeNode("Node"))

                self.assertFalse(self.treeRoot.is_contained_in_subtree(node))
                self.assertFalse(self.treeRoot.is_contained_in_subtree(child))


        def test_is_contained_in_subtree_should_return_true_for_one_of_its_parent(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                node = child.append_childnode(tree.TreeNode("Node"))

                self.assertTrue(node.is_contained_in_subtree(child))
                self.assertTrue(node.is_contained_in_subtree(self.treeRoot))

        def test_is_root_of_should_return_false_for_sibling(self):
                child1 = self.treeRoot.append_childnode(tree.TreeNode("Child1"))
                child2 = self.treeRoot.append_childnode(tree.TreeNode("Child2"))

                self.assertFalse(child1.is_root_of(child2))

        def test_is_root_of_should_return_false_for_one_of_its_parents(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                node = child.append_childnode(tree.TreeNode("Node"))

                self.assertFalse(node.is_root_of(child))
                self.assertFalse(node.is_root_of(self.treeRoot))

        def test_is_root_of_should_return_true_for_one_of_its_descendants(self):
                child = self.treeRoot.append_childnode(tree.TreeNode("Child"))
                node = child.append_childnode(tree.TreeNode("Node"))

                self.assertTrue(self.treeRoot.is_root_of(child))
                self.assertTrue(self.treeRoot.is_root_of(node))


if __name__ == '__main__':
        unittest.main()
