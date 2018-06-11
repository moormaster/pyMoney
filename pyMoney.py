#!/usr/bin/python3

import lib.app
import lib.argparse
import lib.formatter
import lib.data
import lib.data.filter
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

		if len(argv) == 1 or line.endswith(" "):
			argv.append("")

		if len(argv) >= 2:
			if argv[1] == "add":
				# from-category, to-category
				if len(argv) == 4 or len(argv) == 5:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
			elif argv[1] == "list":
				parameters = ['category', 'fromcategory', 'tocategory']

				if argv[-2] in ["--category", "--fromcategory", "--tocategory"]:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
				elif len(argv) >= 3:
					if argv[-1].startswith("--"):
						return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
					elif argv[-1].startswith("-"):
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "-"+v, parameters))))
					else:
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "--"+v, parameters))))
			elif len(argv) == 2:
				return list(filter(lambda v: v.startswith(argv[-1]), ['add', 'list', 'delete']))

	def complete_category(self, text, line, begidx, endidx):
		if endidx < len(line):
			return

		argv = shlex.split(line)

		if len(argv) == 1 or line.endswith(" "):
			argv.append("")

		if len(argv) >= 2:
			if argv[1] == "add":
				# parent-category
				if len(argv) == 3:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
			elif argv[1] == "delete" or argv[1] == "rename":
				# category
				if len(argv) == 3:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
			elif argv[1] == "merge" or argv[1] == "move":
				# category, target-category
				if len(argv) == 3 or len(argv) == 4:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
			elif argv[1] == "list" or argv[1] == "tree":
				if len(argv) == 3:
					parameters = ['fullnamecategories']

					if argv[-1].startswith("--"):
						return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
					elif argv[-1].startswith("-"):
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "-"+v, parameters))))
					else:
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "--"+v, parameters))))
			elif len(argv) == 2:
				return list(filter(lambda v: v.startswith(argv[-1]), ['add', 'delete', 'list', 'merge', 'move', 'rename', 'tree']))

	def complete_summary(self, text, line, begidx, endidx):
		if endidx < len(line):
			return

		argv = shlex.split(line)

		if len(argv) == 1 or line.endswith(" "):
			argv.append("")

		if len(argv) >= 2:
			if argv[1] == "categories":
				parameters = ['category', 'cashflowcategory', 'showempty',  'maxlevel']

				if argv[-2] in ["--category", "--cashflowcategory"]:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
				elif len(argv) >= 3:
					if argv[-1].startswith("--"):
						return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
					else:
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "--"+v, parameters))))
			elif argv[1] == "monthly" or argv[1] == "yearly":
				if len(argv) == 3:
					categories = self.pyMoney.get_moneydata().get_categories_iterator()
					categorynames = map(lambda c: c.get_unique_name(), categories)
					categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

					return list(categorynames)
				if len(argv) == 4:
					parameters = ['balance']

					if argv[-1].startswith("--"):
						return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
					elif argv[-1].startswith("-"):
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "-"+v, parameters))))
					else:
						return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "--"+v, parameters))))
			elif len(argv) == 2:
				return list(filter(lambda v: v.startswith(argv[-1]), ['categories', 'monthly', 'yearly']))

	def complete_export(self, text, line, begidx, endidx):
		if endidx < len(line):
			return

		argv = shlex.split(line)

		if len(argv) == 1 or line.endswith(" "):
			argv.append("")

		if len(argv) >= 2:
			parameters = ['category', 'fromcategory', 'tocategory']

			if argv[-2] in ["--category", "--fromcategory", "--tocategory"]:
				categories = self.pyMoney.get_moneydata().get_categories_iterator()
				categorynames = map(lambda c: c.get_unique_name(), categories)
				categorynames = filter(lambda v: v.startswith(argv[-1]), categorynames)

				return list(categorynames)
			elif len(argv) >= 3:
				if argv[-1].startswith("--"):
					return list(filter(lambda v: v.startswith(argv[-1][2:]), parameters))
				elif argv[-1].startswith("-"):
					return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "-"+v, parameters))))
				else:
					return list(filter(lambda v: v.startswith(argv[-1]), list(map(lambda v: "--"+v, parameters))))


