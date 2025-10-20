import sys
import textwrap
from .colors import Colors
from .utils import convert_type, format_default


class Argument:
    def __init__(self, name, short=None, help="", required=False, default=None,
                 takes_value=False, arg_type=str):
        self.name = name
        self.short = short
        self.help = help
        self.required = required
        self.default = default
        self.takes_value = takes_value
        self.arg_type = arg_type


class SubCommand:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.arguments = {}

    def add_argument(self, *args, **kwargs):
        arg = Argument(*args, **kwargs)
        self.arguments[arg.name] = arg


class ArgumentParser:
    def __init__(self, description=""):
        self.description = description
        self.arguments = {}
        self.subcommands = {}

    def add_argument(self, name, short=None, help="", required=False, default=None,
                     takes_value=False, arg_type=str):
        arg = Argument(name, short, help, required, default, takes_value, arg_type)
        self.arguments[name] = arg

    def add_subcommand(self, name, description=""):
        sub = SubCommand(name, description)
        self.subcommands[name] = sub
        return sub

    def _color(self, text, color):
        return Colors.colorize(text, color)

    def parse_args(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]

        if not argv or argv[0] in ("-h", "--help"):
            self.print_help()
            sys.exit(0)

        # Subcommand check
        if argv[0] in self.subcommands:
            sub = self.subcommands[argv[0]]
            return self._parse_subcommand(sub, argv[1:], argv[0])
        else:
            return self._parse_main(argv)

    def _parse_main(self, argv):
        values = {name: arg.default for name, arg in self.arguments.items()}
        i = 0
        positional = []

        while i < len(argv):
            token = argv[i]
            if token in ("--help", "-h"):
                self.print_help()
                sys.exit(0)

            matched = None
            for name, arg in self.arguments.items():
                if token == f"--{name}" or (arg.short and token == f"-{arg.short}"):
                    matched = arg
                    break

            if matched:
                if matched.takes_value:
                    if i + 1 >= len(argv):
                        self._error(f"Argumen {token} memerlukan nilai.")
                    raw_val = argv[i + 1]
                    values[matched.name] = convert_type(raw_val, matched.arg_type)
                    i += 2
                else:
                    values[matched.name] = True
                    i += 1
            else:
                positional.append(token)
                i += 1

        values["_positional"] = positional

        for name, arg in self.arguments.items():
            if arg.required and values[name] is None:
                self._error(f"Argumen --{name} wajib diisi.")

        return values

    def _parse_subcommand(self, sub, argv, subname):
        values = {n: a.default for n, a in sub.arguments.items()}
        i = 0
        positional = []

        while i < len(argv):
            token = argv[i]
            if token in ("--help", "-h"):
                self.print_sub_help(subname)
                sys.exit(0)

            matched = None
            for name, arg in sub.arguments.items():
                if token == f"--{name}" or (arg.short and token == f"-{arg.short}"):
                    matched = arg
                    break

            if matched:
                if matched.takes_value:
                    if i + 1 >= len(argv):
                        self._error(f"Argumen {token} memerlukan nilai.")
                    raw_val = argv[i + 1]
                    values[matched.name] = convert_type(raw_val, matched.arg_type)
                    i += 2
                else:
                    values[matched.name] = True
                    i += 1
            else:
                positional.append(token)
                i += 1

        values["_positional"] = positional
        return {"_subcommand": subname, **values}

    def _error(self, message):
        print(self._color("Error:", Colors.RED), message)
        sys.exit(1)

    def print_help(self):
        print(self._color("Usage:", Colors.CYAN), "program [options]")
        print()
        if self.description:
            print(self.description)
            print()

        if self.arguments:
            print(self._color("Options:", Colors.YELLOW))
            for name, arg in self.arguments.items():
                short = f"-{arg.short}, " if arg.short else "    "
                takes = " <value>" if arg.takes_value else ""
                print(f"  {short}--{name}{takes}{format_default(arg.default)}")
                if arg.help:
                    print(" " * 8 + arg.help)
            print()

        if self.subcommands:
            print(self._color("Subcommands:", Colors.MAGENTA))
            for name, sub in self.subcommands.items():
                print(f"  {name:<12} {sub.description}")
            print()

    def print_sub_help(self, subname):
        sub = self.subcommands[subname]
        print(self._color(f"Usage: program {subname} [options]", Colors.CYAN))
        print(sub.description)
        print()
        print(self._color("Options:", Colors.YELLOW))
        for name, arg in sub.arguments.items():
            short = f"-{arg.short}, " if arg.short else "    "
            takes = " <value>" if arg.takes_value else ""
            print(f"  {short}--{name}{takes}{format_default(arg.default)}")
            if arg.help:
                print(" " * 8 + arg.help)
        print()
