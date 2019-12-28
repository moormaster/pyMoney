# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
import datetime

class DateRange:
        def __init__(self, year=None, month=None, day=None):
                self.year = year
                self.month = month
                self.day = day

                self.reset_before_or_after_flags()

        def reset_before_or_after_flags(self):
                self.is_before = False
                self.is_before_or_equal = False

                self.is_after = False
                self.is_after_or_equal = False

        def set_is_after(self, boolean):
                if boolean:
                        self.reset_before_or_after_flags()
                self.is_after = boolean

        def set_is_after_or_equal(self, boolean):
                if boolean:
                       self.reset_before_or_after_flags()
                self.is_after_or_equal = boolean

        def set_is_before(self, boolean):
                if boolean:
                        self.reset_before_or_after_flags()
                self.is_before = boolean

        def set_is_before_or_equal(self, boolean):
                if boolean:
                       self.reset_before_or_after_flags()
                self.is_before_or_equal = boolean

        def is_date_in_range(self, date):
                assert isinstance(date, datetime.date)
                if not self.year is None:
                        if self.year < date.year:
                                if self.is_after or self.is_after_or_equal:
                                        return True

                                return False
                        if self.year > date.year:
                                if self.is_before or self.is_before_or_equal:
                                        return True

                                return False

                if not self.month is None:
                        if self.month < date.month:
                                if self.is_after or self.is_after_or_equal:
                                        return True

                                return False
                        if self.month > date.month:
                                if self.is_before or self.is_before_or_equal:
                                        return True

                                return False

                if not self.day is None:
                        if self.day < date.day:
                                if self.is_after or self.is_after_or_equal:
                                        return True

                                return False
                        if self.day > date.day:
                                if self.is_before or self.is_before_or_equal:
                                        return True

                                return False

                if self.is_before or self.is_after:
                        return False

                return True

