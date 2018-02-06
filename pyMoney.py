#!/usr/bin/python3

import lib.app
import lib.formatter
import lib.data
import lib.data.filter
import lib.data.moneydata
import lib.io

import argparse
import calendar
import datetime
import sys


class PyMoneyConsole(lib.app.PyMoney):
	def __init__(self, argv):
		self.argumentparser = self.get_argument_parser()
		self.arguments = self.argumentparser.parse_args(argv)
		self.arguments_dict = self.arguments.__dict__

		lib.app.PyMoney.__init__(self, self.arguments_dict["fileprefix"])
		self.read()

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
		else:
			value = "unhandled exception: " + error.__class__.__module__ + "." + error.__class__.__name__ + ": " + str(error)

		if not value is None:
			print(value, file=sys.stderr)

	def cmdgroup_transaction(self, parser):
		def cmd_add():
			try:
				self.moneydata.add_transaction(	self.arguments_dict["date"], self.arguments_dict["fromcategory"], self.arguments_dict["tocategory"], self.arguments_dict["amount"],
								self.arguments_dict["comment"], self.arguments_dict["force"])
				self.write()
			except Exception as e:
				self.print_error(e)

		def cmd_list():
			transactionfilter = self.filterFactory.create_and_date_transactionfilter(self.arguments_dict["year"], self.arguments_dict["month"], self.arguments_dict["day"])
			summarycategory = None

			if self.arguments_dict["category"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.filterFactory.create_or_category_transactionfilter(self.arguments_dict["category"], self.arguments_dict["category"])
					)
					summarycategory = self.moneydata.get_category(self.arguments_dict["category"])
				except Exception as e:
					self.print_error(e)
					return

			if self.arguments_dict["fromcategory"] or self.arguments_dict["tocategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.filterFactory.create_and_category_transactionfilter(self.arguments_dict["fromcategory"], self.arguments_dict["tocategory"])
					)

					if self.arguments_dict["fromcategory"]:
						summarycategory = self.moneydata.get_category(self.arguments_dict["fromcategory"])
					if self.arguments_dict["tocategory"]:
						summarycategory = self.moneydata.get_category(self.arguments_dict["tocategory"])
				except Exception as e:
					self.print_error(e)
					return

			headerdata = ["Index", "Date", "FromCategory", "ToCategory", "Amount", "Comment"]
			tabledata = []

			fromcategory_name_formatter = lib.formatter.CategoryNameFormatter()
			tocategory_name_formatter = lib.formatter.CategoryNameFormatter()
			if self.arguments_dict["fullnamecategories"]:
				fromcategory_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
				tocategory_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)

			iterator = self.moneydata.filter_transactions(transactionfilter)
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

			d_summary = self.moneydata.create_summary(transactionfilter)

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


		def cmd_delete():
			self.moneydata.delete_transaction(self.arguments_dict["index"])
			self.write()

		d_commands = {
			"add": cmd_add,
			"delete": cmd_delete,
			"list": cmd_list
		}

		if not "command" in self.arguments_dict:
			parser.print_help()
		else:
			d_commands[self.arguments_dict["command"]]()

	def cmdgroup_category(self, parser):
		def cmd_tree():
			category_name_formatter = lib.formatter.CategoryNameFormatter()
			category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
			category_name_formatter.set_indent_with_tree_level(True)

			if self.arguments_dict["fullnamecategories"]:
				category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)
				category_name_formatter.set_indent_with_tree_level(False)

			for c in self.moneydata.categorytree:
				print(category_name_formatter.format(c))

		def cmd_list():
			category_name_formatter = lib.formatter.CategoryNameFormatter()
			if self.arguments_dict["fullnamecategories"]:
				category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_FULL_NAME)

			for category in self.moneydata.categorytree:
				_category = category_name_formatter.format(category)
				print(_category)
			print("")

		def cmd_add():
			try:
				self.moneydata.add_category(self.arguments_dict["parentname"], self.arguments_dict["name"])
				self.write()
			except Exception as e:
				self.print_error(e)

		def cmd_delete():
			try:
				self.moneydata.delete_category(self.arguments_dict["name"])
				self.write()
			except Exception as e:
				self.print_error(e)

		def cmd_move():
			try:
				self.moneydata.move_category(self.arguments_dict["name"], self.arguments_dict["newparentname"])
				self.write()
			except Exception as e:
				self.print_error(e)

		def cmd_rename():
			try:
				self.moneydata.rename_category(self.arguments_dict["name"], self.arguments_dict["newname"])
				self.write()
			except Exception as e:
				self.print_error(e)

		def cmd_merge():
			try:
				self.moneydata.merge_category(self.arguments_dict["name"], self.arguments_dict["targetname"])
				self.write()
			except Exception as e:
				self.print_error(e)

		d_commands = {
			"add": cmd_add,
			"delete": cmd_delete,
			"move": cmd_move,
			"rename": cmd_rename,
			"merge": cmd_merge,
			"list": cmd_list,
			"tree": cmd_tree
		}

		if not "command" in self.arguments_dict:
			parser.print_help()
		else:
			d_commands[self.arguments_dict["command"]]()

	def cmdgroup_summary(self, parser):
		def cmd_categories():
			transactionfilter = self.filterFactory.create_and_date_transactionfilter(self.arguments_dict["year"], self.arguments_dict["month"], self.arguments_dict["day"])

			if self.arguments_dict["cashflowcategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.filterFactory.create_or_category_transactionfilter(self.arguments_dict["cashflowcategory"], self.arguments_dict["cashflowcategory"])
					)
				except Exception as e:
					self.print_error(e)
					return

			categoryfilter = lib.data.filter.Filter(lambda c: True)
			if self.arguments_dict["maxlevel"]:
				categoryfilter = categoryfilter.and_concat(self.filterFactory.create_maxlevel_categoryfilter(self.arguments_dict["maxlevel"]))

			if self.arguments_dict["category"]:
				categoryfilter = categoryfilter.and_concat(self.filterFactory.create_subtree_categoryfilter(self.arguments_dict["category"]))

			d_summary = self.moneydata.create_summary(transactionfilter)
			category_name_formatter = lib.formatter.CategoryNameFormatter()
			category_name_formatter.set_strategy(lib.formatter.CategoryNameFormatter.STRATEGY_NAME)
			category_name_formatter.set_indent_with_tree_level(True)

			headerdata = ["node", "amount", "sum +", "sum -", "sum"]
			tabledata = []

			for category in lib.data.filter.FilterIterator(self.moneydata.categorytree.__iter__(), categoryfilter):
				key = category.get_unique_name()
				name = category_name_formatter.format(category)
				if not self.arguments_dict["showempty"] and d_summary[key].sumcount == 0:
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
					transactionfilter = self.filterFactory.create_and_date_transactionfilter(str(year), str(month), None)
				elif diff_months == 12:
					transactionfilter = self.filterFactory.create_and_date_transactionfilter(str(year), None, None)
				else:
					raise Exception("diff_months value not supported: " + str(diff_months))

				if calculate_balance:
					d_summary = self.moneydata.create_summary(transactionfilter, d_summary)
				else:
					d_summary = self.moneydata.create_summary(transactionfilter, None)

				displayday = calendar.monthrange(year, month)[1]
				if diff_months != 12:
					displaymonth = month
				else:
					displaymonth = 12
				
				tabledata.append([str(datetime.date(year, displaymonth, displayday)), name,
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

		def cmd_monthly():
			mindate = None
			maxdate = None
			for transaction in self.moneydata.transactions:
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			try:
				category = self.moneydata.get_category(self.arguments_dict["category"])
			except Exception as e:
			    self.print_error(e)
			    return

			sub_time_interval_summary(category, mindate.year, mindate.month, 1, maxdate, self.arguments_dict["balance"])

		def cmd_yearly():
			mindate = None
			maxdate = None
			for transaction in self.moneydata.transactions:
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			try:
				category = self.moneydata.get_category(self.arguments_dict["category"])
			except Exception as e:
			    self.print_error(e)
			    return

			sub_time_interval_summary(category, mindate.year, 1, 12, maxdate, self.arguments_dict["balance"])

		d_commands = {
			"categories": cmd_categories,
			"monthly": cmd_monthly,
			"yearly": cmd_yearly
		}

		if not "command" in self.arguments_dict:
			parser.print_help()
		else:
			d_commands[self.arguments_dict["command"]]()

	def get_argument_parser(self):
		p_main = argparse.ArgumentParser()
		p_main.add_argument("--fileprefix", default="pymoney")
		sp_main = p_main.add_subparsers(title="object")

		### transactions
		p_transaction = sp_main.add_parser("transaction")
		p_transaction.set_defaults(func=self.cmdgroup_transaction)
		p_transaction.set_defaults(parser=p_transaction)
		p_transaction.add_argument("--fullnamecategories", action="store_true")
		sp_transaction = p_transaction.add_subparsers(title="command")

		p_transaction_add = sp_transaction.add_parser("add")
		p_transaction_add.set_defaults(command="add")
		p_transaction_add.add_argument("date")
		p_transaction_add.add_argument("fromcategory")
		p_transaction_add.add_argument("tocategory")
		p_transaction_add.add_argument("amount", type=float)
		p_transaction_add.add_argument("comment", default="", nargs='?')
		p_transaction_add.add_argument("--force", action="store_true")

		p_transaction_delete = sp_transaction.add_parser("delete")
		p_transaction_delete.set_defaults(command="delete")
		p_transaction_delete.add_argument("index", type=int)

		p_transaction_list = sp_transaction.add_parser("list")
		p_transaction_list.set_defaults(command="list")
		p_transaction_list.add_argument("year", nargs='?')
		p_transaction_list.add_argument("month", type=int, nargs='?')
		p_transaction_list.add_argument("day", type=int, nargs='?')
		p_transaction_list.add_argument("--category")
		p_transaction_list.add_argument("--fromcategory")
		p_transaction_list.add_argument("--tocategory")

		### categories
		p_category = sp_main.add_parser("category")
		p_category.set_defaults(func=self.cmdgroup_category)
		p_category.set_defaults(parser=p_category)
		p_category.add_argument("--fullnamecategories", action="store_true")
		sp_category = p_category.add_subparsers(title="command")

		p_category_add = sp_category.add_parser("add")
		p_category_add.set_defaults(command="add")
		p_category_add.add_argument("parentname")
		p_category_add.add_argument("name")

		p_category_delete = sp_category.add_parser("delete")
		p_category_delete.set_defaults(command="delete")
		p_category_delete.add_argument("name")

		p_category_merge = sp_category.add_parser("merge")
		p_category_merge.set_defaults(command="merge")
		p_category_merge.add_argument("name")
		p_category_merge.add_argument("targetname")

		p_category_move = sp_category.add_parser("move")
		p_category_move.set_defaults(command="move")
		p_category_move.add_argument("name")
		p_category_move.add_argument("newparentname")

		p_category_rename = sp_category.add_parser("rename")
		p_category_rename.set_defaults(command="rename")
		p_category_rename.add_argument("name")
		p_category_rename.add_argument("newname")

		p_category_list = sp_category.add_parser("tree")
		p_category_list.set_defaults(command="tree")

		p_category_listnames = sp_category.add_parser("list")
		p_category_listnames.set_defaults(command="list")

		### summary
		p_summary = sp_main.add_parser("summary")
		p_summary.set_defaults(func=self.cmdgroup_summary)
		p_summary.set_defaults(parser=p_summary)
		sp_summary = p_summary.add_subparsers(title="command")

		p_summary_categories = sp_summary.add_parser("categories")
		p_summary_categories.set_defaults(command="categories")
		p_summary_categories.add_argument("--maxlevel", type=int, nargs='?')
		p_summary_categories.add_argument("--showempty", action='store_true')
		p_summary_categories.add_argument("--cashflowcategory")
		p_summary_categories.add_argument("--category")
		p_summary_categories.add_argument("year", nargs='?')
		p_summary_categories.add_argument("month", type=int, nargs='?')
		p_summary_categories.add_argument("day", type=int, nargs='?')

		p_summary_monthly = sp_summary.add_parser("monthly")
		p_summary_monthly.set_defaults(command="monthly")
		p_summary_monthly.add_argument("--balance", action='store_true')
		p_summary_monthly.add_argument("category")

		p_summary_yearly = sp_summary.add_parser("yearly")
		p_summary_yearly.set_defaults(command="yearly")
		p_summary_yearly.add_argument("--balance", action='store_true')
		p_summary_yearly.add_argument("category")

		return p_main

	def main(self):
		try:
			self.arguments.func(self.arguments.parser)
		except AttributeError:
			self.argumentparser.print_help()


if __name__ == "__main__":
	pymoneyconsole = PyMoneyConsole(sys.argv[1:])
	pymoneyconsole.main()
