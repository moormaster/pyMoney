# vim: expandtab softtabstop=0 list listchars=tab\:>-,space\:·:
class Filter:
    def __init__(self, filter_func):
        self.filter_func = filter_func

    def __call__(self, item):
        return self.filter_func(item)

    def or_concat(self, filter_func):
        return Filter(lambda item: self(item) or filter_func(item))

    def xor_concat(self, filter_func):
        return Filter(lambda item: self(item) and not filter_func(item) or not self(item) and filter_func(item))

    def and_concat(self, filter_func):
        return Filter(lambda item: self(item) and filter_func(item))

    def negate(self):
        return Filter(lambda item: not self(item))
