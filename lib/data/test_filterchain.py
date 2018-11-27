# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
from lib.data import filterchain

import unittest


class TestFilter(unittest.TestCase):
        def setUp(self):
                self.trueFilter = filterchain.Filter(lambda n: True)
                self.falseFilter = filterchain.Filter(lambda n: False)

        def test_default_filter(self):
                self.assertTrue(self.trueFilter(123))
                self.assertFalse(self.falseFilter(123))

        def test_or_concat(self):
                false_or_false_filter = self.falseFilter.or_concat(self.falseFilter)
                false_or_true_filter = self.falseFilter.or_concat(self.trueFilter)
                true_or_false_filter = self.trueFilter.or_concat(self.falseFilter)
                true_or_true_filter = self.trueFilter.or_concat(self.trueFilter)

                self.assertFalse(false_or_false_filter(123), "false or false should equal to false")
                self.assertTrue(false_or_true_filter(123), "false or true should equal to true")
                self.assertTrue(true_or_false_filter(123), "true or false should equal to true")
                self.assertTrue(true_or_true_filter(123), "true or true should equal to true")

        def test_and_concat(self):
                false_and_false_filter = self.falseFilter.and_concat(self.falseFilter)
                false_and_true_filter = self.falseFilter.and_concat(self.trueFilter)
                true_and_false_filter = self.trueFilter.and_concat(self.falseFilter)
                true_and_true_filter = self.trueFilter.and_concat(self.trueFilter)

                self.assertFalse(false_and_false_filter(123), "false and false should equal to false")
                self.assertFalse(false_and_true_filter(123), "false and true should equal to false")
                self.assertFalse(true_and_false_filter(123), "true and false should equal to false")
                self.assertTrue(true_and_true_filter(123), "true and true should equal to true")

        def test_negate(self):
                negated_false_filter = self.falseFilter.negate()
                negated_true_filter = self.trueFilter.negate()

                self.assertTrue(negated_false_filter(123), "negation of false should be true")
                self.assertFalse(negated_true_filter(123), "negation of true should be false")


if __name__ == '__main__':
        unittest.main()
