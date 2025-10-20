from argparse import ArgumentParser

from rushlib.output import print_red


class Command(ArgumentParser):
    def __init__(self,
                 print_error=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.print_error = print_error

    def error(self, message):
        if self.print_error:
            print_red(f"{message}")
