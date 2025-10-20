def generate_completion(spec, shell="bash", prog="program"):
    """
    spec: {
      "options": ["--verbose","-v","--output","-o","--count","-c", ...],
      "subcommands": {"convert": ["--input","-i","--format","-f"], ...}
    }
    """
    if shell == "bash":
        return _bash(spec, prog)
    if shell == "zsh":
        return _zsh(spec, prog)
    if shell == "fish":
        return _fish(spec, prog)
    raise ValueError("Shell tidak didukung")

def _bash(spec, prog):
    # minimal, cepat, dan cukup kuat
    lines = [f"""# bash completion for {prog}
_{prog}_complete() {{
    local cur prev words cword
    _init_completion -n : || return
    case ${{COMP_WORDS[1]}} in
"""]
    for sub, opts in spec["subcommands"].items():
        lines.append(f"""  {sub})
      COMPREPLY=( $(compgen -W "{' '.join(opts)}" -- "$cur") )
      return 0;;""")
    lines.append("""  *)
      COMPREPLY=( $(compgen -W "{opts} {subs}" -- "$cur") )
      return 0;;
    esac
}
complete -F _{prog}_complete {prog}
""".format(
        opts=" ".join(spec["options"]),
        subs=" ".join(spec["subcommands"].keys())
    ))
    return "\n".join(lines)

def _zsh(spec, prog):
    return f"""#compdef {prog}
_arguments -s \\
  {' '.join([f'"{opt}[option]":' for opt in spec["options"]])} \\
  {' '.join([f'"{sub}:subcommand:(({ " ".join(spec["subcommands"].keys()) }))"'
             for sub in ["subcmd"]])}
"""

def _fish(spec, prog):
    parts = [f"# fish completions for {prog}"]
    for opt in spec["options"]:
        parts.append(f"complete -c {prog} -s {opt[1:]} -l {opt[2:]} 2>/dev/null")
    for sub, opts in spec["subcommands"].items():
        parts.append(f"complete -c {prog} -n '__fish_use_subcommand' -a {sub}")
        for opt in opts:
            parts.append(f"complete -c {prog} -n '__fish_seen_subcommand_from {sub}' -l {opt[2:]}")
    return "\n".join(parts)
