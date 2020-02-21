#!/usr/bin/python3
# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:

import lib.app
import lib.argparse
import lib.formatter
import lib.data
import lib.data.daterange
import lib.data.filterchain
import lib.data.moneydata
import lib.data.tree
import lib.io

import argparse
import calendar
import cmd
import datetime
import shlex
import sys


class PyMoneyCompletion:
        def __init__(self, pyMoney):
                self.pyMoney = pyMoney

        def complete_transaction(self, text, line, begidx, endidx):
                if endidx < len(line):
                        return

                argv = shlex.split(line)

                if len(argv) == 1 or line.endswith(' '):
                        argv.append('')

                if len(argv) >= 2:
                        if argv[1] == 'add':
                                # from-category, to-category
                                if len(argv) == 4 or len(argv) == 5:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)

                                # comment
                                if len(argv) == 7:
                                        searchstring = argv[-1]

                                        def unescapespaces(s):
                                                return s.replace("\\ ", " ")

                                        def escapespaces(s):
                                                return s.replace(" ", "\\ ")

                                        transactions = self.pyMoney.get_moneydata().get_transactions_iterator()
                                        comments = map(lambda t: t.comment, transactions)
                                        comments = list(set(filter(lambda c: c.startswith(unescapespaces(searchstring)), comments)))

                                        if len(comments) == 1:
                                                pos = unescapespaces(searchstring).rfind(" ")
                                                if pos > 0:
                                                        comments[0] = comments[0][pos+1:]

                                        comments = list(map(escapespaces, comments))
                                        return comments

                        elif argv[1] == 'edit':
                                # from-category, to-category
                                if len(argv) == 5 or len(argv) == 6:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)

                                if len(argv) == 8:
                                        searchstring = argv[-1]

                                        def unescapespaces(s):
                                                return s.replace("\\ ", " ")

                                        def escapespaces(s):
                                                return s.replace(" ", "\\ ")

                                        transactions = self.pyMoney.get_moneydata().get_transactions_iterator()
                                        comments = map(lambda t: t.comment, transactions)
                                        comments = list(set(filter(lambda c: c.startswith(unescapespaces(searchstring)), comments)))

                                        if len(comments) == 1:
                                                pos = unescapespaces(searchstring).rfind(" ")
                                                if pos > 0:
                                                        comments[0] = comments[0][pos+1:]

                                        comments = list(map(escapespaces, comments))
                                        return comments

                        elif argv[1] == 'list':
                                parameters = ['after', 'after-or-from', 'before', 'before-or-from', 'from', 'category', 'fromcategory', 'tocategory', 'nopaymentplans', 'paymentplansonly', 'paymentplan', 'paymentplangroup']

                                if argv[-2] in ['--category', '--fromcategory', '--tocategory']:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                                elif argv[-2] == '--paymentplan':
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                                elif argv[-2] == '--paymentplangroup':
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                                elif len(argv) >= 3:
                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        elif argv[-1].startswith('-'):
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '-'+v, parameters))))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        elif len(argv) == 2:
                                return list(filter(lambda v: v.startswith(argv[-1]), ['add', 'edit', 'delete', 'list']))

        def complete_category(self, text, line, begidx, endidx):
                if endidx < len(line):
                        return

                argv = shlex.split(line)

                if len(argv) == 1 or line.endswith(' '):
                        argv.append('')

                if len(argv) >= 2:
                        if argv[1] == 'add':
                                # parent-category
                                if len(argv) == 3:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                        elif argv[1] == 'delete' or argv[1] == 'rename':
                                # category
                                if len(argv) == 3:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                        elif argv[1] == 'merge' or argv[1] == 'move':
                                # category, target-category
                                if len(argv) == 3 or len(argv) == 4:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                        elif argv[1] == 'list' or argv[1] == 'tree':
                                if len(argv) == 3:
                                        parameters = ['fullnamecategories']

                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        elif argv[-1].startswith('-'):
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '-'+v, parameters))))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        elif len(argv) == 2:
                                return list(filter(lambda v: v.startswith(argv[-1]), ['add', 'delete', 'list', 'merge', 'move', 'rename', 'tree']))

        def complete_paymentplan(self, text, line, begidx, endidx):
                if endidx < len(line):
                        return

                argv = shlex.split(line)

                if len(argv) == 1 or line.endswith(' '):
                        argv.append('')

                if len(argv) >= 2:
                        if argv[1] == 'add':
                                # groupname
                                if len(argv) == 4:
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames

                                # from-category, to-category
                                if len(argv) == 5 or len(argv) == 6:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                        elif argv[1] == 'edit':
                                # name
                                if len(argv) == 3:
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                                 # groupname
                                if len(argv) == 4:
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames

                                # from-category, to-category
                                if len(argv) == 5 or len(argv) == 6:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                        elif argv[1] == 'delete':
                                # name
                                if len(argv) == 3:
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                        elif argv[1] == 'rename':
                                # name
                                if len(argv) == 3:
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                        elif argv[1] == 'move':
                                # name
                                if len(argv) == 3:
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                                # groupname
                                if len(argv) == 4:
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                        elif argv[1] == 'execute':
                                # name
                                if len(argv) == 3:
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                        elif argv[1] == 'list':
                                parameters = ['category', 'fromcategory', 'tocategory', 'group']

                                if argv[-2] in ['--category', '--fromcategory', '--tocategory']:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                                elif argv[-2] == '--group':
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                                else:
                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        elif argv[-1].startswith('-'):
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '-'+v, parameters))))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        elif argv[1] == 'listnames':
                                parameters = ['group']

                                if argv[-2] == '--group':
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                                else:
                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        elif argv[-1].startswith('-'):
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '-'+v, parameters))))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        elif len(argv) == 2:
                                return list(filter(lambda v: v.startswith(argv[-1]), ['add', 'edit', 'rename', 'move', 'execute', 'delete', 'list', 'listnames', 'listgroupnames']))

        def complete_summary(self, text, line, begidx, endidx):
                if endidx < len(line):
                        return

                argv = shlex.split(line)

                if len(argv) == 1 or line.endswith(' '):
                        argv.append('')

                if len(argv) >= 2:
                        if argv[1] == 'paymentplansprediction':
                                parameters = ['category', 'cashflowcategory', 'factor', 'divisor', 'group', 'showempty', 'maxlevel']

                                if argv[-2] in ['--category', '--cashflowcategory']:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                                elif argv[-2] == '--group':
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                                elif len(argv) >= 3:
                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        if argv[1] == 'categories':
                                parameters = ['after', 'after-or-from', 'before', 'before-or-from', 'from', 'category', 'cashflowcategory', 'nopaymentplans', 'paymentplansonly', 'paymentplan', 'paymentplangroup', 'showempty',  'maxlevel']

                                if argv[-2] in ['--category', '--cashflowcategory']:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                                elif argv[-2] == '--paymentplan':
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                                elif argv[-2] == '--paymentplangroup':
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                                elif len(argv) >= 3:
                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        elif argv[1] == 'monthly' or argv[1] == 'yearly':
                                parameters = ['after', 'after-or-from', 'before', 'before-or-from', 'from', 'balance', 'nopaymentplans', 'paymentplansonly', 'paymentplan', 'paymentplangroup']

                                if len(argv) == 3:
                                        categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                        categorynames = map(lambda c: c.get_unique_name(), categories)
                                        categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                        return list(categorynames)
                                elif argv[-2] == '--paymentplan':
                                        names = self.pyMoney.get_moneydata().get_paymentplannames()
                                        names = list(filter(lambda v: v.startswith(argv[-1]), names))

                                        return names
                                elif argv[-2] == '--paymentplangroup':
                                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()
                                        groupnames = list(filter(lambda v: v.startswith(argv[-1]), groupnames))

                                        return groupnames
                                elif len(argv) >= 4:

                                        if argv[-1].startswith('--'):
                                                return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                        elif argv[-1].startswith('-'):
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '-'+v, parameters))))
                                        else:
                                                return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))
                        elif len(argv) == 2:
                                return list(filter(lambda v: v.startswith(argv[-1]), ['categories', 'paymentplansprediction', 'monthly', 'yearly']))

        def complete_export(self, text, line, begidx, endidx):
                if endidx < len(line):
                        return

                argv = shlex.split(line)

                if len(argv) == 1 or line.endswith(' '):
                        argv.append('')

                if len(argv) >= 2:
                        parameters = ['after', 'after-or-from', 'before', 'before-or-from', 'from', 'category', 'fromcategory', 'tocategory']

                        if argv[-2] in ['--category', '--fromcategory', '--tocategory']:
                                categories = self.pyMoney.get_moneydata().get_categories_iterator()
                                categorynames = map(lambda c: c.get_unique_name(), categories)
                                categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

                                return list(categorynames)
                        elif len(argv) >= 3:
                                if argv[-1].startswith('--'):
                                        return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
                                elif argv[-1].startswith('-'):
                                        return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '-'+v, parameters))))
                                else:
                                        return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: '--'+v, parameters))))


