#!/usr/bin/python3

import lib.app
import lib.data
import lib.io

import argparse
import datetime
import sys


def init(**arguments):
	global app_instance
	app_instance = lib.app.PyMoney(arguments["fileprefix"])

	app_instance.read()


def cmdgroup_transaction(**cmdgroup_arguments):
	def cmd_add(**arguments):
		app_instance.moneydata.add_transaction(	arguments["date"], arguments["category"], arguments["amount"],
												arguments["comment"], arguments["force"])
		app_instance.write()

	def cmd_list(**arguments):
		transactionfilter = lib.data.Filter(lambda t: True)
		filter_year = filter_month = filter_category = None

		if arguments["year"]:
			filter_year = int(arguments["year"])
			transactionfilter = transactionfilter.and_concat(lambda t: t.date.year == filter_year)

		if arguments["month"]:
			filter_month = int(arguments["month"])
			transactionfilter = transactionfilter.and_concat(lambda t: t.date.month == filter_month)

		if arguments["category"]:
			filter_category = app_instance.moneydata.get_category(arguments["category"])

			if not filter_category:
				print("category not found: " + arguments["category"], file=sys.stderr)
				return

			transactionfilter = transactionfilter.and_concat(
				lambda t: t.category == filter_category or t.category.is_contained_in_subtree(filter_category))

		print("{0:>10} {1:<10} {2:<20} {3:>10} {4:<20}".format("Index", "Date", "Category", "Amount", "Comment"))

		iterator = app_instance.moneydata.filter_transactions(transactionfilter)
		for d in iterator:
			_index = iterator.index
			_date = str(d.date)

			if arguments["fullnamecategories"]:
				_category = d.category.get_full_name()
			else:
				_category = d.category.name

			_amount = d.amount
			_comment = d.comment

			print("{0:>10} {1:>10} {2:<20} {3:>10.2f} {4:<20}".format(_index, _date, _category, _amount, _comment))

	def cmd_delete(**arguments):
		app_instance.moneydata.delete_transaction(arguments["index"])
		app_instance.write()

	d_commands = {
		"add": cmd_add,
		"delete": cmd_delete,
		"list": cmd_list
	}

	d_commands[cmdgroup_arguments["command"]](**cmdgroup_arguments)


def cmdgroup_category(**cmdgroup_arguments):
	def cmd_list(**arguments):
		print(app_instance.moneydata.categorytree)

	def cmd_add(**arguments):
		app_instance.moneydata.add_category(arguments["parentname"], arguments["name"])
		app_instance.write(skipwritetransactions=True)

	def cmd_delete(**arguments):
		app_instance.moneydata.delete_category(arguments["name"])
		app_instance.write(skipwritetransactions=True)

	def cmd_move(**arguments):
		app_instance.moneydata.move_category(arguments["name"], arguments["newparentname"])
		app_instance.write(skipwritetransactions=True)

	def cmd_rename_merge(**arguments):
		if arguments["merge"]:
			app_instance.moneydata.merge_category(arguments["name"], arguments["targetname"])
		else:
			app_instance.moneydata.rename_category(arguments["name"], arguments["newname"])

		app_instance.write()

	def cmd_rename(**arguments):
		_args = arguments.copy()
		_args["merge"] = False
		return cmd_rename_merge(**_args)

	def cmd_merge(**arguments):
		_args = arguments.copy()
		_args["merge"] = True
		return cmd_rename_merge(**_args)

	d_commands = {
		"add": cmd_add,
		"delete": cmd_delete,
		"move": cmd_move,
		"rename": cmd_rename,
		"merge": cmd_merge,
		"list": cmd_list
	}

	d_commands[cmdgroup_arguments["command"]](**cmdgroup_arguments)


def cmdgroup_summary(**cmdgroup_arguments):
	def cmd_categories(**arguments):
		transactionfilter = lib.data.Filter(lambda t: True)

		if arguments["year"] is not None:
			transactionfilter = transactionfilter.and_concat(lambda t: t.date.year == int(arguments["year"]))

		if arguments["month"] is not None:
			transactionfilter = transactionfilter.and_concat(lambda t: t.date.month == int(arguments["month"]))

		d_summary = app_instance.moneydata.create_summary(transactionfilter)

		print("{0:<30} {1:>10} {2:>10}".format("node", "amount", "sum"))
		print()
		for c in app_instance.moneydata.categorytree:
			if len(c.children):
				nodesym = "+"
			else:
				nodesym = "-"

			print("{0:<30} {1:>10.2f} {2:>10.2f}".format("    " * c.get_depth() + " " + nodesym + " " + c.name,
															d_summary[c.name].amount, d_summary[c.name].sum))

	def cmd_monthly(**arguments):
		mindate = None
		maxdate = None
		for transaction in app_instance.moneydata.transactions:
			if not mindate or transaction.date < mindate:
				mindate = transaction.date

			if not maxdate or transaction.date > maxdate:
				maxdate = transaction.date

		category = app_instance.moneydata.categorytree.find_first_node(arguments["category"])

		if not category:
			print("no such category: " + arguments["category"], file=sys.stderr)
			return

		year = mindate.year
		month = mindate.month

		print("{0:<10} {1:<30} {2:>10} {3:>10}".format("date", "node", "amount", "sum"))
		print()

		while datetime.date(year, month, 1) <= maxdate:
			transactionfilter = lib.data.Filter(lambda t: t.date.year == year and t.date.month == month)
			d_summary = app_instance.moneydata.create_summary(transactionfilter)

			print("{0:<10} {1:<30} {2:>10.2f} {3:>10.2f}".format(str(datetime.date(year, month, 1)), category.name,
																d_summary[arguments["category"]].amount,
																d_summary[arguments["category"]].sum))

			month += 1

			if month > 12:
				month = 1
				year += 1

	d_commands = {
		"categories": cmd_categories,
		"monthly": cmd_monthly
	}

	d_commands[cmdgroup_arguments["command"]](**cmdgroup_arguments)


def get_argument_parser():
	p_main = argparse.ArgumentParser()
	p_main.add_argument("--fileprefix", default="pymoney")
	sp_main = p_main.add_subparsers(title="object")

	### transactions
	p_transaction = sp_main.add_parser("transaction")
	p_transaction.set_defaults(func=cmdgroup_transaction)
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
	p_category.set_defaults(func=cmdgroup_category)
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

	### summary
	p_summary = sp_main.add_parser("summary")
	p_summary.set_defaults(func=cmdgroup_summary)
	sp_summary = p_summary.add_subparsers(title="command")

	p_summary_categories = sp_summary.add_parser("categories")
	p_summary_categories.set_defaults(command="categories")
	p_summary_categories.add_argument("year", type=int, nargs='?')
	p_summary_categories.add_argument("month", type=int, nargs='?')

	p_summary_monthly = sp_summary.add_parser("monthly")
	p_summary_monthly.set_defaults(command="monthly")
	p_summary_monthly.add_argument("category")

	return p_main


def main(argv):
	p_main = get_argument_parser()
	arguments = p_main.parse_args(argv)

	init(**arguments.__dict__)
	arguments.func(**arguments.__dict__)


if __name__ == "__main__":
	main(sys.argv[1:])
