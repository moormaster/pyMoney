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

	def cmdgroup_transaction(self, parser):
		def cmd_add():
			self.moneydata.add_transaction(	self.arguments_dict["date"], self.arguments_dict["category"], self.arguments_dict["amount"],
													self.arguments_dict["comment"], self.arguments_dict["force"])
			self.write()

		def cmd_list():
			transactionfilter = lib.data.Filter(lambda t: True)
			filter_year = filter_month = filter_category = None

			if self.arguments_dict["year"]:
				filter_year = int(self.arguments_dict["year"])
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year == filter_year)

			if self.arguments_dict["month"]:
				filter_month = int(self.arguments_dict["month"])
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.month == filter_month)

			if self.arguments_dict["category"]:
				filter_category = self.moneydata.get_category(self.arguments_dict["category"])

				if not filter_category:
					print("category not found: " + self.arguments_dict["category"], file=sys.stderr)
					return

				transactionfilter = transactionfilter.and_concat(
					lambda t: t.category == filter_category or t.category.is_contained_in_subtree(filter_category))

			print("{0:>10} {1:<10} {2:<20} {3:>10} {4:<20}".format("Index", "Date", "Category", "Amount", "Comment"))

			iterator = self.moneydata.filter_transactions(transactionfilter)
			for d in iterator:
				_index = iterator.index
				_date = str(d.date)

				if self.arguments_dict["fullnamecategories"]:
					_category = d.category.get_full_name()
				else:
					_category = d.category.name

				_amount = d.amount
				_comment = d.comment

				print("{0:>10} {1:>10} {2:<20} {3:>10.2f} {4:<20}".format(_index, _date, _category, _amount, _comment))

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
		def cmd_list():
			print(self.moneydata.categorytree.__str__(fullname=self.arguments_dict["fullnamecategories"]))

		def cmd_listnames():
			for category in self.moneydata.categorytree:
				if self.arguments_dict["fullnamecategories"]:
					_category = category.get_full_name()
				else:
					_category = category.name

				print(_category + " ", end="")
			print("")

		def cmd_add():
			self.moneydata.add_category(self.arguments_dict["parentname"], self.arguments_dict["name"])
			self.write(skipwritetransactions=True)

		def cmd_delete():
			self.moneydata.delete_category(self.arguments_dict["name"])
			self.write(skipwritetransactions=True)

		def cmd_move():
			self.moneydata.move_category(self.arguments_dict["name"], self.arguments_dict["newparentname"])
			self.write(skipwritetransactions=True)

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
			"listnames": cmd_listnames
		}

		if not "command" in self.arguments_dict:
			parser.print_help()
		else:
			d_commands[self.arguments_dict["command"]]()

	def cmdgroup_summary(self, parser):
		def cmd_categories():
			transactionfilter = lib.data.Filter(lambda t: True)

			if self.arguments_dict["year"] is not None:
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.year == int(self.arguments_dict["year"]))

			if self.arguments_dict["month"] is not None:
				transactionfilter = transactionfilter.and_concat(lambda t: t.date.month == int(self.arguments_dict["month"]))

			d_summary = self.moneydata.create_summary(transactionfilter)

			print("{0:<40} {1:>10} {2:>10}".format("node", "amount", "sum"))
			print()
			for c in self.moneydata.categorytree:
				if len(c.children):
					nodesym = "+"
				else:
					nodesym = "-"

				print("{0:<40} {1:>10.2f} {2:>10.2f}".format("    " * c.get_depth() + " " + nodesym + " " + c.name,
																d_summary[c.name].amount, d_summary[c.name].sum))

		def cmd_monthly():
			mindate = None
			maxdate = None
			for transaction in self.moneydata.transactions:
				if not mindate or transaction.date < mindate:
					mindate = transaction.date

				if not maxdate or transaction.date > maxdate:
					maxdate = transaction.date

			category = self.moneydata.categorytree.find_first_node(self.arguments_dict["category"])

			if not category:
				print("no such category: " + self.arguments_dict["category"], file=sys.stderr)
				return

			year = mindate.year
			month = mindate.month

			print("{0:<10} {1:<40} {2:>10} {3:>10}".format("date", "node", "amount", "sum"))
			print()

			while datetime.date(year, month, 1) <= maxdate:
				transactionfilter = lib.data.Filter(lambda t: t.date.year == year and t.date.month == month)
				d_summary = self.moneydata.create_summary(transactionfilter)

				print("{0:<10} {1:<40} {2:>10.2f} {3:>10.2f}".format(str(datetime.date(year, month, 1)), category.name,
																	d_summary[self.arguments_dict["category"]].amount,
																	d_summary[self.arguments_dict["category"]].sum))

				month += 1

				if month > 12:
					month = 1
					year += 1

		d_commands = {
			"categories": cmd_categories,
			"monthly": cmd_monthly
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
		p_transaction_add.add_argument("category")
		p_transaction_add.add_argument("amount", type=float)
		p_transaction_add.add_argument("comment", default="", nargs='?')
		p_transaction_add.add_argument("--force", action="store_true")

		p_transaction_delete = sp_transaction.add_parser("delete")
		p_transaction_delete.set_defaults(command="delete")
		p_transaction_delete.add_argument("index", type=int)

		p_transaction_list = sp_transaction.add_parser("list")
		p_transaction_list.set_defaults(command="list")
		p_transaction_list.add_argument("year", type=int, nargs='?')
		p_transaction_list.add_argument("month", type=int, nargs='?')
		p_transaction_list.add_argument("--category")

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

		p_category_list = sp_category.add_parser("list")
		p_category_list.set_defaults(command="list")

		p_category_listnames = sp_category.add_parser("listnames")
		p_category_listnames.set_defaults(command="listnames")

		### summary
		p_summary = sp_main.add_parser("summary")
		p_summary.set_defaults(func=self.cmdgroup_summary)
		p_summary.set_defaults(parser=p_summary)
		sp_summary = p_summary.add_subparsers(title="command")

		p_summary_categories = sp_summary.add_parser("categories")
		p_summary_categories.set_defaults(command="categories")
		p_summary_categories.add_argument("year", type=int, nargs='?')
		p_summary_categories.add_argument("month", type=int, nargs='?')

		p_summary_monthly = sp_summary.add_parser("monthly")
		p_summary_monthly.set_defaults(command="monthly")
		p_summary_monthly.add_argument("category")

		return p_main

	def main(self):
		try:
			self.arguments.func(self.arguments.parser)
		except AttributeError:
			self.argumentparser.print_help()


if __name__ == "__main__":
	pymoneyconsole = PyMoneyConsole(sys.argv[1:])
	pymoneyconsole.main()
