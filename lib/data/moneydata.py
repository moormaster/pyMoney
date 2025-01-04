# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import tree


class MoneyData:
    def __init__(self):
        self.categorytree = CategoryTreeNode("All")
        self.transactions = []
        self.paymentplans = {}

        self.notfoundcategoryname = "NOTFOUND"

        self.nextfreeindex = None

    def get_categories_iterator(self):
        return self.categorytree.__iter__()

    def get_transactions_iterator(self):
        return self.transactions.__iter__()

    def get_paymentplans_iterator(self):
        return self.paymentplans.values().__iter__()

    def filter_transactions(self, filter_func):
        return filter(filter_func, self.get_transactions_iterator())

    def create_new_index(self):
        if self.nextfreeindex is None:
            self.nextfreeindex = len(self.transactions)
        else:
            self.nextfreeindex += 1
        
        return self.nextfreeindex
    
    def import_transaction(self, transaction):
        transaction.index = self.create_new_index()
        self.transactions.append(transaction)

    def add_transaction(self, str_date, str_fromcategory, str_tocategory, str_amount, str_comment, force=False):
        try:
            self.get_category(str_fromcategory)
            self.get_category(str_tocategory)
        except NoSuchCategoryException as e:
            if not force:
                raise e

        newtransaction = self.parse_transaction(str_date, str_fromcategory, str_tocategory, str_amount, str_comment,
            force)
        self.import_transaction(newtransaction)

        return newtransaction

    def edit_transaction(self, index, str_date, str_fromcategory, str_tocategory, str_amount, str_comment):
        oldtransaction = self.transactions[index]

        newtransaction = self.parse_transaction(str_date, str_fromcategory, str_tocategory, str_amount, str_comment)
        self.transactions[index] = newtransaction
        newtransaction.index = index

        return newtransaction

    def delete_transaction(self, index):
        del self.transactions[index]

        for i in range(index, len(self.transactions)):
            self.transactions[i].index = i

        self.nextfreeindex = None

    def parse_transaction(self, str_date, str_categoryin, str_categoryout, str_amount, str_comment,
            autocreatenotfoundcategory=False, dateformat="%Y-%m-%d"):
        from lib.io.parser import TransactionParser
        parser = TransactionParser(self.categorytree, self.notfoundcategoryname, self.paymentplans, dateformat)
        parser.set_autocreatenotfoundcategory(autocreatenotfoundcategory)

        str_paymentplan = ""

        return parser.parse(str_date, str_categoryin, str_categoryout, str_paymentplan, str_amount, str_comment)

    def filter_categories(self, filter_func):
        return filter(filter_func, self.categorytree.__iter__())

    def get_category(self, name):
        nodes = self.categorytree.find_nodes_by_relative_path(name)

        if len(nodes) == 0:
            raise NoSuchCategoryException(name)

        if len(nodes) > 1:
            raise AmbiguousCategoryNameException(name, nodes)

        return nodes[0]

    def get_notfound_category(self):
        try:
            category = self.get_category(self.categorytree.name + "." + self.notfoundcategoryname)
        except NoSuchCategoryException:
            return None

        return category

    def category_is_contained_in_notfound_category(self, category):
        try:
            notfoundcategory = self.get_notfound_category()
        except NoSuchCategoryException:
            return False

        return category.is_contained_in_subtree(notfoundcategory)

    def add_category(self, parentname, name):
        notfoundcategory = self.get_notfound_category()
        category = None
        if not notfoundcategory is None:
            category = notfoundcategory.find_first_node_by_relative_path(name)
        parentcategory = self.get_category(parentname)

        if not category is None:
            raise DuplicateCategoryException(category)

        newcategory = CategoryTreeNode(name)
        parentcategory.append_childnode(newcategory)

        return newcategory

    def delete_category(self, name):
        node = self.get_category(name)

        if not node:
            raise NoSuchCategoryException(name)

        if not node.parent:
            raise CategoryIsTopCategoryException(node)

        # be sure that transactions keep their references to a valid category tree node
        original_unique_name = {}

        for t in self.get_transactions_iterator():
            if t.fromcategory.is_contained_in_subtree(node):
                original_unique_name[id(t.fromcategory)] = t.fromcategory.get_unique_name()

            if t.tocategory.is_contained_in_subtree(node):
                original_unique_name[id(t.tocategory)] = t.tocategory.get_unique_name()

        notfoundcategory = self.get_notfound_category()
        if len(original_unique_name) > 0 and notfoundcategory is None:
            notfoundcategory = self.categorytree.append_childnode(CategoryTreeNode(self.notfoundcategoryname))

        for t in self.get_transactions_iterator():
            if t.fromcategory.is_contained_in_subtree(node):
                t.fromcategory = notfoundcategory.append_by_relative_path(original_unique_name[id(t.fromcategory)])

            if t.tocategory.is_contained_in_subtree(node):
                t.tocategory = notfoundcategory.append_by_relative_path(original_unique_name[id(t.tocategory)])

        node.parent.remove_childnode(node)

    def rename_category(self, name, newname):
        category = self.get_category(name)
        notfoundcategory = self.get_notfound_category()
        newcategory = None
        if not notfoundcategory is None:
            newcategory = notfoundcategory.find_first_node_by_relative_path(newname)
            if not newcategory is None:
                raise DuplicateCategoryException(newcategory)

        if not category.parent is None and newname in category.parent.children:
            raise DuplicateCategoryException(category.parent.children[newname])

        if not newcategory is None:
            newcategory.parent.remove_childnode_by_name(newname)

        category.rename(newname)

    def merge_to_category(self, name, targetname):
        categories = []
        targetcategories = []

        categories.append(self.get_category(name))
        targetcategories.append(self.get_category(targetname))

        i = 0
        while i < len(categories):
            category = categories[i]
            targetcategory = targetcategories[i]

            for child in category.children:
                if child in targetcategory.children:
                    categories.append(category.children[child])
                    targetcategories.append(targetcategory.children[child])

            for t in self.get_transactions_iterator():
                if t.fromcategory is category:
                    t.fromcategory = targetcategory
                if t.tocategory is category:
                    t.tocategory = targetcategory

            for name in self.paymentplans:
                pp = self.paymentplans[name]

                if pp.fromcategory is category:
                    pp.fromcategory = targetcategory
                if pp.tocategory is category:
                    pp.tocategory = targetcategory

            i = i + 1

        category = categories[0]
        targetcategory = targetcategories[0]

        targetcategory.merge_from_node(category)

    def move_category(self, name, newparentname):
        node = self.get_category(name)
        newparent = self.get_category(newparentname)

        node.move_node_to(newparent)

    def parse_paymentplan(self, str_name, str_groupname, str_fromcategory, str_tocategory, str_amount, str_comment,
            autocreatenotfoundcategory=False):
        from lib.io.parser import PaymentPlanParser
        parser = PaymentPlanParser(self.categorytree, self.notfoundcategoryname)
        parser.set_autocreatenotfoundcategory(autocreatenotfoundcategory)

        return parser.parse(str_name, str_groupname, str_fromcategory, str_tocategory, str_amount, str_comment)

    def import_paymentplan(self, paymentplan):
        self.paymentplans[paymentplan.name] = paymentplan

    def add_paymentplan(self, str_name, str_groupname, str_fromcategory, str_tocategory, str_amount, str_comment, force=False):
        try:
            self.get_category(str_fromcategory)
            self.get_category(str_tocategory)
        except NoSuchCategoryException as e:
            if not force:
                raise e

        if str_name in self.paymentplans:
            raise DuplicatePaymentPlanException(self.paymentplans[str_name])

        newpaymentplan = self.parse_paymentplan(str_name, str_groupname, str_fromcategory, str_tocategory, str_amount, str_comment,
            force)
        self.import_paymentplan(newpaymentplan)

        return newpaymentplan

    def edit_paymentplan(self, name, str_groupname, str_fromcategory, str_tocategory, str_amount, str_comment):
        if not name in self.paymentplans:
            raise NoSuchPaymentPlanException(name)

        oldpaymentplan = self.paymentplans[name]
        paymentplan = self.parse_paymentplan(name, str_groupname, str_fromcategory, str_tocategory, str_amount, str_comment)

        for t in self.get_transactions_iterator():
            if t.paymentplan is oldpaymentplan:
                t.paymentplan = paymentplan
        self.paymentplans[name] = paymentplan

        return paymentplan

    def get_paymentplan(self, name):
        if not name in self.paymentplans:
            raise NoSuchPaymentPlanException(name)

        return self.paymentplans[name]

    def get_paymentplannames(self):
        return list(self.paymentplans)

    def get_paymentplangroupnames(self):
        groupnames = []
        is_part_of_groupnames_list = {}

        for name in self.paymentplans:
            paymentplan = self.paymentplans[name]
            groupname = paymentplan.groupname

            if not groupname in is_part_of_groupnames_list:
                groupnames.append(groupname)
                is_part_of_groupnames_list[groupname] = True

        return groupnames

    def find_similar_paymentplans(self, str_fromcategory, str_tocategory, str_amount):
        try:
            self.get_category(str_fromcategory)
            self.get_category(str_tocategory)
        except NoSuchCategoryException as e:
            raise e

        parsedpaymentplan = self.parse_paymentplan("noname", "nogroup", str_fromcategory, str_tocategory, str_amount, "", False)

        result = []
        for paymentplan in self.get_paymentplans_iterator():
            if not paymentplan.fromcategory is parsedpaymentplan.fromcategory:
                continue
            if not paymentplan.tocategory is parsedpaymentplan.tocategory:
                continue
            if not paymentplan.amount == parsedpaymentplan.amount:
                continue

            result.append(paymentplan)

        return result

    def delete_paymentplan(self, name):
        if not name in self.paymentplans:
            raise NoSuchPaymentPlanException(name)

        paymentplan = self.paymentplans.pop(name)

        for t in self.get_transactions_iterator():
            if t.paymentplan is paymentplan:
                t.paymentplan = None

    def rename_paymentplan(self, name, newname):
        if not name in self.paymentplans:
            raise NoSuchPaymentPlanException(name)

        if newname in self.paymentplans and name != newname:
            raise DuplicatePaymentPlanException(self.paymentplans[newname])

        paymentplan = self.paymentplans[name]
        del self.paymentplans[name]

        paymentplan.name = newname
        self.paymentplans[newname] = paymentplan

        return paymentplan

    def move_paymentplan(self, name, newgroupname):
        if not name in self.paymentplans:
            raise NoSuchPaymentPlanException(name)

        paymentplan = self.paymentplans[name]
        paymentplan.groupname = newgroupname

        return paymentplan

    def execute_paymentplan(self, name, str_date, amount=None, str_comment=None):
        if not name in self.paymentplans:
            raise NoSuchPaymentPlanException(name)

        paymentplan = self.paymentplans[name]

        if amount is None:
            amount = paymentplan.amount

        if str_comment is None or len(str_comment) == 0:
            str_comment = paymentplan.comment

        transaction = self.parse_transaction(str_date, paymentplan.fromcategory.get_unique_name(), paymentplan.tocategory.get_unique_name(), amount, str_comment)
        transaction.paymentplan = paymentplan
        self.import_transaction(transaction)

        return transaction

    def create_summary(self, transactionfilter, paymentplanfilter, d_summary=None):
        if d_summary is None:
            d_summary = {}  # resulting map unqique category name -> NodeSummary() object
        d_unique_name = {}      # cached category.get_unique_name() results

        fp_correction_factor = 100      # factor by which each summands gets multiplied before addition - and by which the sum gets divided again
                        # to prevent floating point errors (like sum([0.01]*6) being not equal to 0.06)

        for key in d_summary:
            d_summary[key].amount *= fp_correction_factor
            d_summary[key].amountin *= fp_correction_factor
            d_summary[key].amountout *= fp_correction_factor

            d_summary[key].sum *= fp_correction_factor
            d_summary[key].sumin *= fp_correction_factor
            d_summary[key].sumout *= fp_correction_factor

        for c in self.categorytree:
            unique_name = c.get_unique_name()
            d_unique_name[id(c)] = unique_name
            if not unique_name in d_summary:
                d_summary[unique_name] = NodeSummary()

        for t in self.get_transactions_iterator():
            if not transactionfilter(t):
                continue

            fromkey = d_unique_name[id(t.fromcategory)]
            tokey = d_unique_name[id(t.tocategory)]

            d_summary[fromkey].amountout -= t.amount * fp_correction_factor
            d_summary[fromkey].amount -= t.amount * fp_correction_factor

            d_summary[tokey].amountin += t.amount * fp_correction_factor
            d_summary[tokey].amount += t.amount * fp_correction_factor

            c = t.fromcategory
            while not c is None:
                key = d_unique_name[id(c)]
                d_summary[key].sumcountout = d_summary[key].sumcountout + 1
                d_summary[key].sumcount = d_summary[key].sumcount + 1
                if t.fromcategory.is_contained_in_subtree(c) and not t.tocategory.is_contained_in_subtree(c):
                    d_summary[key].sumout -= t.amount * fp_correction_factor
                    d_summary[key].sum -= t.amount * fp_correction_factor
                c = c.parent

            c = t.tocategory
            while not c is None:
                key = d_unique_name[id(c)]
                d_summary[key].sumcountin = d_summary[key].sumcountin + 1
                d_summary[key].sumcount = d_summary[key].sumcount + 1
                if not t.fromcategory.is_contained_in_subtree(c) and t.tocategory.is_contained_in_subtree(c):
                    d_summary[key].sumin += t.amount * fp_correction_factor
                    d_summary[key].sum += t.amount * fp_correction_factor
                c = c.parent

        for name in self.paymentplans:
            pp = self.paymentplans[name]

            if not paymentplanfilter(pp):
                continue

            c = pp.fromcategory
            while not c is None:
                key = d_unique_name[id(c)]
                d_summary[key].paymentplancountout = d_summary[key].paymentplancountout + 1
                d_summary[key].paymentplancount = d_summary[key].paymentplancount + 1
                c = c.parent

            c = pp.tocategory
            while not c is None:
                key = d_unique_name[id(c)]
                d_summary[key].paymentplancountin = d_summary[key].paymentplancountin + 1
                d_summary[key].paymentplancount = d_summary[key].paymentplancount + 1
                c = c.parent

        for key in d_summary:
            d_summary[key].amount /= fp_correction_factor
            d_summary[key].amountin /= fp_correction_factor
            d_summary[key].amountout /= fp_correction_factor

            d_summary[key].sum /= fp_correction_factor
            d_summary[key].sumin /= fp_correction_factor
            d_summary[key].sumout /= fp_correction_factor

        return d_summary

    def create_paymentplan_summary(self, paymentplanfilter, factor, d_summary=None):
        if d_summary is None:
            d_summary = {}  # resulting map unqique category name -> NodeSummary() object
        d_unique_name = {}      # cached category.get_unique_name() results

        fp_correction_factor = 100      # factor by which each summands gets multiplied before addition - and by which the sum gets divided again
                        # to prevent floating point errors (like sum([0.01]*6) being not equal to 0.06)

        for key in d_summary:
            d_summary[key].amount *= fp_correction_factor
            d_summary[key].amountin *= fp_correction_factor
            d_summary[key].amountout *= fp_correction_factor

            d_summary[key].sum *= fp_correction_factor
            d_summary[key].sumin *= fp_correction_factor
            d_summary[key].sumout *= fp_correction_factor

        for c in self.categorytree:
            unique_name = c.get_unique_name()
            d_unique_name[id(c)] = unique_name
            if not unique_name in d_summary:
                d_summary[unique_name] = NodeSummary()

        for pp in self.get_paymentplans_iterator():
            if not paymentplanfilter(pp):
                continue

            fromkey = d_unique_name[id(pp.fromcategory)]
            tokey = d_unique_name[id(pp.tocategory)]

            d_summary[fromkey].amountout -= pp.amount * fp_correction_factor * factor
            d_summary[fromkey].amount -= pp.amount * fp_correction_factor * factor

            d_summary[tokey].amountin += pp.amount * fp_correction_factor * factor
            d_summary[tokey].amount += pp.amount * fp_correction_factor * factor

            c = pp.fromcategory
            while not c is None:
                key = d_unique_name[id(c)]
                d_summary[key].paymentplancountout = d_summary[key].paymentplancountout + 1
                d_summary[key].paymentplancount = d_summary[key].paymentplancount + 1
                d_summary[key].sumcountout = d_summary[key].sumcountout + 1
                d_summary[key].sumcount = d_summary[key].sumcount + 1
                d_summary[key].sumout -= pp.amount * fp_correction_factor * factor
                d_summary[key].sum -= pp.amount * fp_correction_factor * factor
                c = c.parent

            c = pp.tocategory
            while not c is None:
                key = d_unique_name[id(c)]
                d_summary[key].paymentplancountin = d_summary[key].paymentplancountin + 1
                d_summary[key].paymentplancount = d_summary[key].paymentplancount + 1
                d_summary[key].sumcountin = d_summary[key].sumcountin + 1
                d_summary[key].sumcount = d_summary[key].sumcount + 1
                d_summary[key].sumin += pp.amount * fp_correction_factor * factor
                d_summary[key].sum += pp.amount * fp_correction_factor * factor
                c = c.parent

        for key in d_summary:
            d_summary[key].amount /= fp_correction_factor
            d_summary[key].amountin /= fp_correction_factor
            d_summary[key].amountout /= fp_correction_factor

            d_summary[key].sum /= fp_correction_factor
            d_summary[key].sumin /= fp_correction_factor
            d_summary[key].sumout /= fp_correction_factor

        return d_summary


