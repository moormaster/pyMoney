import pymoney.data
import pymoney.io

import argparse
import datetime
import sys

def not_implemented(*pargs, **args):
	print("not implemented", file=sys.stderr)
	
transaction=category=summary=not_implemented

def init(**args):
	global categorytree, transactions
	global notfoundcategory, transactionfactory
	global t_filename, c_filename, p_filename

	t_filename = args["fileprefix"] + ".transactions"
	c_filename = args["fileprefix"] + ".categories"
	
	try:
		categorytree = pymoney.io.read_categories(c_filename)
	except Exception as e:
		print("failed to read categorytree from " + c_filename + ":\n" + str(e), file=sys.stderr)
		categorytree = pymoney.data.TreeNode("All")
	
	notfoundcategory = categorytree.findNode("NOTFOUND")
	if not notfoundcategory:
		notfoundcategory = categorytree.appendChildNode(pymoney.data.TreeNode("NOTFOUND"))
	
	transactionfactory=pymoney.data.TransactionFactory(categorytree, notfoundcategory)
	
	try:
		transactions = pymoney.io.read_transactions(t_filename, transactionfactory)
	except Exception as e:
		print("failed to read transactions from " + t_filename + ":\n" + str(e), file=sys.stderr)
		transactions = []


def transaction(**args):
	def cmd_add(**args):
		pymoney.io.write_transactions(t_filename, transactionfactory, [transactionfactory.create(args["date"], args["category"], args["amount"], args["comment"])], append=True)
	
	def cmd_list(**args):	
		filter_year = filter_month = filter_category = None
		
		if args["year"]:
			filter_year = int(args["year"])
			
		if args["month"]:
			filter_month = int(args["month"])
			
		if args["category"]:
			filter_category = categorytree.findNode(args["category"])
			
			if not filter_category:
				print("category not found: " + args["category"], file=sys.stderr)
				return


		print("{0:>10} {1:<10} {2:<20} {3:>10} {4:<20}".format("Index", "Date", "Category", "Amount", "Comment"))
				
		for i in range(0, len(transactions)):
			d = transactions[i]				
			
			if filter_year != None and d.date.year != filter_year:
				continue
				
			if filter_month != None and d.date.month != filter_month:
				continue
				
			if filter_category and d.category != filter_category and not d.category.isChildOf(filter_category):
				continue
			
			_index = i
			_date = str(d.date)
			
			if args["fullnamecategories"]:
				_category = d.category.getFullName()
			else:
				_category = d.category.name
			
			_amount = d.amount
			_comment = d.comment
			
			print("{0:>10} {1:>10} {2:<20} {3:>10.2f} {4:<20}".format(_index, _date, _category, _amount, _comment))
			
	def cmd_delete(**args):
		if args["index"] >= 0 and args["index"] < len(transactions):
			del transactions[args["index"]]
			
		pymoney.io.write_transactions(t_filename, transactionfactory, transactions)
		
	d_commands = {
		"add" : 	cmd_add,
		"delete" :	cmd_delete,
		"list" :	cmd_list
	}
	
	d_commands[args["command"]](**args)
			
