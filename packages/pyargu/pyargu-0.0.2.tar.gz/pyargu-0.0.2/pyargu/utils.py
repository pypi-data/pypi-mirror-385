def convert_type(value, type_func):
    try:
        return type_func(value)
    except Exception:
        raise ValueError(f"Gagal mengonversi '{value}' ke {type_func.__name__}")

def format_default(val):
    return f" (default: {val})" if val is not None else ""
