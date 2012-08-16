from . import data
import csv
import os.path

def read_transactions(filename, transactionfactory):
	with open(filename) as f:
		r = csv.DictReader(f)
		
		l = []
		for d in r:
			t = transactionfactory.create(**d)
			
			if t:
				l.append(t)
		
		return sorted(l, key=lambda t: t.date)
	
def write_transactions(filename, transactionfactory, transactions, append=False):
	if append and not os.path.exists(filename):
		append=False

	if append:
		mode='a'
	else:
		mode='w'
	
	with open(filename, mode) as f:
		w = csv.DictWriter(f, fieldnames=data.Transaction.fields)
		
		if not append:
			w.writeheader()

		for t in transactions:
			w.writerow(transactionfactory.create_string_dict(t))
			
def read_categories(filename):
	categorytree = None
	
	nodestack = []

	with open(filename, 'r') as f:
		line = f.readline()
		while line:
			depth = line.count("	")
			name = line.strip()
						
			while len(nodestack) > depth:
				nodestack.pop()
			
			if categorytree:
				node = nodestack[len(nodestack)-1]
				node = node.appendChildNode(data.TreeNode(name))
			else:
				categorytree = data.TreeNode(name)
				node = categorytree
			
			nodestack.append(node)
			line = f.readline()
		
	return categorytree
	
def write_categories(filename, categorytree, notfoundcategory):
	nodestack = []
	
	with open(filename, 'w') as f:
		for node in categorytree:
			if not node.isChildOf(notfoundcategory):
				f.write("	" * node.getDepth())
				f.write(node.name)
				f.write("\n")

