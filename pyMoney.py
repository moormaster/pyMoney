#!/usr/bin/python3

import lib.app
import lib.data
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

	def createAndDateTransactionFilter(self, filter_year, filter_month, filter_day):
		transactionfilter = lib.data.Filter(lambda t: True)

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


	def createOrCategoryTransactionFilter(self, filter_from_category, filter_to_category):
		transactionfilter = lib.data.Filter(lambda t: False)

		if filter_from_category:
			fromcategory = self.moneydata.get_category(filter_from_category)

			if not fromcategory:
				raise lib.data.NoSuchCategoryException(filter_from_category)

			transactionfilter = transactionfilter.or_concat(
				lambda t: t.fromcategory == fromcategory or t.fromcategory.is_contained_in_subtree(fromcategory)
			)

		if filter_to_category:
			tocategory = self.moneydata.get_category(filter_to_category)

			if not tocategory:
				raise lib.data.NoSuchCategoryException(filter_to_category)

			transactionfilter = transactionfilter.or_concat(
				lambda t: t.tocategory == tocategory or t.tocategory.is_contained_in_subtree(tocategory)
			)

		return transactionfilter


	def createAndCategoryTransactionFilter(self, filter_from_category, filter_to_category):
		transactionfilter = lib.data.Filter(lambda t: True)

		if filter_from_category:
			fromcategory = self.moneydata.get_category(filter_from_category)

			if not fromcategory:
				raise lib.data.NoSuchCategoryException(filter_from_category)

			transactionfilter = transactionfilter.and_concat(
				lambda t: t.fromcategory == fromcategory or t.fromcategory.is_contained_in_subtree(fromcategory)
			)

		if filter_to_category:
			tocategory = self.moneydata.get_category(filter_to_category)

			if not tocategory:
				raise lib.data.NoSuchCategoryException(filter_to_category)

			transactionfilter = transactionfilter.and_concat(
				lambda t: t.tocategory == tocategory or t.tocategory.is_contained_in_subtree(tocategory)
			)

		return transactionfilter


	def cmdgroup_transaction(self, parser):
		def cmd_add():
			self.moneydata.add_transaction(	self.arguments_dict["date"], self.arguments_dict["fromcategory"], self.arguments_dict["tocategory"], self.arguments_dict["amount"],
													self.arguments_dict["comment"], self.arguments_dict["force"])
			self.write()

		def cmd_list():
			filter_year = filter_month = filter_category = None

			transactionfilter = self.createAndDateTransactionFilter(self.arguments_dict["year"], self.arguments_dict["month"], self.arguments_dict["day"])

			if self.arguments_dict["category"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.createOrCategoryTransactionFilter(self.arguments_dict["category"], self.arguments_dict["category"])
					)
				except lib.data.NoSuchCategoryException as e:
					print("category not found: " + e.name, file=sys.stderr)
					return

			if self.arguments_dict["fromcategory"] or self.arguments_dict["tocategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.createAndCategoryTransactionFilter(self.arguments_dict["fromcategory"], self.arguments_dict["tocategory"])
					)
				except lib.data.NoSuchCategoryException as e:
					print("category not found: " + e.name, file=sys.stderr)
					return

			print("{0:>10} {1:<10} {2:<20} {3:<40} {4:>10} {5:<20}".format("Index", "Date", "FromCategory", "ToCategory", "Amount", "Comment"))

			d_name = {}
			iterator = self.moneydata.filter_transactions(transactionfilter)
			for d in iterator:
				_index = iterator.index
				_date = str(d.date)

				if self.arguments_dict["fullnamecategories"]:
					if not id(d.fromcategory) in d_name:
						d_name[id(d.fromcategory)] = d.fromcategory.get_full_name()
					if not id(d.tocategory) in d_name:
						d_name[id(d.tocategory)] = d.tocategory.get_full_name()

					_fromcategory = d_name[id(d.fromcategory)]
					_tocategory = d_name[id(d.tocategory)]
				else:
					if not id(d.fromcategory) in d_name:
						d_name[id(d.fromcategory)] = d.fromcategory.get_unique_name()
					if not id(d.tocategory) in d_name:
						d_name[id(d.tocategory)] = d.tocategory.get_unique_name()

					_fromcategory = d_name[id(d.fromcategory)]
					_tocategory = d_name[id(d.tocategory)]

				assert isinstance(d.fromcategory, lib.data.CategoryTreeNode)
				assert isinstance(d.tocategory, lib.data.CategoryTreeNode)
				_amount = d.amount
				_comment = d.comment

				print("{0:>10} {1:>10} {2:<20} {3:<40} {4:>10.2f} {5:<20}".format(_index, _date, _fromcategory, _tocategory, _amount, _comment))

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
			print(self.moneydata.categorytree.__str__(fullname=self.arguments_dict["fullnamecategories"]))

		def cmd_list():
			for category in self.moneydata.categorytree:
				if self.arguments_dict["fullnamecategories"]:
					_category = category.get_full_name()
				else:
					_category = category.get_unique_name()

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
			transactionfilter = self.createAndDateTransactionFilter(self.arguments_dict["year"], self.arguments_dict["month"], self.arguments_dict["day"])

			if self.arguments_dict["cashflowcategory"]:
				try:
					transactionfilter = transactionfilter.and_concat(
						self.createOrCategoryTransactionFilter(self.arguments_dict["cashflowcategory"], self.arguments_dict["cashflowcategory"])
					)
				except lib.data.NoSuchCategoryException as e:
					print("category not found: " + e.name, file=sys.stderr)
					return

			d_summary = self.moneydata.create_summary(transactionfilter)

			print("{0:<55} {1:>10} {2:>10}".format("node", "amount", "sum"))
			print()
			for c in self.moneydata.categorytree:
				key = c.get_unique_name()
				if self.arguments_dict["maxlevel"] and c.get_depth() > self.arguments_dict["maxlevel"]:
					continue
				if not self.arguments_dict["showempty"] and d_summary[key].sumcount == 0:
					continue
				print("{0:<55} {1:>10.2f} {2:>10.2f}".format(c.format(),
																d_summary[key].amount, d_summary[key].sum))

		def sub_time_interval_summary(category, start_year, start_month, diff_months, maxdate):
			year = start_year
			month = start_month

			print("{0:<10} {1:<55} {2:>10} {3:>10}".format("date", "node", "amount", "sum"))
			print()

			while datetime.date(year, month, 1) <= maxdate:
				if diff_months == 1:
					transactionfilter = self.createAndDateTransactionFilter(str(year), str(month), None)
				elif diff_months == 12:
					transactionfilter = self.createAndDateTransactionFilter(str(year), None, None)
				else:
					raise Exception("diff_months value not supported: " + str(diff_months))
				d_summary = self.moneydata.create_summary(transactionfilter)

				key = category.get_unique_name()
				print("{0:<10} {1:<55} {2:>10.2f} {3:>10.2f}".format(str(datetime.date(year, month, 1)), key,
																	 d_summary[key].amount,
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