class PyMoneyConsole(cmd.Cmd):
        def __init__(self, argv):
                cmd.Cmd.__init__(self)

                self.is_interactive = True
                self.prompt = '(pyMoney) '

                parser = self.get_argument_parser()
                self.arguments = parser.parse_args(argv)

                self.pyMoney = lib.app.PyMoney(self.arguments.__dict__['fileprefix'])
                self.pyMoney.read()

                self.completion = PyMoneyCompletion(self.pyMoney)

                self.writeOnQuit = False

                self.stdout = sys.stdout
                self.stderr = sys.stderr

        def set_print_streams(self, stdout, stderr):
                self.stdout = stdout
                self.stderr = stderr

        def print(self, line):
                print(line, file=self.stdout)

        def print_stderr(self, line):
                print(line, file=self.stderr)

        def print_error(self, error):
                value = None

                if isinstance(error, lib.data.moneydata.NoSuchCategoryException):
                        value = 'category not found: ' + error.name
                elif isinstance(error, lib.data.moneydata.DuplicateCategoryException):
                        value = 'category already exists: ' + error.category.get_unique_name()
                elif isinstance(error, lib.data.moneydata.CategoryIsTopCategoryException):
                        value = 'top category may not be deleted: ' + error.category.get_unique_name()
                elif isinstance(error, lib.data.moneydata.AmbiguousCategoryNameException):
                        value = 'category name ' + error.name + ' is ambiguous: ' + str(list(map(lambda c: c.get_unique_name(), error.matching_categories)))
                elif isinstance(error, lib.data.tree.TargetNodeIsPartOfSourceNodeSubTreeException):
                        value = 'cannot move source node into its own subtree: ' + str(error.sourcenode.get_unique_name())
                elif isinstance(error, lib.data.moneydata.NoSuchPaymentPlanException):
                        value = 'payment plan not found: ' + error.name
                elif isinstance(error, lib.data.moneydata.DuplicatePaymentPlanException):
                        value = 'payment plan already exists: ' + error.paymentplan.name + ' (group: ' + error.paymentplan.groupname + ')'
                elif isinstance(error, ValueError):
                        value = str(error)
                else:
                        value = 'unhandled exception: ' + error.__class__.__module__ + '.' + error.__class__.__name__ + ': ' + str(error)

                if not value is None:
                        self.print_stderr(value)

        ### Cmd completion
        def complete_export(self, text, line, beginidx, endidx):
                return self.completion.complete_export(text, line, beginidx, endidx)

        def complete_transaction(self, text, line, beginidx, endidx):
                return self.completion.complete_transaction(text, line, beginidx, endidx)

        def complete_category(self, text, line, beginidx, endidx):
                return self.completion.complete_category(text, line, beginidx, endidx)

        def complete_paymentplan(self, text, line, beginidx, endidx):
                return self.completion.complete_paymentplan(text, line, beginidx, endidx)

        def complete_summary(self, text, line, beginidx, endidx):
                return self.completion.complete_summary(text, line, beginidx, endidx)

        ### Cmd commands
        def parse_daterange(self, str_operator, str_daterange, ignore_day=False):
                # parse string of form [OP]YYYY[-MM[-DD]], i.e. >=2019 or 2019-01-01
                operator = "="
                str_year = None
                str_month = None
                str_day = None

                if not str_operator is None and len(str(str_operator)):
                        if str_operator  == "<=":
                                operator = "<="
                        elif str_operator  == ">=":
                                operator = ">="
                        elif str_operator  == "<":
                                operator = "<"
                        elif str_operator  == ">":
                                operator = ">"

                if not str_daterange is None and len(str(str_daterange)):
                        pos_minus = str_daterange.find("-")
                        if pos_minus < 0:
                                str_year = str_daterange
                                str_daterange = ''
                        else:
                                str_year = str_daterange[:pos_minus]
                                str_daterange = str_daterange[pos_minus+1:]
        
                        pos_minus = str_daterange.find("-")
                        if pos_minus < 0:
                                str_month = str_daterange
                                str_daterange = ''
                        else:
                                str_month = str_daterange[:pos_minus]
                                str_daterange = str_daterange[pos_minus+1:]
        
                        if len(str_daterange):
                                str_day = str_daterange
                                str_daterange = ''

                year = None
                month = None
                day = None
                if not str_year is None and len(str_year):
                        year = int(str_year)
                if not str_month is None and len(str_month):
                        month = int(str_month)
                if not ignore_day:
                        if not str_day is None and len(str_day):
                                day = int(str_day)

                daterange = None
                if not str_year is None and len(str_year):
                        daterange = lib.data.daterange.DateRange(year, month, day, operator=operator)

                return daterange

        def do_transaction(self, args):
                'Adds, edits, deletes or lists transaction(s). Use transaction -h for more details.'
                def cmd_add(arguments):
                        try:
                                if self.is_interactive:
                                        similar_paymentplans = self.pyMoney.get_moneydata().find_similar_paymentplans(arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'], arguments.__dict__['amount'])
                                        if len(similar_paymentplans):
                                                paymentplans = None
                                                for paymentplan in similar_paymentplans:
                                                        if paymentplans is None:
                                                                paymentplans = paymentplan.name
                                                        else:
                                                                paymentplans += ', ' + paymentplan.name

                                                self.print('similar payment plan(s) found: ' + paymentplans)

                                transaction = self.pyMoney.get_moneydata().add_transaction(arguments.__dict__['date'], arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'], arguments.__dict__['amount'],
                                                                arguments.__dict__['comment'], arguments.__dict__['force'])

                                if self.is_interactive:
                                        self.print('added transaction ' + str(transaction.index) + ': transferred amount ' + str(transaction.amount) + ' from ' + transaction.fromcategory.get_unique_name() + ' to ' + transaction.tocategory.get_unique_name())

                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_edit(arguments):
                        try:
                                self.pyMoney.get_moneydata().edit_transaction(arguments.__dict__['index'], arguments.__dict__['date'], arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'],
                                                                arguments.__dict__['amount'], arguments.__dict__['comment'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_list(arguments):
                        after_daterange = self.parse_daterange(">", arguments.__dict__['after'])
                        after_or_from_daterange = self.parse_daterange(">=", arguments.__dict__['after_or_from'])
                        before_daterange = self.parse_daterange("<", arguments.__dict__['before'])
                        before_or_from_daterange = self.parse_daterange("<=", arguments.__dict__['before_or_from'])
                        from_daterange = self.parse_daterange("=", arguments.__dict__['from'])
                        transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(from_daterange, before_daterange, before_or_from_daterange, after_daterange, after_or_from_daterange)

                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)

                        if arguments.__dict__['paymentplansonly'] or arguments.__dict__['paymentplan'] or arguments.__dict__['paymentplangroup']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: not pp is None)
                                )

                        if arguments.__dict__['nopaymentplans']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: pp is None)
                                )

                        if arguments.__dict__['paymentplan']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.name == arguments.__dict__['paymentplan'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        if arguments.__dict__['paymentplangroup']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['paymentplangroup'])
                                        )
                                except Exception as e:
                                        self.print_error(e)


                        summarycategory = None

                        if arguments.__dict__['category']:
                                try:
                                        transactionfilter = transactionfilter.and_concat(
                                                self.pyMoney.filterFactory.create_or_category_transactionfilter(arguments.__dict__['category'], arguments.__dict__['category'])
                                        )
                                        summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__['category'])
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        if arguments.__dict__['fromcategory'] or arguments.__dict__['tocategory']:
                                try:
                                        transactionfilter = transactionfilter.and_concat(
                                                self.pyMoney.filterFactory.create_and_category_transactionfilter(arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'])
                                        )

                                        if arguments.__dict__['fromcategory']:
                                                summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__['fromcategory'])
                                        if arguments.__dict__['tocategory']:
                                                summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__['tocategory'])
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        # also apply paymentplan filter to transactions
                        transactionfilter = transactionfilter.and_concat(
                                lib.data.filterchain.Filter(lambda t: paymentplanfilter(t.paymentplan))
                        )

                        headerdata = ['Index', 'Date', 'FromCategory', 'ToCategory', 'Amount', 'Comment']
                        tabledata = []

                        fromcategory_name_formatter = lib.formatter.CategoryNameFormatter()
                        tocategory_name_formatter = lib.formatter.CategoryNameFormatter()
                        if arguments.__dict__['fullnamecategories']:
                                fromcategory_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
                                tocategory_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)

                        iterator = self.pyMoney.get_moneydata().filter_transactions(transactionfilter)
                        for d in iterator:
                                assert isinstance(d.fromcategory, lib.data.moneydata.CategoryTreeNode)
                                assert isinstance(d.tocategory, lib.data.moneydata.CategoryTreeNode)

                                _index = d.index
                                _date = str(d.date)

                                _fromcategory = fromcategory_name_formatter.format(d.fromcategory)
                                _tocategory = tocategory_name_formatter.format(d.tocategory)

                                _amount = d.amount

                                if not d.paymentplan is None:
                                    _comment = 'Execution of payment plan ' + d.paymentplan.name
                                    if len(d.comment) > 0:
                                        _comment = _comment + ': ' + d.comment
                                else:
                                        _comment = d.comment

                                tabledata.append([_index, _date, _fromcategory, _tocategory, _amount, _comment])

                        d_summary = self.pyMoney.get_moneydata().create_summary(transactionfilter, paymentplanfilter)

                        if summarycategory:
                                _summarycategory = tocategory_name_formatter.format(summarycategory)
                                key = summarycategory.get_unique_name()

                                tabledata.append(['', '', '', '', None, ''])
                                tabledata.append(['', '', '', '+ ' + _summarycategory, d_summary[key].sumin, ''])
                                tabledata.append(['', '', '', '- ' + _summarycategory, d_summary[key].sumout, ''])
                                tabledata.append(['', '', '', 'sum ' + _summarycategory, d_summary[key].sum, ''])

                        tableformatter = lib.formatter.TableFormatter()
                        column = tableformatter.add_column(0)
                        column.set_alignment('>')
                        column = tableformatter.add_column(1)
                        column.set_alignment('>')
                        tableformatter.add_column(2)
                        tableformatter.add_column(3)
                        column = tableformatter.add_column(4)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        tableformatter.add_column(5)

                        lines = tableformatter.get_formatted_lines(headerdata, tabledata)

                        is_first_line = True
                        for line in lines:
                                self.print(line)
                                if is_first_line:
                                        self.print('')

                                is_first_line = False

                def cmd_delete(arguments):
                        self.pyMoney.get_moneydata().delete_transaction(arguments.__dict__['index'])
                        self.writeOnQuit = True

                parser = lib.argparse.ArgumentParser()
                parser.add_argument('--fullnamecategories', action='store_true')
                sp_transaction = parser.add_subparsers(title='command')

                p_transaction_add = sp_transaction.add_parser('add')
                p_transaction_add.set_defaults(command='add')
                p_transaction_add.set_defaults(parser=p_transaction_add)
                p_transaction_add.add_argument('date')
                p_transaction_add.add_argument('fromcategory')
                p_transaction_add.add_argument('tocategory')
                p_transaction_add.add_argument('amount', type=float)
                p_transaction_add.add_argument('comment', default='', nargs='?')
                p_transaction_add.add_argument('--force', action='store_true')

                p_transaction_edit = sp_transaction.add_parser('edit')
                p_transaction_edit.set_defaults(command='edit')
                p_transaction_edit.set_defaults(parser=p_transaction_edit)
                p_transaction_edit.add_argument('index', type=int)
                p_transaction_edit.add_argument('date')
                p_transaction_edit.add_argument('fromcategory')
                p_transaction_edit.add_argument('tocategory')
                p_transaction_edit.add_argument('amount', type=float)
                p_transaction_edit.add_argument('comment', default='', nargs='?')

                p_transaction_delete = sp_transaction.add_parser('delete')
                p_transaction_delete.set_defaults(command='delete')
                p_transaction_delete.set_defaults(parser=p_transaction_delete)
                p_transaction_delete.add_argument('index', type=int)

                p_transaction_list = sp_transaction.add_parser('list')
                p_transaction_list.set_defaults(command='list')
                p_transaction_list.set_defaults(parser=p_transaction_list)

                p_transaction_list.add_argument('--after', metavar='AFTER-DATERANGE')
                p_transaction_list.add_argument('--after-or-from', metavar='AFTER-OR-FROM-DATERANGE')
                p_transaction_list.add_argument('--before', metavar='BEFROE-DATERANGE')
                p_transaction_list.add_argument('--before-or-from', metavar='BEFORE-FROM-DATERANGE')
                p_transaction_list.add_argument('--from', metavar='FROM-DATERANGE', help='i.e. 2000 or 2000-01 or 2000-01-15')

                p_transaction_list.add_argument('--category')
                p_transaction_list.add_argument('--fromcategory')
                p_transaction_list.add_argument('--tocategory')
                p_transaction_list.add_argument('--nopaymentplans', action='store_true')
                p_transaction_list.add_argument('--paymentplansonly', action='store_true')
                p_transaction_list.add_argument('--paymentplan')
                p_transaction_list.add_argument('--paymentplangroup')

                try:
                        arguments = parser.parse_args(shlex.split(args))
                except Exception as e:
                        # parse errors already handled by parser (printed to user)
                        # no further handling
                        return

                d_commands = {
                        'add': cmd_add,
                        'delete': cmd_delete,
                        'edit': cmd_edit,
                        'list': cmd_list
                }

                if not 'command' in arguments.__dict__:
                        parser.print_help()
                else:
                        try:
                                d_commands[arguments.__dict__['command']](arguments)
                        except Exception as e:
                                self.print_error(e)
                                arguments.__dict__['parser'].print_help()
                                return

        def do_category(self, args):
                'Adds, deletes, merges, moves or lists categories. Use category -h for more details.'
                def cmd_tree(arguments):
                        category_name_formatter = lib.formatter.CategoryNameFormatter()
                        category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
                        category_name_formatter.set_indent_with_tree_level(True)

                        if arguments.__dict__['fullnamecategories']:
                                category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
                                category_name_formatter.set_indent_with_tree_level(False)

                        for c in self.pyMoney.get_moneydata().get_categories_iterator():
                                self.print(category_name_formatter.format(c))

                def cmd_list(arguments):
                        category_name_formatter = lib.formatter.CategoryNameFormatter()
                        if arguments.__dict__['fullnamecategories']:
                                category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)

                        for category in self.pyMoney.get_moneydata().get_categories_iterator():
                                _category = category_name_formatter.format(category)
                                self.print(_category)
                        self.print('')

                def cmd_add(arguments):
                        try:
                                self.pyMoney.get_moneydata().add_category(arguments.__dict__['parentname'], arguments.__dict__['name'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_delete(arguments):
                        try:
                                self.pyMoney.get_moneydata().delete_category(arguments.__dict__['name'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_move(arguments):
                        try:
                                self.pyMoney.get_moneydata().move_category(arguments.__dict__['name'], arguments.__dict__['newparentname'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_rename(arguments):
                        try:
                                self.pyMoney.get_moneydata().rename_category(arguments.__dict__['name'], arguments.__dict__['newname'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_merge(arguments):
                        try:
                                self.pyMoney.get_moneydata().merge_to_category(arguments.__dict__['name'], arguments.__dict__['targetname'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                parser = lib.argparse.ArgumentParser()
                sp_category = parser.add_subparsers(title='command')

                p_category_add = sp_category.add_parser('add')
                p_category_add.set_defaults(command='add')
                p_category_add.set_defaults(parser=p_category_add)
                p_category_add.add_argument('parentname')
                p_category_add.add_argument('name')

                p_category_delete = sp_category.add_parser('delete')
                p_category_delete.set_defaults(command='delete')
                p_category_delete.set_defaults(parser=p_category_delete)
                p_category_delete.add_argument('name')

                p_category_merge = sp_category.add_parser('merge')
                p_category_merge.set_defaults(command='merge')
                p_category_merge.set_defaults(parser=p_category_merge)
                p_category_merge.add_argument('name')
                p_category_merge.add_argument('targetname')

                p_category_move = sp_category.add_parser('move')
                p_category_move.set_defaults(command='move')
                p_category_move.set_defaults(parser=p_category_move)
                p_category_move.add_argument('name')
                p_category_move.add_argument('newparentname')

                p_category_rename = sp_category.add_parser('rename')
                p_category_rename.set_defaults(command='rename')
                p_category_rename.set_defaults(parser=p_category_rename)
                p_category_rename.add_argument('name')
                p_category_rename.add_argument('newname')

                p_category_tree = sp_category.add_parser('tree')
                p_category_tree.set_defaults(command='tree')
                p_category_tree.set_defaults(parser=p_category_tree)
                p_category_tree.add_argument('--fullnamecategories', action='store_true')

                p_category_list = sp_category.add_parser('list')
                p_category_list.set_defaults(command='list')
                p_category_list.set_defaults(parser=p_category_list)
                p_category_list.add_argument('--fullnamecategories', action='store_true')

                try:
                        arguments = parser.parse_args(shlex.split(args))
                except Exception as e:
                        # parse errors already handled by parser (printed to user)
                        # no further handling
                        return

                d_commands = {
                        'add': cmd_add,
                        'delete': cmd_delete,
                        'move': cmd_move,
                        'rename': cmd_rename,
                        'merge': cmd_merge,
                        'list': cmd_list,
                        'tree': cmd_tree
                }

                if not 'command' in arguments.__dict__:
                        parser.print_help()
                else:
                        try:
                                d_commands[arguments.__dict__['command']](arguments)
                        except Exception as e:
                                self.print_error(e)
                                arguments.__dict__['parser'].print_help()
                                return

        def do_paymentplan(self, args):
                'Adds, deletes, edits or executes payment plans'
                def cmd_add(arguments):
                        try:
                                self.pyMoney.get_moneydata().add_paymentplan(arguments.__dict__['name'], arguments.__dict__['groupname'], arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'], arguments.__dict__['amount'], arguments.__dict__['comment'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_edit(arguments):
                        try:
                                self.pyMoney.get_moneydata().edit_paymentplan(arguments.__dict__['name'], arguments.__dict__['groupname'], arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'], arguments.__dict__['amount'], arguments.__dict__['comment'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_delete(arguments):
                        try:
                                self.pyMoney.get_moneydata().delete_paymentplan(arguments.__dict__['name'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_rename(arguments):
                        try:
                                self.pyMoney.get_moneydata().rename_paymentplan(arguments.__dict__['name'], arguments.__dict__['newname'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_move(arguments):
                        try:
                                self.pyMoney.get_moneydata().move_paymentplan(arguments.__dict__['name'], arguments.__dict__['newgroupname'])
                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)

                def cmd_list(arguments):
                        headerdata = ['Group', 'PaymentPlan', 'FromCategory', 'ToCategory', 'Amount', 'Comment']
                        tabledata = []

                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)

                        if arguments.__dict__['group']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['group'])
                                )

                        summarycategory = None

                        if arguments.__dict__['category']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                self.pyMoney.filterFactory.create_or_category_paymentplanfilter(arguments.__dict__['category'], arguments.__dict__['category'])
                                        )
                                        summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__['category'])
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        if arguments.__dict__['fromcategory'] or arguments.__dict__['tocategory']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                self.pyMoney.filterFactory.create_and_category_paymentplanfilter(arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'])
                                        )

                                        if arguments.__dict__['fromcategory']:
                                                summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__['fromcategory'])
                                        if arguments.__dict__['tocategory']:
                                                summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__['tocategory'])
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        for paymentplan in self.pyMoney.get_moneydata().get_paymentplans_iterator():
                                if not paymentplanfilter(paymentplan):
                                        continue

                                row = []

                                row.append(paymentplan.groupname)
                                row.append(paymentplan.name)
                                row.append(paymentplan.fromcategory.get_unique_name())
                                row.append(paymentplan.tocategory.get_unique_name())
                                row.append(paymentplan.amount)
                                row.append(paymentplan.comment)

                                tabledata.append(row)

                        d_summary = self.pyMoney.get_moneydata().create_paymentplan_summary(paymentplanfilter, 1)

                        if summarycategory:
                                _summarycategory = summarycategory.get_unique_name()
                                key = summarycategory.get_unique_name()

                                tabledata.append(['', '', '', '', None, ''])
                                tabledata.append(['', '', '', '+ ' + _summarycategory, d_summary[key].sumin, ''])
                                tabledata.append(['', '', '', '- ' + _summarycategory, d_summary[key].sumout, ''])
                                tabledata.append(['', '', '', 'sum ' + _summarycategory, d_summary[key].sum, ''])

                        tableformatter = lib.formatter.TableFormatter()
                        tableformatter.add_column(0)
                        tableformatter.add_column(1)
                        tableformatter.add_column(2)
                        tableformatter.add_column(3)
                        column = tableformatter.add_column(4)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        tableformatter.add_column(5)

                        lines = tableformatter.get_formatted_lines(headerdata, tabledata)

                        is_first_line = True
                        for line in lines:
                                self.print(line)
                                if is_first_line:
                                        self.print('')

                                is_first_line = False

                def cmd_listnames(arguments):
                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)

                        if arguments.__dict__['group']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['group'])
                                )

                        for paymentplan in self.pyMoney.get_moneydata().get_paymentplans_iterator():
                                if not paymentplanfilter(paymentplan):
                                        continue

                                self.print(paymentplan.name)

                def cmd_listgroupnames(arguments):
                        groupnames = self.pyMoney.get_moneydata().get_paymentplangroupnames()

                        for groupname in groupnames:
                                self.print(groupname)

                def cmd_execute(arguments):
                        try:
                                transaction = self.pyMoney.get_moneydata().execute_paymentplan(arguments.__dict__['name'], arguments.__dict__['date'], arguments.__dict__['amount'], arguments.__dict__['comment'])

                                if self.is_interactive:
                                        self.print('added transaction ' + str(transaction.index) + ': transferred amount ' + str(transaction.amount) + ' from ' + transaction.fromcategory.get_unique_name() + ' to ' + transaction.tocategory.get_unique_name())

                                self.writeOnQuit = True
                        except Exception as e:
                                self.print_error(e)


                parser = lib.argparse.ArgumentParser()
                sp_paymentplan = parser.add_subparsers(title='command')

                p_paymentplan_add = sp_paymentplan.add_parser('add')
                p_paymentplan_add.set_defaults(command='add')
                p_paymentplan_add.set_defaults(parser=p_paymentplan_add)
                p_paymentplan_add.add_argument('name')
                p_paymentplan_add.add_argument('groupname')
                p_paymentplan_add.add_argument('fromcategory')
                p_paymentplan_add.add_argument('tocategory')
                p_paymentplan_add.add_argument('amount', type=float)
                p_paymentplan_add.add_argument('comment', default='', nargs='?')

                p_paymentplan_delete = sp_paymentplan.add_parser('delete')
                p_paymentplan_delete.set_defaults(command='delete')
                p_paymentplan_delete.set_defaults(parser=p_paymentplan_delete)
                p_paymentplan_delete.add_argument('name')

                p_paymentplan_edit = sp_paymentplan.add_parser('edit')
                p_paymentplan_edit.set_defaults(command='edit')
                p_paymentplan_edit.set_defaults(parser=p_paymentplan_edit)
                p_paymentplan_edit.add_argument('name')
                p_paymentplan_edit.add_argument('groupname')
                p_paymentplan_edit.add_argument('fromcategory')
                p_paymentplan_edit.add_argument('tocategory')
                p_paymentplan_edit.add_argument('amount', type=float)
                p_paymentplan_edit.add_argument('comment', default='', nargs='?')

                p_paymentplan_rename = sp_paymentplan.add_parser('rename')
                p_paymentplan_rename.set_defaults(command='rename')
                p_paymentplan_rename.set_defaults(parser=p_paymentplan_rename)
                p_paymentplan_rename.add_argument('name')
                p_paymentplan_rename.add_argument('newname')

                p_paymentplan_move = sp_paymentplan.add_parser('move')
                p_paymentplan_move.set_defaults(command='move')
                p_paymentplan_move.set_defaults(parser=p_paymentplan_move)
                p_paymentplan_move.add_argument('name')
                p_paymentplan_move.add_argument('newgroupname')

                p_paymentplan_list = sp_paymentplan.add_parser('list')
                p_paymentplan_list.set_defaults(command='list')
                p_paymentplan_list.set_defaults(parser=p_paymentplan_list)
                p_paymentplan_list.add_argument('--category')
                p_paymentplan_list.add_argument('--fromcategory')
                p_paymentplan_list.add_argument('--tocategory')
                p_paymentplan_list.add_argument('--group')

                p_paymentplan_listnames = sp_paymentplan.add_parser('listnames')
                p_paymentplan_listnames.set_defaults(command='listnames')
                p_paymentplan_listnames.set_defaults(parser=p_paymentplan_listnames)
                p_paymentplan_listnames.add_argument('--group')

                p_paymentplan_listgroupnames = sp_paymentplan.add_parser('listgroupnames')
                p_paymentplan_listgroupnames.set_defaults(command='listgroupnames')
                p_paymentplan_listgroupnames.set_defaults(parser=p_paymentplan_listgroupnames)

                p_paymentplan_execute = sp_paymentplan.add_parser('execute')
                p_paymentplan_execute.set_defaults(command='execute')
                p_paymentplan_execute.set_defaults(parser=p_paymentplan_execute)
                p_paymentplan_execute.add_argument('name')
                p_paymentplan_execute.add_argument('date')
                p_paymentplan_execute.add_argument('amount', default=None, type=float, nargs='?')
                p_paymentplan_execute.add_argument('comment', default='', nargs='?')

                try:
                        arguments = parser.parse_args(shlex.split(args))
                except Exception as e:
                        # parse errors already handled by parser (printed to user)
                        # no further handling
                        return

                d_commands = {
                        'add': cmd_add,
                        'delete': cmd_delete,
                        'edit': cmd_edit,
                        'rename': cmd_rename,
                        'move': cmd_move,
                        'list': cmd_list,
                        'listnames': cmd_listnames,
                        'listgroupnames': cmd_listgroupnames,
                        'execute': cmd_execute
                }

                if not 'command' in arguments.__dict__:
                        parser.print_help()
                else:
                        try:
                                d_commands[arguments.__dict__['command']](arguments)
                        except Exception as e:
                                self.print_error(e)
                                arguments.__dict__['parser'].print_help()
                                return

        def do_summary(self, args):
                'Prints a summarized report across categories / date intervals. Use summary -h for more details.'
                def cmd_categories(arguments):
                        after_daterange = self.parse_daterange(">", arguments.__dict__['after'])
                        after_or_from_daterange = self.parse_daterange(">=", arguments.__dict__['after_or_from'])
                        before_daterange = self.parse_daterange("<", arguments.__dict__['before'])
                        before_or_from_daterange = self.parse_daterange("<=", arguments.__dict__['before_or_from'])
                        from_daterange = self.parse_daterange("=", arguments.__dict__['from'])
                        transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(from_daterange, before_daterange, before_or_from_daterange, after_daterange, after_or_from_daterange)

                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)
                        is_paymentplanfilter_active = False

                        if arguments.__dict__['paymentplansonly'] or arguments.__dict__['paymentplan'] or arguments.__dict__['paymentplangroup']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: not pp is None)
                                )
                                is_paymentplanfilter_active = True

                        if arguments.__dict__['nopaymentplans']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: pp is None)
                                )

                        if arguments.__dict__['paymentplan']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.name == arguments.__dict__['paymentplan'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        if arguments.__dict__['paymentplangroup']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['paymentplangroup'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        if arguments.__dict__['cashflowcategory']:
                                try:
                                        transactionfilter = transactionfilter.and_concat(
                                                self.pyMoney.filterFactory.create_xor_category_transactionfilter(arguments.__dict__['cashflowcategory'], arguments.__dict__['cashflowcategory'])
                                        )
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        categoryfilter = lib.data.filterchain.Filter(lambda c: True)
                        if arguments.__dict__['maxlevel']:
                                categoryfilter = categoryfilter.and_concat(self.pyMoney.filterFactory.create_maxlevel_categoryfilter(arguments.__dict__['maxlevel']))

                        if arguments.__dict__['category']:
                                categoryfilter = categoryfilter.and_concat(self.pyMoney.filterFactory.create_subtree_categoryfilter(arguments.__dict__['category']))

                        # also apply paymentplan filter to transactions
                        transactionfilter = transactionfilter.and_concat(
                                lib.data.filterchain.Filter(lambda t: paymentplanfilter(t.paymentplan))
                        )

                        d_summary = self.pyMoney.get_moneydata().create_summary(transactionfilter, paymentplanfilter)
                        category_name_formatter = lib.formatter.CategoryNameFormatter()
                        category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
                        category_name_formatter.set_indent_with_tree_level(True)

                        headerdata = ['node', 'amount', 'sum +', 'sum -', 'sum']
                        tabledata = []

                        for category in filter(categoryfilter, self.pyMoney.get_moneydata().get_categories_iterator()):
                                key = category.get_unique_name()
                                name = category_name_formatter.format(category)

                                if is_paymentplanfilter_active and d_summary[key].paymentplancount == 0:
                                        continue

                                if not arguments.__dict__['showempty'] and d_summary[key].sumcount == 0:
                                        continue

                                tabledata.append([name, d_summary[key].amount, d_summary[key].sumin, d_summary[key].sumout, d_summary[key].sum])

                        tableformatter = lib.formatter.TableFormatter()
                        tableformatter.add_column(0)
                        column = tableformatter.add_column(1)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(2)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(3)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(4)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')

                        lines = tableformatter.get_formatted_lines(headerdata, tabledata)

                        is_first_line = True
                        for line in lines:
                                self.print(line)
                                if is_first_line:
                                        self.print('')

                                is_first_line = False

                'Prints a summarized report of predicted payments across categories based on the paymentplans. Use summary -h for more details.'
                def cmd_paymentplansprediction(arguments):
                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)
                        factor = 1

                        if not arguments.__dict__['factor'] is None:
                                factor = arguments.__dict__['factor']

                        if not arguments.__dict__['divisor'] is None:
                                factor = 1 / arguments.__dict__['divisor']

                        if arguments.__dict__['group']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: not pp is None)
                                )

                        if arguments.__dict__['group']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['group'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        if arguments.__dict__['cashflowcategory']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                self.pyMoney.filterFactory.create_or_category_paymentplanfilter(arguments.__dict__['cashflowcategory'], arguments.__dict__['cashflowcategory'])
                                        )
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        categoryfilter = lib.data.filterchain.Filter(lambda c: True)
                        if arguments.__dict__['maxlevel']:
                                categoryfilter = categoryfilter.and_concat(self.pyMoney.filterFactory.create_maxlevel_categoryfilter(arguments.__dict__['maxlevel']))

                        if arguments.__dict__['category']:
                                categoryfilter = categoryfilter.and_concat(self.pyMoney.filterFactory.create_subtree_categoryfilter(arguments.__dict__['category']))

                        d_summary = self.pyMoney.get_moneydata().create_paymentplan_summary(paymentplanfilter, factor)
                        category_name_formatter = lib.formatter.CategoryNameFormatter()
                        category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
                        category_name_formatter.set_indent_with_tree_level(True)

                        headerdata = ['node', 'amount', 'sum +', 'sum -', 'sum']
                        tabledata = []

                        for category in filter(categoryfilter, self.pyMoney.get_moneydata().get_categories_iterator()):
                                key = category.get_unique_name()
                                name = category_name_formatter.format(category)

                                if not arguments.__dict__['showempty'] and d_summary[key].sumcount == 0:
                                        continue

                                tabledata.append([name, d_summary[key].amount, d_summary[key].sumin, d_summary[key].sumout, d_summary[key].sum])

                        tableformatter = lib.formatter.TableFormatter()
                        tableformatter.add_column(0)
                        column = tableformatter.add_column(1)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(2)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(3)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(4)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')

                        lines = tableformatter.get_formatted_lines(headerdata, tabledata)

                        is_first_line = True
                        for line in lines:
                                self.print(line)
                                if is_first_line:
                                        self.print('')

                                is_first_line = False

                def sub_time_interval_summary(category, paymentplanfilter, datefilter, start_year, start_month, diff_months, maxdate, calculate_balance):
                        assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

                        category_name_formatter = lib.formatter.CategoryNameFormatter()

                        year = start_year
                        month = start_month

                        headerdata = ['date', 'node', 'amount', 'sum +', 'sum -', 'sum']
                        tabledata = []

                        key = category.get_unique_name()
                        name = category_name_formatter.format(category)
                        d_summary = None
                        while datetime.date(year, month, 1) <= maxdate:
                                if diff_months == 1:
                                        timestep_transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(lib.data.daterange.DateRange(year, month), None, None, None, None)
                                elif diff_months == 12:
                                        timestep_transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(lib.data.daterange.DateRange(year), None, None, None, None)
                                else:
                                        raise Exception('diff_months value not supported: ' + str(diff_months))

                                # also apply paymentplan filter to transactions
                                timestep_transactionfilter = timestep_transactionfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda t: paymentplanfilter(t.paymentplan))
                                )

                                if calculate_balance:
                                        d_summary = self.pyMoney.get_moneydata().create_summary(timestep_transactionfilter, paymentplanfilter, d_summary)
                                else:
                                        d_summary = self.pyMoney.get_moneydata().create_summary(timestep_transactionfilter, paymentplanfilter, None)

                                displayday = calendar.monthrange(year, month)[1]
                                if diff_months != 12:
                                        displaymonth = month
                                else:
                                        displaymonth = 12
                                
                                if datefilter is None or datefilter(datetime.date(year, month, 1)):
                                        tabledata.append([
                                                str(datetime.date(year, displaymonth, displayday)),
                                                name,
                                                d_summary[key].amount,
                                                d_summary[key].sumin,
                                                d_summary[key].sumout,
                                                d_summary[key].sum])

                                month += diff_months

                                if month > 12:
                                        year += int(month / 12)
                                        month %= 12

                        tableformatter = lib.formatter.TableFormatter()
                        tableformatter.add_column(0)
                        tableformatter.add_column(1)
                        column = tableformatter.add_column(2)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(3)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(4)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')
                        column = tableformatter.add_column(5)
                        column.set_alignment('>')
                        column.set_precision(2)
                        column.set_type('f')

                        lines = tableformatter.get_formatted_lines(headerdata, tabledata)

                        is_first_line = True
                        for line in lines:
                                self.print(line)
                                if is_first_line:
                                        self.print('')

                                is_first_line = False

                def cmd_monthly(arguments):
                        after_daterange = self.parse_daterange(">", arguments.__dict__['after'], ignore_day=True)
                        after_or_from_daterange = self.parse_daterange(">=", arguments.__dict__['after_or_from'], ignore_day=True)
                        before_daterange = self.parse_daterange("<", arguments.__dict__['before'], ignore_day=True)
                        before_or_from_daterange = self.parse_daterange("<=", arguments.__dict__['before_or_from'], ignore_day=True)
                        from_daterange = self.parse_daterange("=", arguments.__dict__['from'], ignore_day=True)
                        datefilter = self.pyMoney.filterFactory.create_and_datefilter(from_daterange, before_daterange, before_or_from_daterange, after_daterange, after_or_from_daterange)

                        mindate = None
                        maxdate = None
                        for transaction in self.pyMoney.get_moneydata().get_transactions_iterator():
                                if not datefilter is None:
                                        if not datefilter(transaction.date):
                                                # when not calculating balance skip transactions not applying to the date filter
                                                if not arguments.__dict__['balance']:
                                                        continue

                                if not mindate or transaction.date < mindate:
                                        mindate = transaction.date

                                if not maxdate or transaction.date > maxdate:
                                        maxdate = transaction.date

                        if mindate is None:
                            return

                        if maxdate is None:
                            return

                        try:
                                category = self.pyMoney.get_moneydata().get_category(arguments.__dict__['category'])
                        except Exception as e:
                                self.print_error(e)
                                return

                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)

                        if arguments.__dict__['paymentplansonly'] or arguments.__dict__['paymentplan'] or arguments.__dict__['paymentplangroup']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: not pp is None)
                                )

                        if arguments.__dict__['nopaymentplans']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: pp is None)
                                )

                        if arguments.__dict__['paymentplan']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.name == arguments.__dict__['paymentplan'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        if arguments.__dict__['paymentplangroup']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['paymentplangroup'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        sub_time_interval_summary(category, paymentplanfilter, datefilter, mindate.year, mindate.month, 1, maxdate, arguments.__dict__['balance'])

                def cmd_yearly(arguments):
                        after_daterange = self.parse_daterange(">", arguments.__dict__['after'], ignore_day=True)
                        after_or_from_daterange = self.parse_daterange(">=", arguments.__dict__['after_or_from'], ignore_day=True)
                        before_daterange = self.parse_daterange("<", arguments.__dict__['before'], ignore_day=True)
                        before_or_from_daterange = self.parse_daterange("<=", arguments.__dict__['before_or_from'], ignore_day=True)
                        from_daterange = self.parse_daterange("=", arguments.__dict__['from'], ignore_day=True)
                        datefilter = self.pyMoney.filterFactory.create_and_datefilter(from_daterange, before_daterange, before_or_from_daterange, after_daterange, after_or_from_daterange)

                        mindate = None
                        maxdate = None
                        for transaction in self.pyMoney.get_moneydata().get_transactions_iterator():
                                if not datefilter is None:
                                        if not datefilter(transaction.date):
                                                # when not calculating balance skip transactions not applying to the date filter
                                                if not arguments.__dict__['balance']:
                                                        continue

                                if not mindate or transaction.date < mindate:
                                        mindate = transaction.date

                                if not maxdate or transaction.date > maxdate:
                                        maxdate = transaction.date

                        if mindate is None:
                            return

                        if maxdate is None:
                            return

                        try:
                                category = self.pyMoney.get_moneydata().get_category(arguments.__dict__['category'])
                        except Exception as e:
                                self.print_error(e)
                                return

                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)

                        if arguments.__dict__['paymentplansonly'] or arguments.__dict__['paymentplan'] or arguments.__dict__['paymentplangroup']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: not pp is None)
                                )

                        if arguments.__dict__['nopaymentplans']:
                                paymentplanfilter = paymentplanfilter.and_concat(
                                        lib.data.filterchain.Filter(lambda pp: pp is None)
                                )

                        if arguments.__dict__['paymentplan']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.name == arguments.__dict__['paymentplan'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        if arguments.__dict__['paymentplangroup']:
                                try:
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.groupname == arguments.__dict__['paymentplangroup'])
                                        )
                                except Exception as e:
                                        self.print_error(e)

                        sub_time_interval_summary(category, paymentplanfilter, datefilter, mindate.year, 1, 12, maxdate, arguments.__dict__['balance'])

                parser = lib.argparse.ArgumentParser()
                sp_summary = parser.add_subparsers(title='command')

                p_summary_categories = sp_summary.add_parser('categories')
                p_summary_categories.set_defaults(command='categories')
                p_summary_categories.set_defaults(parser=p_summary_categories)
                p_summary_categories.add_argument('--maxlevel', type=int, nargs='?')
                p_summary_categories.add_argument('--showempty', action='store_true')
                p_summary_categories.add_argument('--cashflowcategory')
                p_summary_categories.add_argument('--category')
                p_summary_categories.add_argument('--nopaymentplans', action='store_true')
                p_summary_categories.add_argument('--paymentplansonly', action='store_true')
                p_summary_categories.add_argument('--paymentplan')
                p_summary_categories.add_argument('--paymentplangroup')
                p_summary_categories.add_argument('--after', metavar='AFTER-DATERANGE')
                p_summary_categories.add_argument('--after-or-from', metavar='AFTER-OR-FROM-DATERANGE')
                p_summary_categories.add_argument('--before', metavar='BEFROE-DATERANGE')
                p_summary_categories.add_argument('--before-or-from', metavar='BEFORE-FROM-DATERANGE')
                p_summary_categories.add_argument('--from', metavar='FROM-DATERANGE', help='i.e. 2000 or 2000-01 or 2000-01-15')

                p_summary_paymentplansprediction = sp_summary.add_parser('paymentplansprediction')
                p_summary_paymentplansprediction.set_defaults(command='paymentplansprediction')
                p_summary_paymentplansprediction.set_defaults(parser=p_summary_paymentplansprediction)
                p_summary_paymentplansprediction.add_argument('--maxlevel', type=int, nargs='?')
                p_summary_paymentplansprediction.add_argument('--showempty', action='store_true')
                p_summary_paymentplansprediction.add_argument('--cashflowcategory')
                p_summary_paymentplansprediction.add_argument('--category')
                p_summary_paymentplansprediction.add_argument('--factor', type=float)
                p_summary_paymentplansprediction.add_argument('--divisor', type=float)
                p_summary_paymentplansprediction.add_argument('--group')

                p_summary_monthly = sp_summary.add_parser('monthly')
                p_summary_monthly.set_defaults(command='monthly')
                p_summary_monthly.set_defaults(parser=p_summary_monthly)
                p_summary_monthly.add_argument('--balance', action='store_true')
                p_summary_monthly.add_argument('--nopaymentplans', action='store_true')
                p_summary_monthly.add_argument('--paymentplansonly', action='store_true')
                p_summary_monthly.add_argument('--paymentplan')
                p_summary_monthly.add_argument('--paymentplangroup')
                p_summary_monthly.add_argument('--after', metavar='AFTER-DATERANGE')
                p_summary_monthly.add_argument('--after-or-from', metavar='AFTER-OR-FROM-DATERANGE')
                p_summary_monthly.add_argument('--before', metavar='BEFROE-DATERANGE')
                p_summary_monthly.add_argument('--before-or-from', metavar='BEFORE-FROM-DATERANGE')
                p_summary_monthly.add_argument('--from', metavar='FROM-DATERANGE', help='i.e. 2000 or 2000-01 or 2000-01-15')
                p_summary_monthly.add_argument('category')

                p_summary_yearly = sp_summary.add_parser('yearly')
                p_summary_yearly.set_defaults(command='yearly')
                p_summary_yearly.set_defaults(parser=p_summary_yearly)
                p_summary_yearly.add_argument('--balance', action='store_true')
                p_summary_yearly.add_argument('--nopaymentplans', action='store_true')
                p_summary_yearly.add_argument('--paymentplansonly', action='store_true')
                p_summary_yearly.add_argument('--paymentplan')
                p_summary_yearly.add_argument('--paymentplangroup')
                p_summary_yearly.add_argument('--after', metavar='AFTER-DATERANGE')
                p_summary_yearly.add_argument('--after-or-from', metavar='AFTER-OR-FROM-DATERANGE')
                p_summary_yearly.add_argument('--before', metavar='BEFROE-DATERANGE')
                p_summary_yearly.add_argument('--before-or-from', metavar='BEFORE-FROM-DATERANGE')
                p_summary_yearly.add_argument('--from', metavar='FROM-DATERANGE', help='i.e. 2000 or 2000-01 or 2000-01-15')
                p_summary_yearly.add_argument('category')

                try:
                        arguments = parser.parse_args(shlex.split(args))
                except Exception as e:
                        # parse errors already handled by parser (printed to user)
                        # no further handling
                        return

                d_commands = {
                        'categories': cmd_categories,
                        'paymentplansprediction': cmd_paymentplansprediction,
                        'monthly': cmd_monthly,
                        'yearly': cmd_yearly
                }

                if not 'command' in arguments.__dict__:
                        parser.print_help()
                else:
                        try:
                                d_commands[arguments.__dict__['command']](arguments)
                        except Exception as e:
                                self.print_error(e)
                                arguments.__dict__['parser'].print_help()
                                return

        def do_export(self, args):
                'Exports data from the given date range. Outputs pyMoney cli commands. Use export -h for more details.'

                def cmd_export(arguments):
                        after_daterange = self.parse_daterange(">", arguments.__dict__['after'])
                        after_or_from_daterange = self.parse_daterange(">=", arguments.__dict__['after_or_from'])
                        before_daterange = self.parse_daterange("<", arguments.__dict__['before'])
                        before_or_from_daterange = self.parse_daterange("<=", arguments.__dict__['before_or_from'])
                        from_daterange = self.parse_daterange("=", arguments.__dict__['from'])
                        transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(from_daterange, before_daterange, before_or_from_daterange, after_daterange, after_or_from_daterange)

                        paymentplanfilter = lib.data.filterchain.Filter(lambda pp: True)

                        if arguments.__dict__['category']:
                                try:
                                        category = self.pyMoney.moneydata.get_category(arguments.__dict__['category'])
                                        transactionfilter = transactionfilter.and_concat(
                                                self.pyMoney.filterFactory.create_or_category_transactionfilter(arguments.__dict__['category'], arguments.__dict__['category'])
                                        )
                                        paymentplanfilter = paymentplanfilter.and_concat(
                                                lib.data.filterchain.Filter(lambda pp: pp.fromcategory.is_contained_in_subtree(category) or pp.tocategory.is_contained_in_subtree(category))
                                        )
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        if arguments.__dict__['fromcategory'] or arguments.__dict__['tocategory']:
                                try:
                                        if arguments.__dict__['fromcategory']:
                                                fromcategory = self.pyMoney.moneydata.get_category(arguments.__dict__['fromcategory'])
                                                paymentplanfilter = paymentplanfilter.and_concat(
                                                        lib.data.filterchain.Filter(lambda pp: pp.fromcategory.is_contained_in_subtree(fromcategory))
                                                )
                                        if arguments.__dict__['tocategory']:
                                                tocategory = self.pyMoney.moneydata.get_category(arguments.__dict__['tocategory'])
                                                paymentplanfilter = paymentplanfilter.and_concat(
                                                        lib.data.filterchain.Filter(lambda pp: pp.tocategory.is_contained_in_subtree(tocategory))
                                                )

                                        transactionfilter = transactionfilter.and_concat(
                                                self.pyMoney.filterFactory.create_and_category_transactionfilter(arguments.__dict__['fromcategory'], arguments.__dict__['tocategory'])
                                        )
                                except Exception as e:
                                        self.print_error(e)
                                        return

                        categories_iterator = self.pyMoney.get_moneydata().get_categories_iterator()
                        transactions_iterator = self.pyMoney.get_moneydata().filter_transactions(transactionfilter)
                        paymentplans_iterator = self.pyMoney.get_moneydata().get_paymentplans_iterator()

                        for c in categories_iterator:
                                assert isinstance(c, lib.data.moneydata.CategoryTreeNode)

                                if c.parent is None:
                                        continue
                                assert isinstance(c.parent, lib.data.moneydata.CategoryTreeNode)

                                parent_category_name = c.parent.get_full_name()
                                category_name = c.name

                                self.print('category add \"' + parent_category_name + '\" \"' + category_name + '\"')

                        for pp in paymentplans_iterator:
                                assert isinstance(pp, lib.data.moneydata.PaymentPlan)
                                assert isinstance(pp.fromcategory, lib.data.moneydata.CategoryTreeNode)
                                assert isinstance(pp.tocategory, lib.data.moneydata.CategoryTreeNode)

                                if not paymentplanfilter(pp):
                                        continue

                                self.print('paymentplan add "' + pp.name + '" "' + pp.groupname + '" "' + pp.fromcategory.get_full_name() + '" "' + pp.tocategory.get_full_name() + '" ' + str(pp.amount) + ' "' + pp.comment + '"')

                        for t in transactions_iterator:
                                assert isinstance(t, lib.data.moneydata.Transaction)
                                assert isinstance(t.fromcategory, lib.data.moneydata.CategoryTreeNode)
                                assert isinstance(t.tocategory, lib.data.moneydata.CategoryTreeNode)

                                if t.paymentplan is None:
                                        self.print('transaction add ' + str(t.date) + ' "' + t.fromcategory.get_full_name() + '" "' + t.tocategory.get_full_name() + '" ' + str(t.amount) + ' "' + t.comment + '"')
                                else:
                                        assert isinstance(t.paymentplan, lib.data.moneydata.PaymentPlan)

                                        update_paymentplan = False
                                        if not t.fromcategory is t.paymentplan.fromcategory:
                                                update_paymentplan = True
                                        if not t.tocategory is t.paymentplan.tocategory:
                                                update_paymentplan = True

                                        if update_paymentplan:
                                                self.print('paymentplan edit "' + t.paymentplan.name + '" "' + t.paymentplan.groupname + '" "' + t.fromcategory.get_unique_name() + '" "' + t.tocategory.get_unique_name() + '" ' + str(t.paymentplan.amount) + ' "' + t.paymentplan.comment + '"')

                                        if t.amount == t.paymentplan.amount:
                                                self.print('paymentplan execute "' + t.paymentplan.name + '" ' + str(t.date))
                                        else:
                                                self.print('paymentplan execute "' + t.paymentplan.name + '" ' + str(t.date) + ' ' + str(t.amount))


                                        if update_paymentplan:
                                                self.print('paymentplan edit "' + t.paymentplan.name + '" "' + t.paymentplan.groupname + '" "' + t.paymentplan.fromcategory.get_unique_name() + '" "' + t.paymentplan.tocategory.get_unique_name() + '" ' + str(t.paymentplan.amount) + ' "' + t.paymentplan.comment + '"')


                parser = lib.argparse.ArgumentParser()
                parser.add_argument('--after', metavar='AFTER-DATERANGE')
                parser.add_argument('--after-or-from', metavar='AFTER-OR-FROM-DATERANGE')
                parser.add_argument('--before', metavar='BEFROE-DATERANGE')
                parser.add_argument('--before-or-from', metavar='BEFORE-FROM-DATERANGE')
                parser.add_argument('--from', metavar='FROM-DATERANGE', help='i.e. 2000 or 2000-01 or 2000-01-15')
                parser.add_argument('--category')
                parser.add_argument('--fromcategory')
                parser.add_argument('--tocategory')

                try:
                        if args == '""':
                                args = ''

                        arguments = parser.parse_args(shlex.split(args))
                except Exception as e:
                        # parse errors already handled by parser (printed to user)
                        # no further handling
                        return

                try:
                        cmd_export(arguments)
                except Exception as e:
                        self.print_error(e)
                        parser.print_help()
                        return

        def do_quit(self, args):
                'Quits the application.'
                if self.writeOnQuit:
                        self.pyMoney.write()

                return True

        ### additional help entries
        def help_parameters(self):
                self.stdout.write("--fileprefix [prefix]\t- loads data from [prefix].transactions, [prefix].categories files. Default value: 'pymoney'\n")
                self.stdout.write('--script\t\t- Executes commands piped from stdin\n')
                self.stdout.write('--cli\t\t\t- Shows a prompt and executes commands from stdin\n')

        ### Cmd behaviour
        def emptyline(self):
                return

        def precmd(self, line):
                if line == 'EOF':
                        return 'quit'
                else:
                        return line

        def get_argument_parser(self):
                p_main = lib.argparse.ArgumentParser()
                p_main.add_argument('--fileprefix', default='pymoney')
                p_main.add_argument('--script', action='store_true')
                p_main.add_argument('--cli', action='store_true')
                p_main.add_argument('command', nargs=argparse.REMAINDER)

                return p_main

        def do_help(self, arg):
                parser = lib.argparse.ArgumentParser()
                parser.add_argument('command', nargs='?')

                arguments = parser.parse_args(shlex.split(arg))

                cmd.Cmd.do_help(self, arguments.__dict__['command'])

        def main(self):
                if self.arguments.__dict__['script']:
                        self.is_interactive = False
                        self.prompt = '.'
                        self.cmdloop()
                elif self.arguments.__dict__['cli']:
                        self.cmdloop()
                else:
                        argv = self.arguments.__dict__['command']

                        if len(argv) > 0:
                                self.onecmd(argv[0] + ' "' + '" "'.join(argv[1:]) + '"')
                                self.do_quit([])
                        else:
                                self.do_help('')


if __name__ == '__main__':
        argv = sys.argv[1:]
        if len(sys.argv)>1 and sys.argv[1] in ('-h', '--help'):
                if len(sys.argv)>2:
                        argv = sys.argv[2:] + [sys.argv[1]]
                else:
                        argv = []

        pymoneyconsole = PyMoneyConsole(argv)
        pymoneyconsole.main()