class PyMoneyConsole(cmd.Cmd):
	def __init__(self, argv):
		cmd.Cmd.__init__(self)

		self.prompt = '(pyMoney) '

		parser = self.get_argument_parser()
		self.arguments = parser.parse_args(argv)

		self.pyMoney = lib.app.PyMoney(self.arguments.__dict__["fileprefix"])
		self.pyMoney.read()

		self.completion = PyMoneyCompletion(self.pyMoney)

		self.writeOnQuit = False

	def print_error(self, error):
		value = None

		if isinstance(error, lib.data.moneydata.NoSuchCategoryException):
			value = "category not found: " + error.name
		elif isinstance(error, lib.data.moneydata.DuplicateCategoryException):
			value = "category already exists: " + error.category.get_unique_name()
		elif isinstance(error, lib.data.moneydata.CategoryIsTopCategoryException):
			value = "top category may not be deleted: " + error.category.get_unique_name()
		elif isinstance(error, lib.data.moneydata.AmbiguousCategoryNameException):
			value = "category name " + error.name + " is ambiguous: " + str(list(map(lambda c: c.get_unique_name(), error.matching_categories)))
		elif isinstance(error, lib.data.tree.TargetNodeIsPartOfSourceNodeSubTreeException):
			value = "cannot move source node into its own subtree: " + str(error.sourcenode.get_unique_name())
		elif isinstance(error, ValueError):
			value = str(error)
		else:
			value = "unhandled exception: " + error.__class__.__module__ + "." + error.__class__.__name__ + ": " + str(error)

		if not value is None:
			print(value, file=sys.stderr)

	### Cmd completion
	def complete_export(self, text, line, beginidx, endidx):
		return self.completion.complete_export(text, line, beginidx, endidx)

	def complete_transaction(self, text, line, beginidx, endidx):
		return self.completion.complete_transaction(text, line, beginidx, endidx)

	def complete_category(self, text, line, beginidx, endidx):
		return self.completion.complete_category(text, line, beginidx, endidx)

	def complete_summary(self, text, line, beginidx, endidx):
		return self.completion.complete_summary(text, line, beginidx, endidx)

	### Cmd commands
	def do_transaction(self, args):
		'Adds, deletes or lists transaction(s). Use transaction -h for more details.'
		def cmd_add(arguments):
			try:
				self.pyMoney.get_moneydata().add_transaction(	arguments.__dict__["date"], arguments.__dict__["fromcategory"], arguments.__dict__["tocategory"], arguments.__dict__["amount"],
								arguments.__dict__["comment"], arguments.__dict__["force"])
				self.writeOnQuit = True
			except Exception as e:
				self.print_error(e)

		def cmd_list(arguments):
			transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(arguments.__dict__["year"], arguments.__dict__["month"], arguments.__dict__["day"])

			summarycategory = None

			if arguments.__dict__["category"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.pyMoney.filterFactory.create_or_category_transactionfilter(arguments.__dict__["category"], arguments.__dict__["category"])
					)
					summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__["category"])
				except Exception as e:
					self.print_error(e)
					return

			if arguments.__dict__["fromcategory"] or arguments.__dict__["tocategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.pyMoney.filterFactory.create_and_category_transactionfilter(arguments.__dict__["fromcategory"], arguments.__dict__["tocategory"])
					)

					if arguments.__dict__["fromcategory"]:
						summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__["fromcategory"])
					if arguments.__dict__["tocategory"]:
						summarycategory = self.pyMoney.get_moneydata().get_category(arguments.__dict__["tocategory"])
				except Exception as e:
					self.print_error(e)
					return

			headerdata = ["Index", "Date", "FromCategory", "ToCategory", "Amount", "Comment"]
			tabledata = []

			fromcategory_name_formatter = lib.formatter.CategoryNameFormatter()
			tocategory_name_formatter = lib.formatter.CategoryNameFormatter()
			if arguments.__dict__["fullnamecategories"]:
				fromcategory_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
				tocategory_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)

			iterator = self.pyMoney.get_moneydata().filter_transactions(transactionfilter)
			for d in iterator:
				assert isinstance(d.fromcategory, lib.data.moneydata.CategoryTreeNode)
				assert isinstance(d.tocategory, lib.data.moneydata.CategoryTreeNode)

				_index = iterator.index
				_date = str(d.date)

				_fromcategory = fromcategory_name_formatter.format(d.fromcategory)
				_tocategory = tocategory_name_formatter.format(d.tocategory)

				_amount = d.amount
				_comment = d.comment

				tabledata.append([_index, _date, _fromcategory, _tocategory, _amount, _comment])

			d_summary = self.pyMoney.get_moneydata().create_summary(transactionfilter)

			if summarycategory:
				_summarycategory = tocategory_name_formatter.format(summarycategory)
				key = summarycategory.get_unique_name()

				tabledata.append(["", "", "", "", None, ""])
				tabledata.append(["", "", "", "+ " + _summarycategory, d_summary[key].sumin, ""])
				tabledata.append(["", "", "", "- " + _summarycategory, d_summary[key].sumout, ""])
				tabledata.append(["", "", "", "sum " + _summarycategory, d_summary[key].sum, ""])

			tableformatter = lib.formatter.TableFormatter()
			column = tableformatter.add_column(0)
			column.set_alignment(">")
			column = tableformatter.add_column(1)
			column.set_alignment(">")
			tableformatter.add_column(2)
			tableformatter.add_column(3)
			column = tableformatter.add_column(4)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			tableformatter.add_column(5)

			lines = tableformatter.get_formatted_lines(headerdata, tabledata)

			is_first_line = True
			for line in lines:
				print(line)
				if is_first_line:
					print("")

				is_first_line = False

		def cmd_delete(arguments):
			self.pyMoney.get_moneydata().delete_transaction(arguments.__dict__["index"])
			self.writeOnQuit = True

		parser = lib.argparse.ArgumentParser()
		parser.add_argument("--fullnamecategories", action="store_true")
		sp_transaction = parser.add_subparsers(title="command")

		p_transaction_add = sp_transaction.add_parser("add")
		p_transaction_add.set_defaults(command="add")
		p_transaction_add.set_defaults(parser=p_transaction_add)
		p_transaction_add.add_argument("date")
		p_transaction_add.add_argument("fromcategory")
		p_transaction_add.add_argument("tocategory")
		p_transaction_add.add_argument("amount", type=float)
		p_transaction_add.add_argument("comment", default="", nargs='?')
		p_transaction_add.add_argument("--force", action="store_true")

		p_transaction_delete = sp_transaction.add_parser("delete")
		p_transaction_delete.set_defaults(command="delete")
		p_transaction_delete.set_defaults(parser=p_transaction_delete)
		p_transaction_delete.add_argument("index", type=int)

		p_transaction_list = sp_transaction.add_parser("list")
		p_transaction_list.set_defaults(command="list")
		p_transaction_list.set_defaults(parser=p_transaction_list)
		p_transaction_list.add_argument("year", nargs='?')
		p_transaction_list.add_argument("month", type=int, nargs='?')
		p_transaction_list.add_argument("day", type=int, nargs='?')
		p_transaction_list.add_argument("--category")
		p_transaction_list.add_argument("--fromcategory")
		p_transaction_list.add_argument("--tocategory")

		try:
			arguments = parser.parse_args(shlex.split(args))
		except Exception as e:
			# parse errors already handled by parser (printed to user)
			# no further handling
			return

		d_commands = {
			"add": cmd_add,
			"delete": cmd_delete,
			"list": cmd_list
		}

		if not "command" in arguments.__dict__:
			parser.print_help()
		else:
			try:
				d_commands[arguments.__dict__["command"]](arguments)
			except Exception as e:
				self.print_error(e)
				arguments.__dict__["parser"].print_help()
				return

	def do_category(self, args):
		'Adds, deletes, merges, moves or lists categories. Use category -h for more details.'
		def cmd_tree(arguments):
			category_name_formatter = lib.formatter.CategoryNameFormatter()
			category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
			category_name_formatter.set_indent_with_tree_level(True)

			if arguments.__dict__["fullnamecategories"]:
				category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
				category_name_formatter.set_indent_with_tree_level(False)

			for c in self.pyMoney.get_moneydata().get_categories_iterator():
				print(category_name_formatter.format(c))

		def cmd_list(arguments):
			category_name_formatter = lib.formatter.CategoryNameFormatter()
			if arguments.__dict__["fullnamecategories"]:
				category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)

			for category in self.pyMoney.get_moneydata().get_categories_iterator():
				_category = category_name_formatter.format(category)
				print(_category)
			print("")

		def cmd_add(arguments):
			try:
				self.pyMoney.get_moneydata().add_category(arguments.__dict__["parentname"], arguments.__dict__["name"])
				self.writeOnQuit = True
			except Exception as e:
				self.print_error(e)

		def cmd_delete(arguments):
			try:
				self.pyMoney.get_moneydata().delete_category(arguments.__dict__["name"])
				self.writeOnQuit = True
			except Exception as e:
				self.print_error(e)

		def cmd_move(arguments):
			try:
				self.pyMoney.get_moneydata().move_category(arguments.__dict__["name"], arguments.__dict__["newparentname"])
				self.writeOnQuit = True
			except Exception as e:
				self.print_error(e)

		def cmd_rename(arguments):
			try:
				self.pyMoney.get_moneydata().rename_category(arguments.__dict__["name"], arguments.__dict__["newname"])
				self.writeOnQuit = True
			except Exception as e:
				self.print_error(e)

		def cmd_merge(arguments):
			try:
				self.pyMoney.get_moneydata().merge_to_category(arguments.__dict__["name"], arguments.__dict__["targetname"])
				self.writeOnQuit = True
			except Exception as e:
				self.print_error(e)

		parser = lib.argparse.ArgumentParser()
		sp_category = parser.add_subparsers(title="command")

		p_category_add = sp_category.add_parser("add")
		p_category_add.set_defaults(command="add")
		p_category_add.set_defaults(parser=p_category_add)
		p_category_add.add_argument("parentname")
		p_category_add.add_argument("name")

		p_category_delete = sp_category.add_parser("delete")
		p_category_delete.set_defaults(command="delete")
		p_category_delete.set_defaults(parser=p_category_delete)
		p_category_delete.add_argument("name")

		p_category_merge = sp_category.add_parser("merge")
		p_category_merge.set_defaults(command="merge")
		p_category_merge.set_defaults(parser=p_category_merge)
		p_category_merge.add_argument("name")
		p_category_merge.add_argument("targetname")

		p_category_move = sp_category.add_parser("move")
		p_category_move.set_defaults(command="move")
		p_category_move.set_defaults(parser=p_category_move)
		p_category_move.add_argument("name")
		p_category_move.add_argument("newparentname")

		p_category_rename = sp_category.add_parser("rename")
		p_category_rename.set_defaults(command="rename")
		p_category_rename.set_defaults(parser=p_category_rename)
		p_category_rename.add_argument("name")
		p_category_rename.add_argument("newname")

		p_category_tree = sp_category.add_parser("tree")
		p_category_tree.set_defaults(command="tree")
		p_category_tree.set_defaults(parser=p_category_tree)
		p_category_tree.add_argument("--fullnamecategories", action="store_true")

		p_category_list = sp_category.add_parser("list")
		p_category_list.set_defaults(command="list")
		p_category_list.set_defaults(parser=p_category_list)
		p_category_list.add_argument("--fullnamecategories", action="store_true")

		try:
			arguments = parser.parse_args(shlex.split(args))
		except Exception as e:
			# parse errors already handled by parser (printed to user)
			# no further handling
			return

		d_commands = {
			"add": cmd_add,
			"delete": cmd_delete,
			"move": cmd_move,
			"rename": cmd_rename,
			"merge": cmd_merge,
			"list": cmd_list,
			"tree": cmd_tree
		}

		if not "command" in arguments.__dict__:
			parser.print_help()
		else:
			try:
				d_commands[arguments.__dict__["command"]](arguments)
			except Exception as e:
				self.print_error(e)
				arguments.__dict__["parser"].print_help()
				return

	def do_summary(self, args):
		'Prints a summarized report across categories / date intervals. Use summary -h for more details.'
		def cmd_categories(arguments):
			transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(arguments.__dict__["year"], arguments.__dict__["month"], arguments.__dict__["day"])

			if arguments.__dict__["cashflowcategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.pyMoney.filterFactory.create_or_category_transactionfilter(arguments.__dict__["cashflowcategory"], arguments.__dict__["cashflowcategory"])
					)
				except Exception as e:
					self.print_error(e)
					return

			categoryfilter = lib.data.filter.Filter(lambda c: True)
			if arguments.__dict__["maxlevel"]:
				categoryfilter = categoryfilter.and_concat(self.pyMoney.filterFactory.create_maxlevel_categoryfilter(arguments.__dict__["maxlevel"]))

			if arguments.__dict__["category"]:
				categoryfilter = categoryfilter.and_concat(self.pyMoney.filterFactory.create_subtree_categoryfilter(arguments.__dict__["category"]))

			d_summary = self.pyMoney.get_moneydata().create_summary(transactionfilter)
			category_name_formatter = lib.formatter.CategoryNameFormatter()
			category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
			category_name_formatter.set_indent_with_tree_level(True)

			headerdata = ["node", "amount", "sum +", "sum -", "sum"]
			tabledata = []

			for category in lib.data.filter.FilterIterator(self.pyMoney.get_moneydata().get_categories_iterator(), categoryfilter):
				key = category.get_unique_name()
				name = category_name_formatter.format(category)
				if not arguments.__dict__["showempty"] and d_summary[key].sumcount == 0:
					continue

				tabledata.append([name, d_summary[key].amount, d_summary[key].sumin, d_summary[key].sumout, d_summary[key].sum])

			tableformatter = lib.formatter.TableFormatter()
			tableformatter.add_column(0)
			column = tableformatter.add_column(1)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			column = tableformatter.add_column(2)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			column = tableformatter.add_column(3)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			column = tableformatter.add_column(4)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")

			lines = tableformatter.get_formatted_lines(headerdata, tabledata)

			is_first_line = True
			for line in lines:
				print(line)
				if is_first_line:
					print("")

				is_first_line = False

		def sub_time_interval_summary(category, start_year, start_month, diff_months, maxdate, calculate_balance):
			assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

			category_name_formatter = lib.formatter.CategoryNameFormatter()

			year = start_year
			month = start_month

			headerdata = ["date", "node", "amount", "sum +", "sum -", "sum"]
			tabledata = []

			key = category.get_unique_name()
			name = category_name_formatter.format(category)
			d_summary = None
			while datetime.date(year, month, 1) <= maxdate:
				if diff_months == 1:
					transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(str(year), str(month), None)
				elif diff_months == 12:
					transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(str(year), None, None)
				else:
					raise Exception("diff_months value not supported: " + str(diff_months))

				if calculate_balance:
					d_summary = self.pyMoney.get_moneydata().create_summary(transactionfilter, d_summary)
				else:
					d_summary = self.pyMoney.get_moneydata().create_summary(transactionfilter, None)

				displayday = calendar.monthrange(year, month)[1]
				if diff_months != 12:
					displaymonth = month
				else:
					displaymonth = 12
				
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
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			column = tableformatter.add_column(3)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			column = tableformatter.add_column(4)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")
			column = tableformatter.add_column(5)
			column.set_alignment(">")
			column.set_precision(2)
			column.set_type("f")

			lines = tableformatter.get_formatted_lines(headerdata, tabledata)

			is_first_line = True
			for line in lines:
				print(line)
				if is_first_line:
					print("")

				is_first_line = False

		def cmd_monthly(arguments):
			mindate = None
			maxdate = None
			for transaction in self.pyMoney.get_moneydata().get_transactions_iterator():
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			try:
				category = self.pyMoney.get_moneydata().get_category(arguments.__dict__["category"])
			except Exception as e:
				self.print_error(e)
				return

			sub_time_interval_summary(category, mindate.year, mindate.month, 1, maxdate, arguments.__dict__["balance"])

		def cmd_yearly(arguments):
			mindate = None
			maxdate = None
			for transaction in self.pyMoney.get_moneydata().get_transactions_iterator():
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			try:
				category = self.pyMoney.get_moneydata().get_category(arguments.__dict__["category"])
			except Exception as e:
				self.print_error(e)
				return

			sub_time_interval_summary(category, mindate.year, 1, 12, maxdate, arguments.__dict__["balance"])

		parser = lib.argparse.ArgumentParser()
		sp_summary = parser.add_subparsers(title="command")

		p_summary_categories = sp_summary.add_parser("categories")
		p_summary_categories.set_defaults(command="categories")
		p_summary_categories.set_defaults(parser=p_summary_categories)
		p_summary_categories.add_argument("--maxlevel", type=int, nargs='?')
		p_summary_categories.add_argument("--showempty", action='store_true')
		p_summary_categories.add_argument("--cashflowcategory")
		p_summary_categories.add_argument("--category")
		p_summary_categories.add_argument("year", nargs='?')
		p_summary_categories.add_argument("month", type=int, nargs='?')
		p_summary_categories.add_argument("day", type=int, nargs='?')

		p_summary_monthly = sp_summary.add_parser("monthly")
		p_summary_monthly.set_defaults(command="monthly")
		p_summary_monthly.set_defaults(parser=p_summary_monthly)
		p_summary_monthly.add_argument("--balance", action='store_true')
		p_summary_monthly.add_argument("category")

		p_summary_yearly = sp_summary.add_parser("yearly")
		p_summary_yearly.set_defaults(command="yearly")
		p_summary_yearly.set_defaults(parser=p_summary_yearly)
		p_summary_yearly.add_argument("--balance", action='store_true')
		p_summary_yearly.add_argument("category")

		try:
			arguments = parser.parse_args(shlex.split(args))
		except Exception as e:
			# parse errors already handled by parser (printed to user)
			# no further handling
			return

		d_commands = {
			"categories": cmd_categories,
			"monthly": cmd_monthly,
			"yearly": cmd_yearly
		}

		if not "command" in arguments.__dict__:
			parser.print_help()
		else:
			try:
				d_commands[arguments.__dict__["command"]](arguments)
			except Exception as e:
				self.print_error(e)
				arguments.__dict__["parser"].print_help()
				return

	def do_export(self, args):
		'Exports data from the given date range. Outputs pyMoney cli commands. Use export -h for more details.'

		def cmd_export(arguments):
			transactionfilter = self.pyMoney.filterFactory.create_and_date_transactionfilter(arguments.__dict__["year"], arguments.__dict__["month"], arguments.__dict__["day"])

			if arguments.__dict__["category"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.pyMoney.filterFactory.create_or_category_transactionfilter(arguments.__dict__["category"], arguments.__dict__["category"])
					)
				except Exception as e:
					self.print_error(e)
					return

			if arguments.__dict__["fromcategory"] or arguments.__dict__["tocategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.pyMoney.filterFactory.create_and_category_transactionfilter(arguments.__dict__["fromcategory"], arguments.__dict__["tocategory"])
					)
				except Exception as e:
					self.print_error(e)
					return

			categories_iterator = self.pyMoney.get_moneydata().get_categories_iterator()
			transactions_iterator = self.pyMoney.get_moneydata().filter_transactions(transactionfilter)

			for c in categories_iterator:
				assert isinstance(c, lib.data.moneydata.CategoryTreeNode)

				if c.parent is None:
					continue
				assert isinstance(c.parent, lib.data.moneydata.CategoryTreeNode)

				parent_category_name = c.parent.get_full_name()
				category_name = c.name

				print("category add \"" + parent_category_name + "\" \"" + category_name + "\"")

			for t in transactions_iterator:
				assert isinstance(t, lib.data.moneydata.Transaction)
				assert isinstance(t.fromcategory, lib.data.moneydata.CategoryTreeNode)
				assert isinstance(t.tocategory, lib.data.moneydata.CategoryTreeNode)

				print("transaction add " + str(t.date) + " \"" + t.fromcategory.get_full_name() + "\" \"" + t.tocategory.get_full_name() + "\" " + str(t.amount) + " \"" + t.comment + "\"")

			pass

		parser = lib.argparse.ArgumentParser()
		parser.add_argument("year", nargs='?')
		parser.add_argument("month", type=int, nargs='?')
		parser.add_argument("day", type=int, nargs='?')
		parser.add_argument("--category")
		parser.add_argument("--fromcategory")
		parser.add_argument("--tocategory")

		try:
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
		self.stdout.write("--fileprefix [prefix]\t- loads data from [prefix].transactions, [preifix].categories files. Default value: 'pymoney'\n")
		self.stdout.write("--script\t\t- Executes commands piped from stdin\n")
		self.stdout.write("--cli\t\t\t- Shows a prompt and executes commands from stdin\n")

	### Cmd behaviour
	def emptyline(self):
		return

	def precmd(self, line):
		if line == "EOF":
			return "quit"
		else:
			return line

	def get_argument_parser(self):
		p_main = lib.argparse.ArgumentParser()
		p_main.add_argument("--fileprefix", default="pymoney")
		p_main.add_argument("--script", action='store_true')
		p_main.add_argument("--cli", action='store_true')
		p_main.add_argument("command", nargs=argparse.REMAINDER)

		return p_main

	def do_help(self, arg):
		parser = lib.argparse.ArgumentParser()
		parser.add_argument("command", nargs='?')

		arguments = parser.parse_args(shlex.split(arg))

		cmd.Cmd.do_help(self, arguments.__dict__["command"])

	def main(self):
		if self.arguments.__dict__["script"]:
			self.prompt = "."
			self.cmdloop()
		elif self.arguments.__dict__["cli"]:
			self.cmdloop()
		else:
			argv = self.arguments.__dict__["command"]

			if len(argv) > 0:
				self.onecmd(argv[0] + ' "' + '" "'.join(argv[1:]) + '"')
				self.do_quit([])
			else:
				self.do_help([])

if __name__ == "__main__":
	argv = sys.argv[1:]
	if len(sys.argv)>1 and sys.argv[1] in ("-h", "--help"):
		if len(sys.argv)>2:
			argv = sys.argv[2:] + [sys.argv[1]]
		else:
			argv = []

	pymoneyconsole = PyMoneyConsole(argv)
	pymoneyconsole.main()
