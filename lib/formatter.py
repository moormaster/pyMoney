import lib.data
import lib.data.moneydata
import lib.io
import lib.io.parser
import lib.io.Categories
import lib.io.Transactions


class CategoryNameFormatter:
	STRATEGY_NAME = 0
	STRATEGY_UNIQUE_NAME = 1
	STRATEGY_FULL_NAME = 2

	def __init__(self):
		self.d_namecache = {}
		self.strategy = self.STRATEGY_UNIQUE_NAME
		self.indentWithTreeLevel = False

		pass


	def set_strategy(self, strategy):
		if not strategy in [self.STRATEGY_NAME, self.STRATEGY_UNIQUE_NAME, self.STRATEGY_FULL_NAME]:
			raise "invalid strategy: " + str(strategy)

		if self.strategy != strategy:
			self.d_namecache = {}

		self.strategy = strategy


	def set_indent_with_tree_level(self, flag):
		if not flag:
			self.indentWithTreeLevel = False
		else:
			self.indentWithTreeLevel = True


	def format(self, category):
		assert isinstance(category, lib.data.moneydata.CategoryTreeNode)

		if not id(category) in self.d_namecache:
			if self.strategy == self.STRATEGY_NAME:
				self.d_namecache[id(category)] = category.name
			elif self.strategy == self.STRATEGY_UNIQUE_NAME:
				self.d_namecache[id(category)] = category.get_unique_name()
			else:
				self.d_namecache[id(category)] = category.get_full_name()

		formattedvalue = self.d_namecache[id(category)]
		if self.indentWithTreeLevel:
			formattedvalue = "  "*category.get_depth() + formattedvalue

		return formattedvalue


class TableFormatter:
	def __init__(self):
		self.columns = []
		pass

	def add_column(self, dataindex):
		column = TableFormatterColumn(dataindex)
		self.columns.append(column)

		return column

	def get_trimmed_value(self, string, max_length):
		if not max_length:
			return string

		if len(string) <= max_length:
			return string

		return string[0:max_length-4] + "..." + string[-1]

	def get_formatted_cell_value(self, column, linedata):
		assert isinstance(column, TableFormatterColumn)

		try:
			value = column.get_formatstring().format(*linedata)
		except:
			value = ""

		value = self.get_trimmed_value(value, column.get_maxwidth())

		return value

	def get_formatted_headercell_value(self, column, linedata):
		assert isinstance(column, TableFormatterColumn)

		value = column.get_headerformatstring().format(*linedata)
		value = self.get_trimmed_value(value, column.get_maxwidth())

		return value

	def get_data_column_width(self, headerdata, data):
		if not len(self.columns):
			return []

		linevalues = []

		index = 0
		for column in self.columns:
			value = self.get_formatted_headercell_value(column, headerdata)
			linevalues.append(value)

			index = index+1

		datawidth = list(map(lambda s: len(s), linevalues))

		for linedata in data:
			linevalues = []

			index = 0
			for column in self.columns:
				value = self.get_formatted_cell_value(column, linedata)
				linevalues.append(value)

				index = index+1

			linedatawidth = list(map(lambda s: len(s), linevalues))

			for i in range(len(linedatawidth)):
				if linedatawidth[i] > datawidth[i]:
					datawidth[i] = linedatawidth[i]

		return datawidth

	def get_formatted_lines(self, headerdata, data):
		if not len(self.columns):
			return []

		previous_column_width = []

		datawidth = self.get_data_column_width(headerdata, data)

		index = 0
		for column in self.columns:
			assert isinstance(column, TableFormatterColumn)

			previous_column_width.append(column.get_width())
			column.set_width(datawidth[index])

			index = index+1

		# last column does not have a minimum width (if left aligned and string)
		if column.get_alignment() == "<":
			column.set_width(None)

		lines = []

		line = ""
		index = 0
		for column in self.columns:
			value = self.get_formatted_headercell_value(column, headerdata)

			if index == 0:
				line = value
			else:
				line = line + " " + value

			index = index+1

		lines.append(line)

		for linedata in data:
			line = ""
			index = 0
			for column in self.columns:
				value = self.get_formatted_cell_value(column, linedata)

				if index == 0:
					line = value
				else:
					line = line + " " + value

				index = index+1

			lines.append(line)

		# restore previous column settings
		index = 0
		for column in self.columns:
			assert isinstance(column, TableFormatterColumn)

			column.set_width(previous_column_width[index])


			index = index+1


		return lines


class TableFormatterColumn:
	def __init__(self, dataindex):
		self._dataindex = dataindex

		self._alignment = "<"
		self._width = None
		self._precision = None
		self._type = None

		self._maxwidth = None

		pass

	def get_alignment(self):
		return self._alignment

	def set_alignment(self, value):
		self._alignment = value

	def get_dataindex(self):
		return self._dataindex

	def set_dataindex(self, value):
		self._dataindex = value

	def get_maxwidth(self):
		return self._maxwidth

	def set_maxwidth(self, value):
		self._maxwidth = value

	def get_precision(self):
		return self._precision

	def set_precision(self, value):
		self._precision = value

	def get_type(self):
		return self._type

	def set_type(self, value):
		self._type = value

	def get_width(self):
		return self._width

	def set_width(self, value):
		self._width = value

	def get_headerformatstring(self):
		index = str(self._dataindex)
		formatstring = ""

		if not self._alignment is None:
			if formatstring == "":
				formatstring = ":"
			formatstring = formatstring + self._alignment

		if not self._width is None:
			if formatstring == "":
				formatstring = ":"
			formatstring = formatstring + str(self._width)

		return "{" + index + formatstring + "}"

	def get_formatstring(self):
		index = str(self._dataindex)
		formatstring = ""

		if not self._alignment is None:
			if formatstring == "":
				formatstring = ":"
			formatstring = formatstring + self._alignment

		if not self._width is None:
			if formatstring == "":
				formatstring = ":"
			formatstring = formatstring + str(self._width)

		if not self._precision is None:
			if formatstring == "":
				formatstring = ":"
			formatstring = formatstring + "." + str(self._precision)

		if not self._type is None:
			if formatstring == "":
				formatstring = ":"
			formatstring = formatstring + self._type

		return "{" + index + formatstring + "}"