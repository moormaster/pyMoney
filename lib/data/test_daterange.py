# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
import unittest
import datetime

from lib.data.daterange import DateRange

class Test_daterange(unittest.TestCase):
        def test_is_date_in_range(self):
                date = datetime.date(2019, 6, 15)

                self.assertFalse( DateRange(2018).is_date_in_range(date),               "2018           < 2019-06-15")
                self.assertFalse( DateRange(2019, 5).is_date_in_range(date),            "2019-05        < 2019-06-15")
                self.assertFalse( DateRange(2019, 6, 14).is_date_in_range(date),        "2019-06-14     < 2019-06-15")

                self.assertFalse( DateRange(2020).is_date_in_range(date),               "2020           > 2019-06-15")
                self.assertFalse( DateRange(2019, 5).is_date_in_range(date),            "2019-05        > 2019-06-15")
                self.assertFalse( DateRange(2019, 6, 16).is_date_in_range(date),        "2019-06-16     > 2019-06-15")

                self.assertTrue( DateRange().is_date_in_range(date),                    "2019-06-15     in ''")
                self.assertTrue( DateRange(2019).is_date_in_range(date),                "2019-06-15     in 2019")
                self.assertTrue( DateRange(2019, 6).is_date_in_range(date),             "2019-06-15     in 2019-06")
                self.assertTrue( DateRange(2019, 6, 15).is_date_in_range(date),         "2019-06-15     in 2019-06-15")

        def test_is_date_in_range_before(self):
                date = datetime.date(2019, 6, 15)

                dateYRange = DateRange(2019)
                dateYRange.set_is_before(True)

                dateYMRange = DateRange(2019, 6)
                dateYMRange.set_is_before(True)

                dateYMDRange = DateRange(2019, 6, 15)
                dateYMDRange.set_is_before(True)


                self.assertFalse( dateYRange.is_date_in_range(date),    "<2019           > 2019-06-15")
                self.assertFalse( dateYMRange.is_date_in_range(date),   "<2019-06        > 2019-06-15")
                self.assertFalse( dateYMDRange.is_date_in_range(date),  "<2019-06-15     > 2019-06-15")


                dateYRange = DateRange(2020)
                dateYRange.set_is_before(True)

                dateYMRange = DateRange(2019, 7)
                dateYMRange.set_is_before(True)

                dateYMDRange = DateRange(2019, 6, 16)
                dateYMDRange.set_is_before(True)

                self.assertTrue( dateYRange.is_date_in_range(date),     "2019-06-15     in <2020")
                self.assertTrue( dateYMRange.is_date_in_range(date),    "2019-06-15     in <2019-07")
                self.assertTrue( dateYMDRange.is_date_in_range(date),   "2019-06-15     in <2019-06-16")

        def test_is_date_in_range_before_or_equal(self):
                date = datetime.date(2019, 6, 15)

                dateYRange = DateRange(2018)
                dateYRange.set_is_before_or_equal(True)

                dateYMRange = DateRange(2019, 5)
                dateYMRange.set_is_before_or_equal(True)

                dateYMDRange = DateRange(2019, 6, 14)
                dateYMDRange.set_is_before_or_equal(True)


                self.assertFalse( dateYRange.is_date_in_range(date),    "<=2018         > 2019-06-15")
                self.assertFalse( dateYMRange.is_date_in_range(date),   "<=2019-05      > 2019-06-15")
                self.assertFalse( dateYMDRange.is_date_in_range(date),  "<=2019-06-14   > 2019-06-15")


                dateYRange = DateRange(2019)
                dateYRange.set_is_before_or_equal(True)

                dateYMRange = DateRange(2019, 6)
                dateYMRange.set_is_before_or_equal(True)

                dateYMDRange = DateRange(2019, 6, 15)
                dateYMDRange.set_is_before_or_equal(True)

                self.assertTrue( dateYRange.is_date_in_range(date),     "2019-06-15     in <=2019")
                self.assertTrue( dateYMRange.is_date_in_range(date),    "2019-06-15     in <=2019-06")
                self.assertTrue( dateYMDRange.is_date_in_range(date),   "2019-06-15     in <=2019-06-15")

        def test_is_date_in_range_after(self):
                date = datetime.date(2019, 6, 15)

                dateYRange = DateRange(2019)
                dateYRange.set_is_after(True)

                dateYMRange = DateRange(2019, 6)
                dateYMRange.set_is_after(True)

                dateYMDRange = DateRange(2019, 6, 15)
                dateYMDRange.set_is_after(True)


                self.assertFalse( dateYRange.is_date_in_range(date),    ">2019           > 2019-06-15")
                self.assertFalse( dateYMRange.is_date_in_range(date),   ">2019-06        > 2019-06-15")
                self.assertFalse( dateYMDRange.is_date_in_range(date),  ">2019-06-15     > 2019-06-15")


                dateYRange = DateRange(2018)
                dateYRange.set_is_after(True)

                dateYMRange = DateRange(2019, 5)
                dateYMRange.set_is_after(True)

                dateYMDRange = DateRange(2019, 6, 14)
                dateYMDRange.set_is_after(True)

                self.assertTrue( dateYRange.is_date_in_range(date),     "2019-06-15     in >2018")
                self.assertTrue( dateYMRange.is_date_in_range(date),    "2019-06-15     in >2019-05")
                self.assertTrue( dateYMDRange.is_date_in_range(date),   "2019-06-15     in >2019-06-14")

        def test_is_date_in_range_after_or_equal(self):
                date = datetime.date(2019, 6, 15)

                dateYRange = DateRange(2020)
                dateYRange.set_is_after_or_equal(True)

                dateYMRange = DateRange(2019, 7)
                dateYMRange.set_is_after_or_equal(True)

                dateYMDRange = DateRange(2019, 6, 16)
                dateYMDRange.set_is_after_or_equal(True)


                self.assertFalse( dateYRange.is_date_in_range(date),    ">=2020         < 2019-06-15")
                self.assertFalse( dateYMRange.is_date_in_range(date),   ">=2019-07      < 2019-06-15")
                self.assertFalse( dateYMDRange.is_date_in_range(date),  ">=2019-06-16   < 2019-06-15")


                dateYRange = DateRange(2019)
                dateYRange.set_is_after_or_equal(True)

                dateYMRange = DateRange(2019, 6)
                dateYMRange.set_is_after_or_equal(True)

                dateYMDRange = DateRange(2019, 6, 15)
                dateYMDRange.set_is_after_or_equal(True)

                self.assertTrue( dateYRange.is_date_in_range(date),     "2019-06-15     in >=2019")
                self.assertTrue( dateYMRange.is_date_in_range(date),    "2019-06-15     in >=2019-06")
                self.assertTrue( dateYMDRange.is_date_in_range(date),   "2019-06-15     in >=2019-06-15")


if __name__ == "__main__":
        unittest.main()
