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

                self.assertFalse( DateRange(2019, operator="<").is_date_in_range(date),         "<2019           > 2019-06-15")
                self.assertFalse( DateRange(2019, 6, operator="<").is_date_in_range(date),      "<2019-06        > 2019-06-15")
                self.assertFalse( DateRange(2019, 6, 15, operator="<").is_date_in_range(date),  "<2019-06-15     > 2019-06-15")

                self.assertTrue( DateRange(2020, operator="<").is_date_in_range(date),          "2019-06-15     in <2020")
                self.assertTrue( DateRange(2019, 7, operator="<").is_date_in_range(date),       "2019-06-15     in <2019-07")
                self.assertTrue( DateRange(2019, 6, 16, operator="<").is_date_in_range(date),   "2019-06-15     in <2019-06-16")

        def test_is_date_in_range_before_or_equal(self):
                date = datetime.date(2019, 6, 15)

                self.assertFalse( DateRange(2018, operator="<=").is_date_in_range(date),        "<=2018         > 2019-06-15")
                self.assertFalse( DateRange(2019, 5, operator="<=").is_date_in_range(date),     "<=2019-05      > 2019-06-15")
                self.assertFalse( DateRange(2019, 6, 14, operator="<=").is_date_in_range(date), "<=2019-06-14   > 2019-06-15")

                self.assertTrue( DateRange(2019, operator="<=").is_date_in_range(date),         "2019-06-15     in <=2019")
                self.assertTrue( DateRange(2019, 6, operator="<=").is_date_in_range(date),      "2019-06-15     in <=2019-06")
                self.assertTrue( DateRange(2019, 6, 15, operator="<=").is_date_in_range(date),  "2019-06-15     in <=2019-06-15")

        def test_is_date_in_range_after(self):
                date = datetime.date(2019, 6, 15)

                self.assertFalse( DateRange(2019, operator=">").is_date_in_range(date),         ">2019           > 2019-06-15")
                self.assertFalse( DateRange(2019, 6, operator=">").is_date_in_range(date),      ">2019-06        > 2019-06-15")
                self.assertFalse( DateRange(2019, 6, 15, operator=">").is_date_in_range(date),  ">2019-06-15     > 2019-06-15")

                self.assertTrue( DateRange(2018, operator=">").is_date_in_range(date),          "2019-06-15     in >2018")
                self.assertTrue( DateRange(2019, 5, operator=">").is_date_in_range(date),       "2019-06-15     in >2019-05")
                self.assertTrue( DateRange(2019, 6, 14, operator=">").is_date_in_range(date),   "2019-06-15     in >2019-06-14")

        def test_is_date_in_range_after_or_equal(self):
                date = datetime.date(2019, 6, 15)

                self.assertFalse( DateRange(2020, operator=">=").is_date_in_range(date),        ">=2020         < 2019-06-15")
                self.assertFalse( DateRange(2019, 7, operator=">=").is_date_in_range(date),     ">=2019-07      < 2019-06-15")
                self.assertFalse( DateRange(2019, 6, 16, operator=">=").is_date_in_range(date), ">=2019-06-16   < 2019-06-15")

                self.assertTrue( DateRange(2019, operator=">=").is_date_in_range(date),         "2019-06-15     in >=2019")
                self.assertTrue( DateRange(2019, 6, operator=">=").is_date_in_range(date),      "2019-06-15     in >=2019-06")
                self.assertTrue( DateRange(2019, 6, 15, operator=">=").is_date_in_range(date),  "2019-06-15     in >=2019-06-15")


if __name__ == "__main__":
        unittest.main()
