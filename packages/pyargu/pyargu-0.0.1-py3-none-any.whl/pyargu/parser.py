import sys
import textwrap

class Argument:
    def __init__(self, name, short=None, help="", required=False, default=None, takes_value=False):
        self.name = name
        self.short = short
        self.help = help
        self.required = required
        self.default = default
        self.takes_value = takes_value


class ArgumentParser:
    def __init__(self, description=""):
        self.description = description
        self.arguments = {}
        self.values = {}

    def add_argument(self, name, short=None, help="", required=False, default=None, takes_value=False):
        arg = Argument(name, short, help, required, default, takes_value)
        self.arguments[name] = arg

    def parse_args(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]
        
        self.values = {name: arg.default for name, arg in self.arguments.items()}

        i = 0
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
                        raise ValueError(f"Expected value after {token}")
                    value = argv[i + 1]
                    self.values[matched.name] = value
                    i += 2
                else:
                    self.values[matched.name] = True
                    i += 1
            elif "=" in token and token.startswith("--"):
                key, val = token[2:].split("=", 1)
                if key in self.arguments:
                    self.values[key] = val
                i += 1
            else:
                # positional arguments
                if "_positional" not in self.values:
                    self.values["_positional"] = []
                self.values["_positional"].append(token)
                i += 1

        # check required
        for name, arg in self.arguments.items():
            if arg.required and self.values.get(name) is None:
                raise ValueError(f"Missing required argument: --{name}")

        return self.values

    def print_help(self):
        print("Usage: program [options]\n")
        if self.description:
            print(self.description)
            print()
        print("Options:")
        for name, arg in self.arguments.items():
            short = f"-{arg.short}, " if arg.short else "    "
            takes = " <value>" if arg.takes_value else ""
            print(f"  {short}--{name}{takes}")
            if arg.help:
                print(textwrap.indent(arg.help, " " * 8))
        print("")

