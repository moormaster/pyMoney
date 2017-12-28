from lib.data import filter

import unittest


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.data = []
        self.data.append("A1")
        self.data.append("A2")
        self.data.append("B1")
        self.data.append("B2")

        self.charAFilter = filter.Filter(lambda v: v[0] == "A")
        self.num1Filter = filter.Filter(lambda v: v[1] == "1")

    def test_filters(self):
        self.assertTrue(self.charAFilter(self.data[0]))
        self.assertTrue(self.charAFilter(self.data[1]))
        self.assertFalse(self.charAFilter(self.data[2]))
        self.assertFalse(self.charAFilter(self.data[3]))

        self.assertTrue(self.num1Filter(self.data[0]))
        self.assertFalse(self.num1Filter(self.data[1]))
        self.assertTrue(self.num1Filter(self.data[2]))
        self.assertFalse(self.num1Filter(self.data[3]))

    def test_or_concat(self):
        transactionfilter = [self.charAFilter.or_concat(self.num1Filter),
                             self.num1Filter.or_concat(self.charAFilter)]

        for f in transactionfilter:
            for d in self.data:
                if self.charAFilter(d) or self.num1Filter(d):
                    self.assertTrue(f(d))
                else:
                    self.assertFalse(f(d))

    def test_and_concat(self):
        transactionfilter = [self.charAFilter.and_concat(self.num1Filter),
                             self.num1Filter.and_concat(self.charAFilter)]

        for f in transactionfilter:
            for d in self.data:
                if self.charAFilter(d) and self.num1Filter(d):
                    self.assertTrue(f(d))
                else:
                    self.assertFalse(f(d))

    def test_negate(self):
        transactionfilter = [self.charAFilter, self.num1Filter]

        for f in transactionfilter:
            nf = f.negate()

            for t in self.data:
                if not f(t):
                    self.assertTrue(nf(t))
                else:
                    self.assertFalse(nf(t))


class TestFilterIterator(unittest.TestCase):
    def setUp(self):
        self.list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_filteriterator(self):
        filter_func = lambda n: n > 5
        filteriter = filter.FilterIterator(self.list.__iter__(), filter_func)

        l = list(filteriter)

        self.assertEqual(l, [6, 7, 8, 9, 10])


if __name__ == '__main__':
    unittest.main()
