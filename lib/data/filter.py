class FilterIterator:
	def __init__(self, iterator, filter_func):
		self.iterator = iterator
		self.filter_func = filter_func
		self.index = None

	def __iter__(self):
		return self

	def __next__(self):
		if self.index is None:
			self.index = -1

		nextitem = self.iterator.__next__()
		self.index += 1

		while nextitem is not None and not self.filter_func(nextitem):
			nextitem = self.iterator.__next__()
			self.index += 1

		return nextitem


class Filter:
	def __init__(self, filter_func):
		self.filter_func = filter_func

	def __call__(self, item):
		return self.filter_func(item)

	def or_concat(self, filter_func):
		return Filter(lambda item: self(item) or filter_func(item))

	def and_concat(self, filter_func):
		return Filter(lambda item: self(item) and filter_func(item))

	def negate(self):
		return Filter(lambda item: not self(item))
