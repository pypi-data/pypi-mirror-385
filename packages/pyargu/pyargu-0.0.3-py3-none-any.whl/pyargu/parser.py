import os, sys
from .colors import Colors as C
from .errors import ParseError
from .utils import convert_type, deep_merge, load_config, env_key, wrap
from .completion import generate_completion

class Argument:
    def __init__(
        self, name, short=None, help="", required=False, default=None,
        takes_value=None, arg_type=str, nargs=1, choices=None, validators=None, metavar=None
    ):
        self.name = name
        self.short = short
        self.help = help
        self.required = required
        self.default = default
        self.arg_type = arg_type
        self.nargs = nargs  # 1 | "?" | "+" | "*" | int
        self.choices = choices
        self.validators = validators or []
        self.metavar = metavar or name.upper()
        # infer takes_value: bool arg default to flag
        self.takes_value = bool(takes_value if takes_value is not None else (arg_type is not bool))

    def convert(self, raw):
        if self.nargs in (None, 1):
            val = convert_type(raw, self.arg_type)
            return self._validate(val)
        # multiple
        src = raw if isinstance(raw, list) else [raw]
        vals = [convert_type(v, self.arg_type) for v in src]
        return [self._validate(v) for v in vals]

    def _validate(self, v):
        if self.choices is not None and v not in self.choices:
            raise ValueError(f"harus salah satu dari {self.choices}")
        for fn in self.validators:
            v = fn(v)
        return v


class SubCommand:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.arguments = {}

    def add_argument(self, *args, **kwargs):
        arg = Argument(*args, **kwargs)
        self.arguments[arg.name] = arg