def category(**args):
	def cmd_list(**args):
		print(categorytree)

	def cmd_add(**args):
		node = categorytree.findNode(args["name"])
		parentnode = categorytree.findNode(args["parentname"])
		
		if node and not node.isChildOf(notfoundcategory):
			print("node already exists: " + args["name"], file=sys.stderr)
			return

		if not parentnode:
			print("no such node: " + args["parentname"], file=sys.stderr)
			return
			
		if node and node.isChildOf(notfoundcategory):
			node.parent.removeChildNode(args["name"])
		
		parentnode.appendChildNode(pymoney.data.TreeNode(args["name"]))

		pymoney.io.write_categories(c_filename, categorytree, notfoundcategory)

	def cmd_delete(**args):
		node = categorytree.findNode(args["name"])
		
		if not node:
			print("no such node: " + args["name"], file=sys.stderr)
			return

		if not node.parent:
			print("cannot remove topnode: " + args["name"], file=sys.stderr)
			return

		node.parent.removeChildNode(node.name)
		
		pymoney.io.write_categories(c_filename, categorytree, notfoundcategory)

	def cmd_move(**args):
		node = categorytree.findNode(args["name"])
		newparent = categorytree.findNode(args["newparentname"])

		if not node:
			print("no such node: " + args["name"])
			return

		if not newparent:
			print("no such node: " + args["newparentname"])
			return

		if newparent.isChildOf(node):
			print("cannot move node to one of its subnodes: " + args["name"])
			return

		node.parent.removeChildNode(args["name"])
		newparent.appendChildNode(node)

		pymoney.io.write_categories(c_filename, categorytree, notfoundcategory)
		
	def cmd_rename_merge(**args):
		node = categorytree.findNode(args["oldname"])
		newnode = categorytree.findNode(args["newname"])
		parent = node.parent
		
		if not node:
			print("no such node: " + args["oldname"])
			return
			
		if args["merge"] and not node.parent:
			print("cannot move root node")
			return
		
		if not args["merge"]:
			if newnode and not newnode.isChildOf(notfoundcategory):
				print("node already exists: " + args["newname"])
				return

		if newnode and newnode.isChildOf(notfoundcategory):
			newnode.parent.removeChildNode(args["newname"])
		
		if args["merge"]:
			node.parent.removeChildNode(nodename)
		else:
			node.rename(args["newname"])
		
		if args["merge"]:
			for t in transactions:
				if t.category == node:
					t.category = newnode
				
		pymoney.io.write_categories(c_filename, categorytree, notfoundcategory)
		pymoney.io.write_transactions(t_filename, transactionfactory, transactions)
		
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
		d_summary = {}
	
		for c in categorytree:
			d_summary[c.name] = pymoney.data.NodeSummary()
			
		for t in transactions:
			if args["year"] and t.date.year != args["year"]:
				continue
			
			if args["month"] and t.date.month != args["month"]:
				continue
			
			d_summary[t.category.name].amount += t.amount
			
			c = t.category
			while c:
				d_summary[c.name].sum += t.amount
				c = c.parent
			
		
		print("{0:<30} {1:>10} {2:>10}".format("node", "amount", "sum"))
		print()
		for c in categorytree:
			if len(c.children):
				nodesym = "+"
			else:
				nodesym = "-"
			
			print("{0:<30} {1:>10.2f} {2:>10.2f}".format("    "*c.getDepth() + " " + nodesym + " " + c.name, d_summary[c.name].amount, d_summary[c.name].sum))
			
	def cmd_monthly(**args):
		mindate = None
		maxdate = None
		for t in transactions:
			if not mindate or t.date < mindate:
				mindate = t.date
				
			if not maxdate or t.date > maxdate:
				maxdate = t.date
	
		category = categorytree.findNode(args["category"])
		
		if not category:
			print("no such category: " + args["category"], file=sys.stderr)
			return
		
		year = mindate.year
		month = mindate.month
	
		print("{0:<10} {1:<30} {2:>10} {3:>10}".format("date", "node", "amount", "sum"))
		print()
	
		while datetime.date(year, month, 1) <= maxdate:
			summary = pymoney.data.NodeSummary()
			
			for t in transactions:
				if t.date.year != year or t.date.month != month:
					continue
			
				if t.category == category:
					summary.amount += t.amount
					summary.sum += t.amount 
			
				if t.category.isChildOf(category):
					summary.sum += t.amount
			
		
			print("{0:<10} {1:<30} {2:>10.2f} {3:>10.2f}".format(str(datetime.date(year, month, 1)), category.name, summary.amount, summary.sum))
			
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
	p_transaction_list.add_argument("--year");
	p_transaction_list.add_argument("--month");
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
	p_category_rename.add_argument("oldname")
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
