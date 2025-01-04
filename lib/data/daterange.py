# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
import datetime

class DateRange:
    def __init__(self, year=None, month=None, day=None, operator="="):
        self.year = year
        self.month = month
        self.day = day
        self.operator = operator

    def is_date_in_range(self, date):
        assert isinstance(date, datetime.date)
        if not self.year is None:
            if self.year < date.year:
                if self.operator == ">" or self.operator == ">=":
                    return True

                return False
            if self.year > date.year:
                if self.operator == "<" or self.operator == "<=":
                    return True

                return False

        if not self.month is None:
            if self.month < date.month:
                if self.operator == ">" or self.operator == ">=":
                    return True

                return False
            if self.month > date.month:
                if self.operator == "<" or self.operator == "<=":
                    return True

                return False

        if not self.day is None:
            if self.day < date.day:
                if self.operator == ">" or self.operator == ">=":
                    return True

                return False
            if self.day > date.day:
                if self.operator == "<" or self.operator == "<=":
                    return True

                return False

        if self.operator == "<" or self.operator == ">":
            return False

        return True

