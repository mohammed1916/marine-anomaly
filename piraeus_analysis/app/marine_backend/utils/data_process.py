# marine_backend/utils/data_process.py
import math
import numbers


def sanitize_row(d: dict) -> dict:
    """
    Return JSON-safe copy of row.
    Converts NaN / inf (Python + NumPy) to None.
    """
    out = {}
    for k, v in d.items():
        # print("v: ", v)
        if isinstance(v, numbers.Real) and not math.isfinite(v):
            out[k] = None
        else:
            out[k] = v
    return out


