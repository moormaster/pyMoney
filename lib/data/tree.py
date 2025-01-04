# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
class TreeNode:
    def __init__(self, name):
        self._validate_name(name)

        self.parent = None
        self.name = name
        self.children = {}

    def _validate_name(self, name):
        if "." in name:
            raise Exception("name may not contain character .")

    def __iter__(self):
        return DFSIterator(self)

    def __str__(self, fullname=False):
        res = ""

        for node in self:
            res += node.format(fullname) + "\n"

        return res

    def format(self, fullname=False):
        _depth = "\t" * self.get_depth()

        if fullname:
            _name = self.get_full_name()
        else:
            _name = self.name

        return _depth + _name

    def append_childnode(self, node):
        assert isinstance(node, TreeNode)

        if node.name in self.children:
            raise DuplicateNodeException(self, node.name)

        self.children[node.name] = node
        node.parent = self

        return self.children[node.name]

    def remove_childnode_by_name(self, name):
        if not name in self.children:
            raise NoSuchNodeException(name)

        node = self.children[name]

        self.remove_childnode(node)

    def remove_childnode(self, node):
        if not node.name in self.children or node != self.children[node.name]:
            raise NodeIsNotAChildException(self, node)

        node.parent = None
        self.children.pop(node.name)

    def merge_from_node(self, sourcenode):
        if self.is_contained_in_subtree(sourcenode):
            raise TargetNodeIsPartOfSourceNodeSubTreeException(sourcenode, self)

        if sourcenode.parent is not None:
            sourcenode.parent.remove_childnode(sourcenode)

        children = []
        for c in sourcenode.children:
            children.append(sourcenode.children[c])

        for c in children:
            if c.name in self.children:
                self.children[c.name].merge_from_node(c)
            else:
                sourcenode.remove_childnode(c)
                self.append_childnode(c)

    def move_node_to(self, targetnode):
        if targetnode.is_contained_in_subtree(self):
            raise TargetNodeIsPartOfSourceNodeSubTreeException(targetnode, self)

        if self.parent is not None:
            self.parent.remove_childnode(self)

        targetnode.append_childnode(self)

    def rename(self, newnodename):
        self._validate_name(newnodename)
        
        parent = self.parent

        if parent:
            if newnodename in parent.children:
                raise DuplicateNodeException(parent, newnodename)

            parent.children.pop(self.name)
            parent.children[newnodename] = self

        self.name = newnodename

    def get_depth(self):
        if not self.parent:
            return 0
        else:
            return self.parent.get_depth() + 1

    def get_root(self):
        p = self

        while p.parent is not None:
            p = p.parent

        return p

    def find_nodes(self, name):
        l = []

        if name == self.name:
            l.append(self)
        else:
            for c in self.children.values():
                l = l + c.find_nodes(name)

        return l

    def find_nodes_by_relative_path(self, path):
        names = path.split(".")
        l = self.find_nodes(names[-1])

        for i in range(len(l)).__reversed__():
            match = True

            node = l[i]
            for j in range(len(names)).__reversed__():
                if node is None or node.name != names[j]:
                    match = False

                if not node is None:
                    node = node.parent

            if not match:
                l.pop(i)

        return l

    def find_first_node_by_relative_path(self, path):
        l = self.find_nodes_by_relative_path(path)

        if len(l) > 0:
            return l[0]

        return None

    def get_full_name(self):
        if self.parent:
            return self.parent.get_full_name() + "." + self.name
        else:
            return self.name

    def get_relative_name_to(self, ancestor):
        assert isinstance(ancestor, TreeNode)

        node = self
        name = self.name
        while not node is ancestor:
            node = node.parent
            name = node.name + "." + name

        return name

    def get_unique_name(self):
        root_node = self.get_root()

        matching_nodes = root_node.find_nodes(self.name)
        namestart_nodes = list(matching_nodes)

        namestart_node = self
        has_duplicates = len(matching_nodes) > 1

        while has_duplicates:
            names = []

            has_duplicates = False
            for i in range(len(namestart_nodes)):
                namestart_nodes[i] = namestart_nodes[i].parent
                nodename = matching_nodes[i].get_relative_name_to(namestart_nodes[i])
                if matching_nodes[i] is self:
                    namestart_node = namestart_nodes[i]

                if nodename in names:
                    has_duplicates = True
                names.append(nodename)

        return self.get_relative_name_to(namestart_node)

    def is_contained_in_subtree(self, node):
        if node is self:
            return True

        p = self
        while not p.parent is None:
            p = p.parent
            if node is p:
                return True
        return False

    def is_root_of(self, node):
        return node.is_contained_in_subtree(self)


class DFSIterator:
    def __init__(self, treenode):
        self.treenode = treenode
        self.nodestack = [treenode]

    def __iter__(self):
        return DFSIterator(self.treenode)

    def __next__(self):
        if not len(self.nodestack):
            raise StopIteration

        node = self.nodestack.pop(0)
        self.nodestack = list(node.children.values()) + self.nodestack

        return node


class DuplicateNodeException(Exception):
    def __init__(self, parentnode, name):
        assert isinstance(parentnode, TreeNode)

        Exception.__init__(self, name)
        self.parentnode = parentnode
        self.name = name


class NodeIsNotAChildException(Exception):
    def __init__(self, parentnode, node):
        assert isinstance(parentnode, TreeNode)
        assert isinstance(node, TreeNode)

        Exception.__init__(self, parentnode.name, node.name)
        self.parentnode = parentnode
        self.node = node


class NoSuchNodeException(Exception):
    def __init__(self, name):
        Exception.__init__(self, name)
        self.name = name


class TargetNodeIsPartOfSourceNodeSubTreeException(Exception):
    def __init__(self, sourcenode, targetnode):
        assert isinstance(sourcenode, TreeNode)
        assert isinstance(targetnode, TreeNode)

        Exception.__init__(self, sourcenode.name, targetnode.name)
        self.sourcenode = sourcenode
        self.targetnode = targetnode
