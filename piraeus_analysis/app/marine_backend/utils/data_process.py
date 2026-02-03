import math

def sanitize_row(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, float) and not math.isfinite(v):
            d[k] = None
    return d
