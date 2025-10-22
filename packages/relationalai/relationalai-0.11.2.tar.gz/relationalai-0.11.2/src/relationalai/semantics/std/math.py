from __future__ import annotations

from relationalai.semantics.internal import internal as b
from .std import _Number, _make_expr

def abs(value: _Number) -> b.Expression:
    return _make_expr("abs", value, b.Number.ref("res"))

def natural_log(value: _Number) -> b.Expression:
    return _make_expr("natural_log", value, b.Number.ref("res"))

def sqrt(value: _Number) -> b.Expression:
    return _make_expr("sqrt", value, b.Float.ref("res"))

def maximum(left: _Number, right: _Number) -> b.Expression:
    return _make_expr("maximum", left, right, b.Number.ref("res"))

def minimum(left: _Number, right: _Number) -> b.Expression:
    return _make_expr("minimum", left, right, b.Number.ref("res"))

def isinf(value: _Number) -> b.Expression:
    return _make_expr("isinf", value)

def isnan(value: _Number) -> b.Expression:
    return _make_expr("isnan", value)

def ceil(value: _Number) -> b.Expression:
    return _make_expr("ceil", value, b.Number.ref("res"))

def floor(value: _Number) -> b.Expression:
    return _make_expr("floor", value, b.Number.ref("res"))

def pow(base: _Number, exponent: _Number) -> b.Expression:
    return _make_expr("pow", base, exponent, b.Float.ref("res"))

def cbrt(value: _Number) -> b.Expression:
    return _make_expr("cbrt", value, b.Float.ref("res"))

def factorial(value: _Number) -> b.Expression:
    return _make_expr("factorial", value, b.Number.ref("res"))

def cos(value: _Number) -> b.Expression:
    return _make_expr("cos", value, b.Float.ref("res"))

def cosh(value: _Number) -> b.Expression:
    return _make_expr("cosh", value, b.Float.ref("res"))

def acos(value: _Number) -> b.Expression:
    return _make_expr("acos", value, b.Float.ref("res"))

def acosh(value: _Number) -> b.Expression:
    return _make_expr("acosh", value, b.Float.ref("res"))

def sin(value: _Number) -> b.Expression:
    return _make_expr("sin", value, b.Float.ref("res"))

def sinh(value: _Number) -> b.Expression:
    return _make_expr("sinh", value, b.Float.ref("res"))

def asin(value: _Number) -> b.Expression:
    return _make_expr("asin", value, b.Float.ref("res"))

def asinh(value: _Number) -> b.Expression:
    return _make_expr("asinh", value, b.Float.ref("res"))