class Transaction(object):
    fields = ["index", "date", "fromcategory", "tocategory", "paymentplan", "amount", "comment"]
    __slots__ = fields

    def __init__(self, index, date, fromcategory, tocategory, amount, comment):
        assert (isinstance(fromcategory, CategoryTreeNode))
        assert (isinstance(tocategory, CategoryTreeNode))

        self.index = index
        self.date = date
        self.fromcategory = fromcategory
        self.tocategory = tocategory
        self.paymentplan = None
        self.amount = amount
        self.comment = comment

    def __str__(self):
        return str(self.index) + " " + str(self.date) + " " + self.fromcategory.get_unique_name() + " " + self.tocategory.get_unique_name() + " " + str(self.amount) + " " + self.comment


class PaymentPlan(object):
    fields = ["name", "groupname", "fromcategory", "tocategory", "amount", "comment"]
    __slots__ = fields

    def __init__(self, name, groupname, fromcategory, tocategory, amount, comment):
        assert(isinstance(fromcategory, CategoryTreeNode))
        assert(isinstance(tocategory, CategoryTreeNode))

        self.name = name
        self.groupname = groupname
        self.fromcategory = fromcategory
        self.tocategory = tocategory
        self.amount = amount
        self.comment = comment

    def __str__(self):
        return self.name + " " + self.groupname + " " + self.fromcategory.get_unique_name() + " " + self.tocategory.get_unique_name() + " " + str(self.amount) + " " + self.comment


