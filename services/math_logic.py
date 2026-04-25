# services/math_logic.py

import re

SUPERSCRIPT_MAP = {
    "²": "**2", "³": "**3", "⁴": "**4",
    "⁵": "**5", "⁶": "**6", "⁷": "**7",
    "⁸": "**8", "⁹": "**9", "¹⁰": "**10",
}


def convert_superscript(expr: str):
    for k, v in SUPERSCRIPT_MAP.items():
        expr = expr.replace(k, v)
    return expr


async def process_math(query: str):
    raw = query.strip()

    # -------- PERCENTAGE --------
    m = re.fullmatch(r"(\d+(?:\.\d+)?)%\s*of\s*(\d+(?:\.\d+)?)", raw, re.I)
    if m:
        p, n = map(float, m.groups())
        return f"<b>{p}% of {n} =</b> <code>{(p / 100) * n}</code>"

    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*is\s*%\s*of\s*(\d+(?:\.\d+)?)", raw, re.I)
    if m:
        a, b = map(float, m.groups())
        return f"<b>{a} is % of {b} =</b> <code>{(a / b) * 100:.2f}%</code>"

    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([↑↓])\s*(\d+(?:\.\d+)?)%", raw)
    if m:
        v, arrow, p = m.groups()
        v, p = float(v), float(p)
        res = v * (1 + p / 100) if arrow == "↑" else v * (1 - p / 100)
        return f"<b>{v} {arrow} {p}% =</b> <code>{res}</code>"

    # -------- NORMAL MATH --------
    expr = convert_superscript(raw.replace(" ", ""))

    if not re.fullmatch(r"[0-9+\-*/().]+", expr):
        return None

    if re.fullmatch(r"\d+(\.\d+)?", expr):
        return None

    if re.search(r"\d+\.$", expr):
        return None

    if re.match(r"^[+\-*/]", expr):
        return None

    match = re.search(r"\*\*(\d+)", expr)
    if match and int(match.group(1)) > 8:
        return None

    try:
        res = eval(expr, {"__builtins__": None}, {})
        return f"<b>{raw} =</b> <code>{res}</code>"
    except:
        return None