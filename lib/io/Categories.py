# vim: expandtab softtabstop=0 list listchars=tab\:>-:
from lib.io.formatter import CategoryFormatter
from lib.io.parser import CategoryParser


def read(filename):
        categoryparser = CategoryParser()

        with open(filename, 'r') as f:
                line = f.readline()
                while line:
                        categoryparser.parse(line)

                        line = f.readline()

        return categoryparser.categorytree


def write(filename, categorytree, notfoundcategory):
        with open(filename, 'w') as f:
                for node in categorytree:
                        if not node.is_contained_in_subtree(notfoundcategory):
                                f.write(CategoryFormatter.format(node) + "\n")

                f.close()
