# vim: expandtab softtabstop=0 list listchars=tab\:>-:
import argparse
import sys as _sys


class ArgumentParser(argparse.ArgumentParser):
        def __init__(self,
                        prog=None,
                        usage=None,
                        description=None,
                        epilog=None,
                        parents=[],
                        formatter_class=argparse.HelpFormatter,
                        prefix_chars='-',
                        fromfile_prefix_chars=None,
                        argument_default=None,
                        conflict_handler='error',
                        add_help=True,
                        allow_abbrev=True):
                argparse.ArgumentParser.__init__(self, prog, usage, description, epilog, parents, formatter_class,
                        prefix_chars, fromfile_prefix_chars, argument_default, conflict_handler,
                        add_help, allow_abbrev)

        def exit(self, status=0, message=None):
                if message:
                        self._print_message(message, _sys.stderr)
                # skip _sys.exit(...) and throw exception instead
                raise Exception(message)