class ArgumentParser:
    def __init__(self, description="", env_prefix="ARGU"):
        self.description = description
        self.env_prefix = env_prefix
        self.arguments = {}
        self.subcommands = {}
        # built-in: --config, --generate-completion
        self.add_argument("config", short=None, help="Path file konfigurasi (JSON atau k=v)", takes_value=True)
        self.add_argument("generate-completion", help="Cetak skrip completion (bash/zsh/fish). Gunakan dengan --shell.", takes_value=False, default=False, arg_type=bool)
        self.add_argument("shell", help="Target shell untuk --generate-completion", takes_value=True, choices=["bash","zsh","fish"])

    # API
    def add_argument(self, *args, **kwargs):
        arg = Argument(*args, **kwargs)
        self.arguments[arg.name] = arg
        return arg

    def add_subcommand(self, name, description=""):
        sub = SubCommand(name, description)
        self.subcommands[name] = sub
        return sub

    # Parsing
    def parse_args(self, argv=None):
        if argv is None:
            argv = sys.argv[1:]

        # handle early help
        if not argv or argv[0] in ("-h", "--help"):
            self.print_help(); raise SystemExit(0)

        # completion
        if "--generate-completion" in argv:
            # best-effort prog name = invoked module or script
            prog = os.path.basename(sys.argv[0]) or "program"
            shell = self._read_opt_value(argv, "--shell")
            if not shell:
                self._error("Gunakan --shell [bash|zsh|fish] bersama --generate-completion")
            spec = self._completion_spec()
            print(generate_completion(spec, shell=shell, prog=prog))
            raise SystemExit(0)

        if argv[0] in self.subcommands:
            return self._parse_with_merge(self.subcommands[argv[0]], argv[1:], subname=argv[0])
        return self._parse_with_merge(None, argv)

    def _parse_with_merge(self, sub, argv, subname=None):
        # 1) start with defaults
        values = {name: a.default for name, a in (sub.arguments if sub else self.arguments).items()}

        # 2) config file (from argv, then merge)
        cfg_path = self._read_opt_value(argv, "--config")
        if cfg_path:
            cfg = load_config(cfg_path)
            values = deep_merge(values, self._coerce_from_mapping(cfg, sub))

        # 3) env
        env_map = self._load_env(subname)
        values = deep_merge(values, env_map)

        # 4) CLI tokens
        cli_map, positional = self._parse_tokens(argv, (sub.arguments if sub else self.arguments))
        values = deep_merge(values, cli_map)
        values["_positional"] = positional
        if subname:
            values["_subcommand"] = subname

        # 5) required check
        for name, arg in (sub.arguments if sub else self.arguments).items():
            if arg.required and values.get(name) in (None, [], False, ""):
                self._error(f"--{name} wajib diisi")

        return values

    def _parse_tokens(self, argv, space_args):
        values, i, positional = {}, 0, []
        def match(tok):
            for name, a in space_args.items():
                if tok == f"--{name}" or (a.short and tok == f"-{a.short}"):
                    return a
            return None

        while i < len(argv):
            tok = argv[i]
            if tok in ("-h","--help"):
                # space-aware help
                if space_args is self.arguments: self.print_help()
                else: self.print_sub_help(values.get("_subcommand",""))
                raise SystemExit(0)
            if tok == "--generate-completion":
                # handled earlier
                i += 1; continue
            if tok == "--config":
                i += 2; continue
            if tok == "--shell":
                i += 2; continue

            arg = match(tok)
            if arg:
                if arg.takes_value:
                    # support --name=value
                    if "=" in tok and tok.startswith("--"):
                        raw = tok.split("=",1)[1]
                        i += 1
                    else:
                        if i+1 >= len(argv): self._error(f"{tok} memerlukan nilai")
                        raw = argv[i+1]; i += 2
                    # handle nargs
                    if arg.nargs in (None, 1):
                        values[arg.name] = arg.convert(raw)
                    else:
                        count, items = self._collect_nargs(argv, i, arg.nargs)
                        i += count
                        values[arg.name] = arg.convert(items)
                else:
                    values[arg.name] = True
                    i += 1
            elif tok.startswith("--") and "=" in tok:
                name, raw = tok[2:].split("=",1)
                if name in space_args:
                    values[name] = space_args[name].convert(raw)
                i += 1
            elif tok.startswith("-") and len(tok) > 2:  # short cluster: -abc
                # treat as individual flags (all must be non-value)
                for ch in tok[1:]:
                    found = None
                    for a in space_args.values():
                        if a.short == ch:
                            found = a; break
                    if not found: self._error(f"flag -{ch} tidak dikenal")
                    if found.takes_value: self._error(f"-{ch} memerlukan nilai, tidak bisa cluster")
                    values[found.name] = True
                i += 1
            else:
                positional.append(tok); i += 1
        return values, positional

    def _collect_nargs(self, argv, start, nargs):
        if isinstance(nargs, int):
            if start + nargs > len(argv): self._error(f"memerlukan {nargs} nilai")
            return nargs, argv[start:start+nargs]
        vals = []
        i = start
        if nargs in ("+","*"):
            while i < len(argv) and not argv[i].startswith("-"):
                vals.append(argv[i]); i += 1
            if nargs == "+" and not vals: self._error("memerlukan >=1 nilai")
            return i-start, vals
        if nargs == "?":
            if i < len(argv) and not argv[i].startswith("-"):
                return 1, [argv[i]]
            return 0, []
        self._error("nargs tidak valid")

    def _read_opt_value(self, argv, name):
        if name in argv:
            idx = argv.index(name)
            if idx+1 >= len(argv): self._error(f"{name} memerlukan nilai")
            return argv[idx+1]
        for t in argv:
            if t.startswith(name+"="):
                return t.split("=",1)[1]
        return None

    def _coerce_from_mapping(self, mapping, sub):
        # mapping: {name: value}
        space_args = sub.arguments if sub else self.arguments
        out = {}
        for name, raw in mapping.items():
            if name in space_args:
                a = space_args[name]
                if a.nargs not in (None,1) and not isinstance(raw, list):
                    raw = [raw]
                out[name] = a.convert(raw)
        return out

    def _load_env(self, subname):
        space = self.arguments if not subname else self.subcommands[subname].arguments
        out = {}
        for name, a in space.items():
            key = env_key(self.env_prefix + (f"_{subname}" if subname else ""), name)
            if key in os.environ:
                raw = os.environ[key]
                if a.nargs not in (None,1):
                    raw = raw.split(",")
                out[name] = a.convert(raw)
        return out

    def _completion_spec(self):
        def opts(space):
            L=[]
            for n,a in space.items():
                L.append(f"--{n}")
                if a.short: L.append(f"-{a.short}")
            # built-ins commonly useful:
            L.extend(["--help","-h","--config","--generate-completion","--shell"])
            return L
        subs = {name: [f"--{n}" for n in s.arguments] for name, s in self.subcommands.items()}
        return {"options": opts(self.arguments), "subcommands": subs}

    def _error(self, msg):
        print(C.c("Error:", C.RED), msg)
        raise ParseError(msg)

    # HELP
    def print_help(self):
        print(C.c("Usage:", C.CYAN), "program [options] [subcommand]")
        if self.description:
            print("\n" + wrap(self.description, 90))
        if self.arguments:
            print("\n" + C.c("Options:", C.YELLOW))
            for n,a in self.arguments.items():
                s = f"  {(('-'+a.short+', ') if a.short else '    ')}--{n}"
                if a.takes_value: s += f" <{a.metavar}>"
                extra=[]
                if a.default not in (None, False, [], ""): extra.append(f"default={a.default}")
                if a.choices: extra.append(f"choices={a.choices}")
                if a.nargs not in (None,1): extra.append(f"nargs={a.nargs}")
                print(s + (f"  [{', '.join(extra)}]" if extra else ""))
                if a.help: print(" " * 8 + wrap(a.help, 88, indent=8))
        if self.subcommands:
            print("\n" + C.c("Subcommands:", C.MAGENTA))
            for n,s in self.subcommands.items():
                print(f"  {n:12} {s.description}")

    def print_sub_help(self, subname):
        s = self.subcommands[subname]
        print(C.c(f"Usage: program {subname} [options]", C.CYAN))
        if s.description: print(wrap(s.description, 90))
        if s.arguments:
            print("\n" + C.c("Options:", C.YELLOW))
            for n,a in s.arguments.items():
                line = f"  {(('-'+a.short+', ') if a.short else '    ')}--{n}"
                if a.takes_value: line += f" <{a.metavar}>"
                extra=[]
                if a.default not in (None, False, [], ""): extra.append(f"default={a.default}")
                if a.choices: extra.append(f"choices={a.choices}")
                if a.nargs not in (None,1): extra.append(f"nargs={a.nargs}")
                print(line + (f"  [{', '.join(extra)}]" if extra else ""))
                if a.help: print(" " * 8 + wrap(a.help, 88, indent=8))