class NodeSummary(object):
    __slots__ = ["amountin", "amountout", "amount", "sumcountin", "sumcountout", "sumcount", "paymentplancountin", "paymentplancountout", "paymentplancount", "sumin", "sumout", "sum"]

    def __init__(self):
        self.amountin = 0
        self.amountout = 0
        self.amount = 0

        self.sumcountin = 0
        self.sumcountout = 0
        self.sumcount = 0

        self.paymentplancountin = 0
        self.paymentplancountout = 0
        self.paymentplancount = 0

        self.sumin = 0
        self.sumout = 0
        self.sum = 0

        pass


class CategoryTreeNode(tree.TreeNode):
    def __init__(self, name):
        tree.TreeNode.__init__(self, name)

    def _validate_name(self, name):
        if "." in name:
            raise InvalidCategoryNameException(name)

    def append_by_relative_path(self, path):
        if len(path) == 0:
            return self

        node_names = path.split(".")

        category = self
        for i in range(len(node_names)):
            if node_names[i] in category.children:
                category = category.children[node_names[i]]
            else:
                category = category.append_childnode(CategoryTreeNode(node_names[i]))

        return category

    def append_childnode(self, node):
        assert isinstance(node, CategoryTreeNode)

        root_node = self.get_root()

        if node.name == root_node.name:
            raise DuplicateCategoryException(root_node)

        if node.name in self.children:
            raise DuplicateCategoryException(self.children[node.name])

        return tree.TreeNode.append_childnode(self, node)

    def format(self, fullname=False):
        _depth = "  " * self.get_depth()

        if fullname:
            _name = self.get_full_name()
        else:
            _name = self.name

        return _depth + _name


class AmbiguousCategoryNameException(Exception):
    def __init__(self, name, matching_categories):
        for c in matching_categories:
            assert isinstance(c, CategoryTreeNode)

        Exception.__init__(self, name, matching_categories)

        self.name = name
        self.matching_categories = matching_categories


class DuplicateCategoryException(Exception):
    def __init__(self, category):
        assert isinstance(category, CategoryTreeNode)

        Exception.__init__(self, category.get_unique_name())

        self.category = category


class InvalidCategoryNameException(Exception):
    def __init__(self, name):
        self.name = name


class NoSuchCategoryException(tree.NoSuchNodeException):
    def __init__(self, name):
        tree.NoSuchNodeException.__init__(self, name)


class CategoryIsTopCategoryException(Exception):
    def __init__(self, category):
        assert isinstance(category, CategoryTreeNode)

        Exception.__init__(self, category.get_unique_name())

        self.category = category


class DuplicatePaymentPlanException(Exception):
    def __init__(self, paymentplan):
        assert isinstance(paymentplan, PaymentPlan)

        Exception.__init__(self, paymentplan.name)

        self.paymentplan = paymentplan


class NoSuchPaymentPlanException(Exception):
    def __init__(self, name):
        Exception.__init__(self, name)

        self.name = name
