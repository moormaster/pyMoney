# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data.moneydata import CategoryTreeNode


class CategoryFormatter:
        def __init__(self):
                pass

        @staticmethod
        def format(category):
                assert (isinstance(category, CategoryTreeNode))

                return "\t" * category.get_depth() + category.name


class TransactionFormatter:
        def __init__(self):
                pass

        @staticmethod
        def format(transaction, notfoundcategory):
                if not notfoundcategory is None and transaction.fromcategory.is_contained_in_subtree(notfoundcategory):
                        str_fromcategory = transaction.fromcategory.get_relative_name_to(notfoundcategory)
                        str_fromcategory = str_fromcategory[len(notfoundcategory.name) + 1:]
                else:
                        str_fromcategory = transaction.fromcategory.get_unique_name()

                if not notfoundcategory is None and transaction.tocategory.is_contained_in_subtree(notfoundcategory):
                        str_tocategory = transaction.tocategory.get_relative_name_to(notfoundcategory)
                        str_tocategory = str_tocategory[len(notfoundcategory.name) + 1:]
                else:
                        str_tocategory = transaction.tocategory.get_unique_name()

                return {"date": str(transaction.date),
                                "fromcategory": str_fromcategory,
                                "tocategory": str_tocategory,
                                "amount": str(transaction.amount),
                                "comment": transaction.comment}
