from flask import Flask, render_template, request, jsonify
import sympy as sp
import math

app = Flask(__name__)

x = sp.symbols('x')


def parse_function(expr: str):
    try:
        f_expr = sp.sympify(expr)
        f = sp.lambdify(x, f_expr, modules=["math"])
        return f_expr, f, None
    except Exception as e:
        return None, None, str(e)


def parse_derivative(expr: str):
    try:
        f_expr = sp.sympify(expr)
        df_expr = sp.diff(f_expr, x)
        df = sp.lambdify(x, df_expr, modules=["math"])
        return df_expr, df, None
    except Exception as e:
        return None, None, str(e)


def safe_number(val):
    if val is None:
        return None
    if isinstance(val, complex):
        if abs(val.imag) < 1e-12:
            return float(val.real)
        raise ValueError("Complex value encountered.")
    return float(val)


def bisection_method(f, a, b, tol=1e-6, max_iter=50):
    data = []
    fa = safe_number(f(a))
    fb = safe_number(f(b))

    if fa * fb > 0:
        return {"error": "For Bisection, f(a) and f(b) must have opposite signs."}

    prev_c = None
    c = None
    for i in range(1, max_iter + 1):
        c = (a + b) / 2.0
        fc = safe_number(f(c))
        error = abs(c - prev_c) if prev_c is not None else None

        data.append({
            "iter": i,
            "a": a,
            "b": b,
            "c": c,
            "f_c": fc,
            "error": error,
        })

        if abs(fc) < tol or (error is not None and error < tol):
            return {"root": c, "iterations": data}

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

        prev_c = c

    return {"root": c, "iterations": data}


def regula_falsi_method(f, a, b, tol=1e-6, max_iter=50):
    data = []
    fa = safe_number(f(a))
    fb = safe_number(f(b))

    if fa * fb > 0:
        return {"error": "For Regula-Falsi, f(a) and f(b) must have opposite signs."}

    prev_c = None
    c = None
    for i in range(1, max_iter + 1):
        denominator = (fb - fa)
        if denominator == 0:
            return {"error": "Division by zero encountered in Regula-Falsi."}
        c = (a * fb - b * fa) / denominator
        fc = safe_number(f(c))
        error = abs(c - prev_c) if prev_c is not None else None

        data.append({
            "iter": i,
            "a": a,
            "b": b,
            "c": c,
            "f_c": fc,
            "error": error,
        })

        if abs(fc) < tol or (error is not None and error < tol):
            return {"root": c, "iterations": data}

        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc

        prev_c = c

    return {"root": c, "iterations": data}


def newton_raphson_method(f, df, x0, tol=1e-6, max_iter=50):
    data = []

    for i in range(1, max_iter + 1):
        fx = safe_number(f(x0))
        dfx = safe_number(df(x0))

        if dfx == 0:
            return {"error": "Derivative became zero. Newton-Raphson failed."}

        x1 = x0 - fx / dfx
        error = abs(x1 - x0)

        data.append({
            "iter": i,
            "x_n": x0,
            "f_xn": fx,
            "df_xn": dfx,
            "x_next": x1,
            "error": error,
        })

        if error < tol:
            return {"root": x1, "iterations": data}

        x0 = x1

    return {"root": x0, "iterations": data}


def secant_method(f, x0, x1, tol=1e-6, max_iter=50):
    data = []

    for i in range(1, max_iter + 1):
        f0 = safe_number(f(x0))
        f1 = safe_number(f(x1))
        denominator = (f1 - f0)
        if denominator == 0:
            return {"error": "Division by zero in Secant method."}

        x2 = x1 - f1 * (x1 - x0) / denominator
        error = abs(x2 - x1)

        data.append({
            "iter": i,
            "x_n_minus_1": x0,
            "x_n": x1,
            "x_next": x2,
            "f_xn": f1,
            "error": error,
        })

        if error < tol:
            return {"root": x2, "iterations": data}

        x0, x1 = x1, x2

    return {"root": x1, "iterations": data}


def fixed_point_iteration(g, x0, tol=1e-6, max_iter=50):
    data = []

    for i in range(1, max_iter + 1):
        x1 = safe_number(g(x0))
        error = abs(x1 - x0)

        data.append({
            "iter": i,
            "x_n": x0,
            "x_next": x1,
            "error": error,
        })

        if error < tol:
            return {"root": x1, "iterations": data}

        x0 = x1

    return {"root": x0, "iterations": data}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json(force=True)
    method = data.get("method")
    expr = data.get("function", "").strip()
    tol = float(data.get("tolerance", 1e-6))
    max_iter = int(data.get("max_iter", 50))

    if not expr and method != "fixed_point":
        return jsonify({"error": "Please enter a valid function f(x)."})

    f_expr, f, err = parse_function(expr)
    if method != "fixed_point" and err:
        return jsonify({"error": f"Invalid function: {err}"})

    try:
        if method == "bisection":
            a = float(data["a"])
            b = float(data["b"])
            result = bisection_method(f, a, b, tol, max_iter)

        elif method == "regula_falsi":
            a = float(data["a"])
            b = float(data["b"])
            result = regula_falsi_method(f, a, b, tol, max_iter)

        elif method == "newton":
            x0 = float(data["x0"])
            _, df, derr = parse_derivative(expr)
            if derr:
                return jsonify({"error": f"Derivative error: {derr}"})
            result = newton_raphson_method(f, df, x0, tol, max_iter)

        elif method == "secant":
            x0 = float(data["x0"])
            x1 = float(data["x1"])
            result = secant_method(f, x0, x1, tol, max_iter)

        elif method == "fixed_point":
            g_expr = data.get("g_function", "").strip()
            if not g_expr:
                return jsonify({"error": "Please enter g(x) for Fixed Point Iteration."})
            _, g, gerr = parse_function(g_expr)
            if gerr:
                return jsonify({"error": f"Invalid g(x): {gerr}"})
            x0 = float(data["x0"])
            result = fixed_point_iteration(g, x0, tol, max_iter)
        else:
            return jsonify({"error": "Unsupported method selected."})

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
