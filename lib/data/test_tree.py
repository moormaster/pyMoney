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

	def test___iter__(self):
		l = list(self.tree)

		expected_set = {self.tree, self.childnode1, self.subchildnode1_1, self.subchildnode1_2, self.childnode2,
						self.subchildnode2_1, self.subchildnode2_2}
		self.assertSetEqual(expected_set, set(l))

		self.assertTrue(l[0] is self.tree)

		self.assertTrue(l[1] is self.childnode1 or l[1] is self.childnode2)
		self.assertTrue(l[4] is self.childnode1 or l[4] is self.childnode2)

		if l[1] is self.childnode1:
			self.assertTrue(l[2] is self.subchildnode1_1 or l[2] is self.subchildnode1_2)
			self.assertTrue(l[3] is self.subchildnode1_1 or l[3] is self.subchildnode1_2)

			self.assertTrue(l[5] is self.subchildnode2_1 or l[5] is self.subchildnode2_2)
			self.assertTrue(l[6] is self.subchildnode2_1 or l[6] is self.subchildnode2_2)
		else:
			self.assertTrue(l[2] is self.subchildnode2_1 or l[2] is self.subchildnode2_2)
			self.assertTrue(l[3] is self.subchildnode2_1 or l[3] is self.subchildnode2_2)

			self.assertTrue(l[5] is self.subchildnode1_1 or l[5] is self.subchildnode1_2)
			self.assertTrue(l[6] is self.subchildnode1_1 or l[6] is self.subchildnode1_2)

	def test_format(self):
		self.assertRegex(self.tree.format(), "[\t]{0}[^\t]*")
		self.assertRegex(self.childnode1.format(), "[\t]{1}[^\t]*")
		self.assertRegex(self.childnode2.format(), "[\t]{1}[^\t]*")
		self.assertRegex(self.subchildnode1_1.format(), "[\t]{2}[^\t]*")

	def test_append_childnode(self):
		self.assertRaises(AssertionError, self.tree.append_childnode, object())

		node = self.tree.append_childnode(tree.TreeNode("Child"))

		self.assertTrue(node is not None)
		self.assertEqual(node.parent, self.tree)

		subnode = node.append_childnode(tree.TreeNode("SubChild"))

		self.assertTrue(subnode is not None)
		self.assertEqual(subnode.parent, node)

	def test_remove_childnode_by_name(self):
		self.assertRaisesRegex(tree.NoSuchNodeException, "NoChild", self.tree.remove_childnode_by_name, "NoChild")

		self.tree.remove_childnode_by_name("Child1")

		self.assertEqual(self.tree.find_first_node_by_relative_path("Child1"), None)
		self.assertNotEqual(self.tree.find_first_node_by_relative_path("SubChild1"), self.subchildnode1_1)
		self.assertEqual(self.tree.find_first_node_by_relative_path("Child2"), self.childnode2)

	def test_remove_childnode(self):
		self.assertRaisesRegex(tree.NodeIsNotAChildException, "('All', 'NoChild')",
			self.tree.remove_childnode, tree.TreeNode("NoChild"))

		self.tree.remove_childnode(self.childnode1)

		self.assertEqual(self.tree.find_first_node_by_relative_path("Child1"), None)
		self.assertNotEqual(self.tree.find_first_node_by_relative_path("SubChild1"), self.subchildnode1_1)
		self.assertEqual(self.tree.find_first_node_by_relative_path("Child2"), self.childnode2)

	def test_merge(self):
		sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
		targetcategory = self.tree.find_first_node_by_relative_path("Child1.SubChild1")

		assert isinstance(sourcecategory, tree.TreeNode)
		assert isinstance(targetcategory, tree.TreeNode)

		self.assertRaisesRegex(tree.TargetNodeIsPartOfSourceNodeSubTreeException, "('Child1', 'SubChild1')",
			targetcategory.merge_to_node, sourcecategory)

		sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
		targetcategory = self.tree.find_first_node_by_relative_path("Child2")

		subcategories = targetcategory.children

		targetcategory.merge_to_node(sourcecategory)

		self.assertEqual(len(subcategories), 2)
		for category in subcategories:
			self.assertEqual(subcategories[category].parent, targetcategory)

	def test_move_to(self):
		sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
		targetcategory = self.tree.find_first_node_by_relative_path("Child1.SubChild1")

		assert isinstance(sourcecategory, tree.TreeNode)
		assert isinstance(targetcategory, tree.TreeNode)

		self.assertRaisesRegex(tree.TargetNodeIsPartOfSourceNodeSubTreeException, "('SubChild1', 'Child1')",
			sourcecategory.move_node_to, targetcategory)

		sourcecategory = self.tree.find_first_node_by_relative_path("Child1")
		targetcategory = self.tree.find_first_node_by_relative_path("Child2")

		sourcecategory.move_node_to(targetcategory)

		self.assertEqual(sourcecategory.parent, targetcategory)

	def test_rename(self):
		self.subchildnode1_1.rename("renamed")

		self.assertEqual(self.subchildnode1_1.name, "renamed")
		self.assertEqual(self.tree.find_first_node_by_relative_path("renamed"), self.subchildnode1_1)

	def test_get_depth(self):
		self.assertEqual(self.tree.get_depth(), 0)
		self.assertEqual(self.childnode1.get_depth(), 1)
		self.assertEqual(self.subchildnode1_1.get_depth(), 2)

	def test_get_root(self):
		self.assertEqual(self.tree.get_root(), self.tree)
		self.assertEqual(self.childnode1.get_root(), self.tree)
		self.assertEqual(self.subchildnode1_1.get_root(), self.tree)

	def test_find_first_node_by_relative_path(self):
		node = self.tree.find_first_node_by_relative_path("Child1.SubChild1")
		selfnode = self.subchildnode1_1.find_first_node_by_relative_path("SubChild1")
		notfoundnode = self.tree.find_first_node_by_relative_path("NoChild")

		self.assertEqual(node, self.subchildnode1_1)
		self.assertEqual(selfnode, self.subchildnode1_1)
		self.assertEqual(notfoundnode, None)

	def test_find_nodes_by_relative_path(self):
		nodelist = self.tree.find_nodes_by_relative_path("SubChild1")
		selfnodelist = self.subchildnode1_1.find_nodes_by_relative_path("SubChild1")
		notfoundnodelist = self.tree.find_nodes_by_relative_path("NoChild")

		self.assertEqual(len(nodelist), 2)
		self.assertSetEqual(set(nodelist), {self.subchildnode1_1, self.subchildnode2_1})
		self.assertEqual(len(selfnodelist), 1)
		self.assertEqual(selfnodelist[0], self.subchildnode1_1)
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
