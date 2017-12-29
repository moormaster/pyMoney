#!/usr/bin/python3

import lib.app
import lib.data
import lib.data.filter
import lib.data.moneydata
import lib.io

import argparse
import datetime
import sys


class PyMoneyConsole(lib.app.PyMoney):
	def __init__(self, argv):
		self.argumentparser = self.get_argument_parser()
		self.arguments = self.argumentparser.parse_args(argv)
		self.arguments_dict = self.arguments.__dict__

		lib.app.PyMoney.__init__(self, self.arguments_dict["fileprefix"])
		self.read()

	def create_and_date_transactionfilter(self, filter_year, filter_month, filter_day):
		transactionfilter = lib.data.filter.Filter(lambda t: True)

		if filter_year:
			if filter_year[0:2] == ">=":
				year = int(filter_year[2:])
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year >= year)
			elif filter_year[0:2] == "<=":
				year = int(filter_year[2:])
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year <= year)
			elif filter_year[0:1] == ">":
				year = int(filter_year[1:])
				if filter_month or filter_day:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year >= year)
				else:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year)
			elif filter_year[0:1] == "<":
				year = int(filter_year[1:])
				if filter_month or filter_day:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year <= year)
				else:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year < year)
			else:
				year = int(filter_year)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year == year)

		if filter_month:
			if filter_year and filter_year[0:2] == ">=":
				month = int(filter_month)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month >= month)
			elif filter_year and filter_year[0:2] == "<=":
				month = int(filter_month)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year < year or t.date.year == year and t.date.month <= month)
			elif filter_year and filter_year[0:1] == ">":
				month = int(filter_month)
				if filter_day:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month >= month)
				else:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month > month)
			elif filter_year and filter_year[0:1] == "<":
				month = int(filter_month)
				if filter_day:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month <= month)
				else:
					transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month < month)
			else:
				month = int(filter_month)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.month == month)

		if filter_day:
			if filter_year and filter_year[0:2] == ">=":
				day = int(filter_day)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month > month or t.date.year == year and t.date.month == month and t.date.day >= day)
			elif filter_year and filter_year[0:2] == "<=":
				day = int(filter_day)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year < year or t.date.year == year and t.date.month < month or t.date.year == year and t.date.month == month and t.date.day <= day)
			elif filter_year and filter_year[0:1] == ">":
				day = int(filter_day)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year > year or t.date.year == year and t.date.month > month or t.date.year == year and t.date.month == month and t.date.day > day)
			elif filter_year and filter_year[0:1] == "<":
				day = int(filter_day)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year < year or t.date.year == year and t.date.month < month or t.date.year == year and t.date.month == month and t.date.day < day)
			else:
				day = int(filter_day)
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.day == day)

		return transactionfilter


	def create_or_category_transactionfilter(self, filter_from_category, filter_to_category):
		transactionfilter = lib.data.filter.Filter(lambda t: False)

		if filter_from_category:
			fromcategory = self.moneydata.get_category(filter_from_category)

			if not fromcategory:
				raise lib.data.moneydata.NoSuchCategoryException(filter_from_category)

			transactionfilter = transactionfilter.or_concat(
				lambda t: t.fromcategory is fromcategory or t.fromcategory.is_contained_in_subtree(fromcategory)
			)

		if filter_to_category:
			tocategory = self.moneydata.get_category(filter_to_category)

			if not tocategory:
				raise lib.data.moneydata.NoSuchCategoryException(filter_to_category)

			transactionfilter = transactionfilter.or_concat(
				lambda t: t.tocategory is tocategory or t.tocategory.is_contained_in_subtree(tocategory)
			)

		return transactionfilter


	def create_and_category_transactionfilter(self, filter_from_category, filter_to_category):
		transactionfilter = lib.data.filter.Filter(lambda t: True)

		if filter_from_category:
			fromcategory = self.moneydata.get_category(filter_from_category)

			if not fromcategory:
				raise lib.data.moneydata.NoSuchCategoryException(filter_from_category)

			transactionfilter = transactionfilter.and_concat(
				lambda t: t.fromcategory is fromcategory or t.fromcategory.is_contained_in_subtree(fromcategory)
			)

		if filter_to_category:
			tocategory = self.moneydata.get_category(filter_to_category)

			if not tocategory:
				raise lib.data.moneydata.NoSuchCategoryException(filter_to_category)

			transactionfilter = transactionfilter.and_concat(
				lambda t: t.tocategory is tocategory or t.tocategory.is_contained_in_subtree(tocategory)
			)

		return transactionfilter


	def create_maxlevel_category_transactionfilter(self, maxlevel):
		categoryfilter = lib.data.filter.Filter(lambda c: True)

		if maxlevel:
			categoryfilter = categoryfilter.and_concat(lambda c: c.get_depth() <= maxlevel)

		return categoryfilter


	def create_subtree_category_transactionfilter(self, filter_rootcategory):
		categoryfilter = lib.data.filter.Filter(lambda c: True)

		rootcategory = self.moneydata.get_category(filter_rootcategory)

		if not rootcategory:
			raise lib.data.moneydata.NoSuchCategoryException(filter_rootcategory)

		categoryfilter = categoryfilter.and_concat(
			lambda c: c is rootcategory or c.is_contained_in_subtree(rootcategory)
		)

		return categoryfilter


	def cmdgroup_transaction(self, parser):
		def cmd_add():
			self.moneydata.add_transaction(	self.arguments_dict["date"], self.arguments_dict["fromcategory"], self.arguments_dict["tocategory"], self.arguments_dict["amount"],
													self.arguments_dict["comment"], self.arguments_dict["force"])
			self.write()

		def cmd_list():
			transactionfilter = self.create_and_date_transactionfilter(self.arguments_dict["year"], self.arguments_dict["month"], self.arguments_dict["day"])
			summarycategory = None

			if self.arguments_dict["category"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.create_or_category_transactionfilter(self.arguments_dict["category"], self.arguments_dict["category"])
					)
					summarycategory = self.moneydata.get_category(self.arguments_dict["category"])
				except lib.data.moneydata.NoSuchCategoryException as e:
					print("category not found: " + e.name, file=sys.stderr)
					return

			if self.arguments_dict["fromcategory"] or self.arguments_dict["tocategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.create_and_category_transactionfilter(self.arguments_dict["fromcategory"], self.arguments_dict["tocategory"])
					)

					if self.arguments_dict["fromcategory"]:
						summarycategory = self.moneydata.get_category(self.arguments_dict["fromcategory"])
					if self.arguments_dict["tocategory"]:
						summarycategory = self.moneydata.get_category(self.arguments_dict["tocategory"])
				except lib.data.moneydata.NoSuchCategoryException as e:
					print("category not found: " + e.name, file=sys.stderr)
					return

			print("{0:>10} {1:<10} {2:<20} {3:<40} {4:>10} {5:<20}".format("Index", "Date", "FromCategory", "ToCategory", "Amount", "Comment"))

			fromcategory_name_formatter = lib.app.CategoryNameFormatter()
			tocategory_name_formatter = lib.app.CategoryNameFormatter()
			if self.arguments_dict["fullnamecategories"]:
				fromcategory_name_formatter.set_strategy(lib.app.CategoryNameFormatter.STRATEGY_FULL_NAME)
				tocategory_name_formatter.set_strategy(lib.app.CategoryNameFormatter.STRATEGY_FULL_NAME)

			fromcategory_name_formatter.set_maxlength(20)
			tocategory_name_formatter.set_maxlength(40)

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

				print("{0:>10} {1:>10} {2:<20} {3:<40} {4:>10.2f} {5:<20}".format(_index, _date, _fromcategory, _tocategory, _amount, _comment))

			d_summary = self.moneydata.create_summary(transactionfilter)

			if summarycategory:
				_summarycategory = tocategory_name_formatter.format(summarycategory)
				key = summarycategory.get_unique_name()

				print("")
				print("{0:>10} {1:>10} {2:<20} {3:<40} {4:>10.2f} {5:<20}".format("", "", "", "+ " + _summarycategory, d_summary[key].sumin, ""))
				print("{0:>10} {1:>10} {2:<20} {3:<40} {4:>10.2f} {5:<20}".format("", "", "", "- " + _summarycategory, d_summary[key].sumout, ""))
				print("{0:>10} {1:>10} {2:<20} {3:<40} {4:>10.2f} {5:<20}".format("", "", "", "sum " + _summarycategory, d_summary[key].sum, ""))

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
			category_name_formatter = lib.app.CategoryNameFormatter()
			category_name_formatter.set_strategy(lib.app.CategoryNameFormatter.STRATEGY_NAME)
			category_name_formatter.set_indent_with_tree_level(True)

			if self.arguments_dict["fullnamecategories"]:
				category_name_formatter.set_strategy(lib.app.CategoryNameFormatter.STRATEGY_FULL_NAME)
				category_name_formatter.set_indent_with_tree_level(False)

			for c in self.moneydata.categorytree:
				print(category_name_formatter.format(c))

		def cmd_list():
			category_name_formatter = lib.app.CategoryNameFormatter()
			if self.arguments_dict["fullnamecategories"]:
				category_name_formatter.set_strategy(lib.app.CategoryNameFormatter.STRATEGY_FULL_NAME)

			for category in self.moneydata.categorytree:
				_category = category_name_formatter.format(category)
				print(_category)
			print("")

		def cmd_add():
			self.moneydata.add_category(self.arguments_dict["parentname"], self.arguments_dict["name"])
			self.write()

		def cmd_delete():
			self.moneydata.delete_category(self.arguments_dict["name"])
			self.write()

		def cmd_move():
			self.moneydata.move_category(self.arguments_dict["name"], self.arguments_dict["newparentname"])
			self.write()

		def cmd_rename():
			self.moneydata.rename_category(self.arguments_dict["name"], self.arguments_dict["newname"])
			self.write()

		def cmd_merge():
			self.moneydata.merge_category(self.arguments_dict["name"], self.arguments_dict["targetname"])
			self.write()

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
			transactionfilter = self.create_and_date_transactionfilter(self.arguments_dict["year"], self.arguments_dict["month"], self.arguments_dict["day"])

			if self.arguments_dict["cashflowcategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.create_or_category_transactionfilter(self.arguments_dict["cashflowcategory"], self.arguments_dict["cashflowcategory"])
					)
				except lib.data.moneydata.NoSuchCategoryException as e:
					print("category not found: " + e.name, file=sys.stderr)
					return

			categoryfilter = lib.data.filter.Filter(lambda c: True)
			if self.arguments_dict["maxlevel"]:
				categoryfilter = categoryfilter.and_concat(self.create_maxlevel_category_transactionfilter(self.arguments_dict["maxlevel"]))

			if self.arguments_dict["category"]:
				categoryfilter = categoryfilter.and_concat(self.create_subtree_category_transactionfilter(self.arguments_dict["category"]))

			d_summary = self.moneydata.create_summary(transactionfilter)
			category_name_formatter = lib.app.CategoryNameFormatter()
			category_name_formatter.set_strategy(lib.app.CategoryNameFormatter.STRATEGY_NAME)
			category_name_formatter.set_maxlength(55)
			category_name_formatter.set_indent_with_tree_level(True)

			print("{0:<55} {1:>10} {2:>10} {3:>10} {4:>10}".format("node", "amount", "sum +", "sum -", "sum"))
			print()
			for category in lib.data.filter.FilterIterator(self.moneydata.categorytree.__iter__(), categoryfilter):
				key = category.get_unique_name()
				name = category_name_formatter.format(category)
				if not self.arguments_dict["showempty"] and d_summary[key].sumcount == 0:
					continue
				print("{0:<55} {1:>10.2f} {2:>10.2f} {3:>10.2f} {4:>10.2f}".format(name,
																d_summary[key].amount, d_summary[key].sumin, d_summary[key].sumout, d_summary[key].sum))

		def sub_time_interval_summary(category, start_year, start_month, diff_months, maxdate):
			assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

			category_name_formatter = lib.app.CategoryNameFormatter()

			year = start_year
			month = start_month

			category_name_formatter.set_maxlength(55)
			print("{0:<10} {1:<55} {2:>10} {3:>10} {4:>10} {5:>10}".format("date", "node", "amount", "sum +", "sum -", "sum"))
			print()

			key = category.get_unique_name()
			name = category_name_formatter.format(category)
			while datetime.date(year, month, 1) <= maxdate:
				if diff_months == 1:
					transactionfilter = self.create_and_date_transactionfilter(str(year), str(month), None)
				elif diff_months == 12:
					transactionfilter = self.create_and_date_transactionfilter(str(year), None, None)
				else:
					raise Exception("diff_months value not supported: " + str(diff_months))
				d_summary = self.moneydata.create_summary(transactionfilter)

				print("{0:<10} {1:<55} {2:>10.2f} {3:>10.2f} {4:>10.2f} {5:>10.2f}".format(str(datetime.date(year, month, 1)), name,
																	 d_summary[key].amount,
																	 d_summary[key].sumin,
																	 d_summary[key].sumout,
																	 d_summary[key].sum))

				month += diff_months

				if month > 12:
					year += int(month / 12)
					month %= 12

		def cmd_monthly():
			mindate = None
			maxdate = None
			for transaction in self.moneydata.transactions:
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			category = self.moneydata.get_category(self.arguments_dict["category"])

			if not category:
				print("no such category: " + self.arguments_dict["category"], file=sys.stderr)
				return

			sub_time_interval_summary(category, mindate.year, mindate.month, 1, maxdate)

		def cmd_yearly():
			mindate = None
			maxdate = None
			for transaction in self.moneydata.transactions:
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			category = self.moneydata.get_category(self.arguments_dict["category"])

			if not category:
				print("no such category: " + self.arguments_dict["category"], file=sys.stderr)
				return

			sub_time_interval_summary(category, mindate.year, 1, 12, maxdate)

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
		p_summary_monthly.add_argument("category")

		p_summary_yearly = sp_summary.add_parser("yearly")
		p_summary_yearly.set_defaults(command="yearly")
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
