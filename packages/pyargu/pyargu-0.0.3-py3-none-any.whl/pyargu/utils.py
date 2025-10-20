import json, os, shlex

def convert_type(value, type_func):
    if type_func is bool:
        if isinstance(value, bool): return value
        s = str(value).strip().lower()
        if s in ("1","true","yes","on"): return True
        if s in ("0","false","no","off"): return False
        raise ValueError(f"tidak bisa konversi '{value}' ke bool")
    if type_func is list:
        if isinstance(value, list): return value
        # dukung dipisah koma: "a,b,c"
        return [v for v in str(value).split(",") if v != ""]
    return type_func(value)

def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if text.startswith("{"):  # JSON
        return json.loads(text)
    # Fallback: k=v per baris (sangat sederhana)
    cfg = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg

def env_key(prefix: str, name: str) -> str:
    return f"{prefix}_{name.replace('-', '_').upper()}"

def wrap(s, width=80, indent=0):
    import textwrap
    return "\n".join(textwrap.wrap(s, width=width, subsequent_indent=" " * indent))

def shell_quote(s: str) -> str:
    return shlex.quote(str(s))