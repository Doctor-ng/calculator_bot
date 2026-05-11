# services/math_logic.py

import re
import math

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
    expr = convert_superscript(raw.replace(" ", "").lower())
    
    # ===== FIX INVERSE INPUT FIRST =====

    # convert sin^-1(x) → asin(x)
    expr = re.sub(r"\bsin\^-1\(", "asin(", expr)
    expr = re.sub(r"\bcos\^-1\(", "acos(", expr)
    expr = re.sub(r"\btan\^-1\(", "atan(", expr)

    # convert unicode
    expr = expr.replace("sin⁻¹", "asin")
    expr = expr.replace("cos⁻¹", "acos")
    expr = expr.replace("tan⁻¹", "atan")
    
    # degree symbol
    expr = expr.replace("°", "") 

    # power
    expr = expr.replace("^", "**")

    # sqrt
    expr = re.sub(r"sqrt\((.*?)\)", r"math.sqrt(\1)", expr)

    
    # ===== INVERSE TRIG FIRST (IMPORTANT ORDER) =====
    
    # sin^-1(x) style
    expr = re.sub(r"\bsin\^-1\(([^()]*)\)", r"math.degrees(math.asin(\1))", expr)
    expr = re.sub(r"\bcos\^-1\(([^()]*)\)", r"math.degrees(math.acos(\1))", expr)
    expr = re.sub(r"\btan\^-1\(([^()]*)\)", r"math.degrees(math.atan(\1))", expr)
    
    # sin⁻¹(x)
    expr = expr.replace("sin⁻¹", "asin")
    expr = expr.replace("cos⁻¹", "acos")
    expr = expr.replace("tan⁻¹", "atan")
    
    # asin(x)
    expr = re.sub(r"\basin\(([^()]*)\)", r"math.degrees(math.asin(\1))", expr)
    expr = re.sub(r"\bacos\(([^()]*)\)", r"math.degrees(math.acos(\1))", expr)
    expr = re.sub(r"\batan\(([^()]*)\)", r"math.degrees(math.atan(\1))", expr)
    
    # ===== NORMAL TRIG =====
    expr = re.sub(r"\bsin\(([^()]*)\)", r"math.sin(math.radians(\1))", expr)
    expr = re.sub(r"\bcos\(([^()]*)\)", r"math.cos(math.radians(\1))", expr)
    expr = re.sub(r"\btan\(([^()]*)\)", r"math.tan(math.radians(\1))", expr)
    
    expr = re.sub(r"\bcosec\(([^()]*)\)", r"(1/math.sin(math.radians(\1)))", expr)
    expr = re.sub(r"\bsec\(([^()]*)\)", r"(1/math.cos(math.radians(\1)))", expr)
    expr = re.sub(r"\bcot\(([^()]*)\)", r"(1/math.tan(math.radians(\1)))", expr)

   # ✅ SAFE CHAR CHECK (ALLOW math)
    if not re.fullmatch(r"[0-9+\-*/().a-z]+", expr):
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


    # ===== EVALUATE =====
    try:
       res = eval(expr, {"__builtins__": None}, {"math": math})

       if isinstance(res, float):
          formatted = f"{res:,.10f}".rstrip("0").rstrip(".")
       else:
          formatted = f"{res:,}"

       return f"<b>{raw}</b> = <code>{formatted}</code>"

    except Exception as e:
     print("MATH ERROR:", e)
    return None