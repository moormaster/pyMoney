#!/usr/bin/python3

import pymoney.app
import pymoney.data
import pymoney.io

import argparse
import datetime
import sys

def not_implemented(*pargs, **args):
	print("not implemented", file=sys.stderr)
	
transaction=category=summary=not_implemented

def init(**args):
	global app
	app = pymoney.app.PyMoney(args["fileprefix"])

def transaction(**args):
	def cmd_add(**args):
		app.add_transaction(args["date"], args["category"], args["amount"], args["comment"])
		app.write_transactions()
	
	def cmd_list(**args):
		filter = pymoney.data.Filter(lambda t: True)
		filter_year = filter_month = filter_category = None
		
		if args["year"]:
			filter_year = int(args["year"])
			filter = filter.andConcat(lambda t: t.date.year == filter_year)
			
		if args["month"]:
			filter_month = int(args["month"])
			filter = filter.andConcat(lambda t: t.date.month == filter_month)
			
		if args["category"]:
			filter_category = app.categorytree.findNode(args["category"])
			
			if not filter_category:
				print("category not found: " + args["category"], file=sys.stderr)
				return
				
			filter = filter.andConcat(lambda t: t.category == filter_category or t.category.isChildOf(filter_category))


		print("{0:>10} {1:<10} {2:<20} {3:>10} {4:<20}".format("Index", "Date", "Category", "Amount", "Comment"))
		
		iterator = app.filter_transactions(filter)
		for d in iterator:
			_index = iterator.index
			_date = str(d.date)
			
			if args["fullnamecategories"]:
				_category = d.category.getFullName()
			else:
				_category = d.category.name
			
			_amount = d.amount
			_comment = d.comment
			
			print("{0:>10} {1:>10} {2:<20} {3:>10.2f} {4:<20}".format(_index, _date, _category, _amount, _comment))
			
	def cmd_delete(**args):
		app.delete_transaction(args["index"])
		app.write_transactions()
		
	d_commands = {
		"add" : 	cmd_add,
		"delete" :	cmd_delete,
		"list" :	cmd_list
	}
	
	d_commands[args["command"]](**args)
			
def category(**args):
	def cmd_list(**args):
		print(app.categorytree)

	def cmd_add(**args):
		app.add_category(args["parentname"], args["name"])
		app.write_categories()

	def cmd_delete(**args):
		app.delete_category(args["name"])
		app.write_categories()

	def cmd_move(**args):
		app.move_category(args["name"], args["newparentname"])
		app.write_categories()
		
	def cmd_rename_merge(**args):
		if args["merge"]:
			app.merge_category(args["name"], args["targetname"])
		else:
			app.rename_category(args["name"], args["newname"])
			
		app.write_categories()
		app.write_transactions()
		
	def cmd_rename(**args):
		_args = args.copy()
		_args["merge"] = False
		return cmd_rename_merge(**_args)
		
	def cmd_merge(**args):
		_args = args.copy()
		_args["merge"] = True
		return cmd_rename_merge(**_args)
			
	
	d_commands = {
		"add" :		cmd_add,
		"delete" :	cmd_delete,
		"move" :	cmd_move,
		"rename" :	cmd_rename,
		"merge" :	cmd_merge,
		"list" :	cmd_list
	}
	
	d_commands[args["command"]](**args)
	
def summary(**args):
	def cmd_categories(**args):
		filter = pymoney.data.Filter(lambda t: True)
		
		if args["year"] != None:
			filter = filter.andConcat(lambda t: t.date.year == int(args["year"]))
	
		if args["month"] != None:
			filter = filter.andConcat(lambda t: t.date.month == int(args["month"]))
	
		d_summary = app.create_summary(filter)
			
		
		print("{0:<30} {1:>10} {2:>10}".format("node", "amount", "sum"))
		print()
		for c in app.categorytree:
			if len(c.children):
				nodesym = "+"
			else:
				nodesym = "-"
			
			print("{0:<30} {1:>10.2f} {2:>10.2f}".format("    "*c.getDepth() + " " + nodesym + " " + c.name, d_summary[c.name].amount, d_summary[c.name].sum))
			
	def cmd_monthly(**args):
		mindate = None
		maxdate = None
		for t in app.transactions:
			if not mindate or t.date < mindate:
				mindate = t.date
				
			if not maxdate or t.date > maxdate:
				maxdate = t.date
	
		category = app.categorytree.findNode(args["category"])
		
		if not category:
			print("no such category: " + args["category"], file=sys.stderr)
			return
		
		year = mindate.year
		month = mindate.month
	
		print("{0:<10} {1:<30} {2:>10} {3:>10}".format("date", "node", "amount", "sum"))
		print()
	
		while datetime.date(year, month, 1) <= maxdate:
			filter = pymoney.data.Filter(lambda t: t.date.year == year and t.date.month == month)
			d_summary = app.create_summary(filter)
			
		
			print("{0:<10} {1:<30} {2:>10.2f} {3:>10.2f}".format(str(datetime.date(year, month, 1)), category.name, d_summary[args["category"]].amount, d_summary[args["category"]].sum))
			
			month = month + 1
			
			if month > 12:
				month = 1
				year = year + 1
			
		
	d_commands = {
		"categories" :	cmd_categories,
		"monthly" : cmd_monthly
	}
	
	d_commands[args["command"]](**args)
	
		

def main(argv):
	p_main = argparse.ArgumentParser()
	p_main.add_argument("--fileprefix", default="pymoney");
	
	sp_main = p_main.add_subparsers(title="object")

	### transactions
	p_transaction = sp_main.add_parser("transaction")
	p_transaction.add_argument("--fullnamecategories", action="store_true")
	p_transaction.set_defaults(func=transaction)

	sp_transaction = p_transaction.add_subparsers(title="command")
	
	p_transaction_add = sp_transaction.add_parser("add")
	p_transaction_add.set_defaults(command="add")
	p_transaction_add.add_argument("date")
	p_transaction_add.add_argument("category")
	p_transaction_add.add_argument("amount")
	p_transaction_add.add_argument("comment", default="", nargs='?')
	
	p_transaction_delete = sp_transaction.add_parser("delete")
	p_transaction_delete.set_defaults(command="delete")
	p_transaction_delete.add_argument("index", type=int)
	
	p_transaction_list = sp_transaction.add_parser("list")
	p_transaction_list.add_argument("year", type=int, nargs='?');
	p_transaction_list.add_argument("month", type=int, nargs='?');
	p_transaction_list.add_argument("--category");
	p_transaction_list.set_defaults(command="list")
	
	### categories
	p_category = sp_main.add_parser("category")
	p_category.add_argument("--fullnamecategories", action="store_true")
	p_category.set_defaults(func=category)
	
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
	p_summary.set_defaults(func=summary)
	
	sp_summary = p_summary.add_subparsers(title="command")
	
	p_summary_categories = sp_summary.add_parser("categories")
	p_summary_categories.set_defaults(command="categories")
	p_summary_categories.add_argument("year", type=int, nargs='?');
	p_summary_categories.add_argument("month", type=int, nargs='?')
	
	p_summary_monthly = sp_summary.add_parser("monthly")
	p_summary_monthly.set_defaults(command="monthly")
	p_summary_monthly.add_argument("category")


	arguments = p_main.parse_args(argv)
	# print(arguments.__dict__)
	
	init(**arguments.__dict__)
	arguments.func(**arguments.__dict__)

	
main(sys.argv[1:])
