from relationalai.semantics.metamodel.types import digits_to_bits
from relationalai.semantics.lqp import ir as lqp
from relationalai.semantics.lqp.types import is_numeric
from relationalai.semantics.lqp.utils import UniqueNames
from relationalai.semantics.lqp.constructors import mk_primitive, mk_specialized_value, mk_type, mk_value, mk_var

rel_to_lqp = {
    "=": "rel_primitive_eq",
    "!=": "rel_primitive_neq",
    "%": "rel_primitive_remainder",
    "abs": "rel_primitive_abs",
    "ceil": "rel_primitive_round_up",
    "floor": "rel_primitive_round_down",
    "pow": "rel_primitive_power",
    "cbrt": "rel_primitive_cbrt",
    "factorial": "rel_primitive_factorial",
    "cos": "rel_primitive_cos",
    "cosh": "rel_primitive_cosh",
    "acos": "rel_primitive_acos",
    "acosh": "rel_primitive_acosh",
    "sin": "rel_primitive_sin",
    "sinh": "rel_primitive_sinh",
    "asin": "rel_primitive_asin",
    "asinh": "rel_primitive_asinh",
    "construct_date": "rel_primitive_construct_date",
    "construct_date_from_datetime": "rel_primitive_datetime_date_convert",
    "construct_datetime": "rel_primitive_construct_datetime",
    "construct_datetime_ms_tz": "rel_primitive_construct_datetime",
    "hash": "rel_primitive_hash_tuple_uint128",
    "uuid_to_string": "rel_primitive_uuid_string",
    "parse_date": "rel_primitive_parse_date",
    "parse_datetime": "rel_primitive_parse_datetime",
    "parse_decimal": "rel_primitive_parse_decimal",
    "parse_int64": "rel_primitive_parse_int",
    "parse_int128": "rel_primitive_parse_int128",
    "parse_float": "rel_primitive_parse_float",
    "string": "rel_primitive_string",
    "starts_with": "rel_primitive_starts_with",
    "ends_with": "rel_primitive_ends_with",
    "contains": "rel_primitive_contains",
    "num_chars": "rel_primitive_num_chars",
    "substring": "rel_primitive_substring",
    "like_match": "rel_primitive_like_match",
    "lower": "rel_primitive_lowercase",
    "upper": "rel_primitive_uppercase",
    "concat": "rel_primitive_concat",
    "replace": "rel_primitive_replace",
    "strip": "rel_primitive_trim",
    "date_year": "rel_primitive_date_year",
    "date_month": "rel_primitive_date_month",
    "date_week": "rel_primitive_date_week",
    "date_day": "rel_primitive_date_day",
    "date_add": "rel_primitive_typed_add_date_period",
    "date_subtract": "rel_primitive_typed_subtract_date_period",
    "dates_period_days": "rel_primitive_date_days_between",
    "datetime_add": "rel_primitive_typed_add_datetime_period",
    "datetime_subtract": "rel_primitive_typed_subtract_datetime_period",
    "datetime_week": "rel_primitive_datetime_week",
    "datetimes_period_milliseconds": "rel_primitive_datetime_milliseconds_between",
    "date_format": "rel_primitive_format_date",
    "datetime_format": "rel_primitive_format_datetime",
    "range": "rel_primitive_range",
    "natural_log": "rel_primitive_natural_log",
    "sqrt": "rel_primitive_sqrt",
    "isinf": "rel_primitive_isinf",
    "isnan": "rel_primitive_isnan",
    # Division is monotype, but only on the input args. Until we distinguish between input
    # and output args, we can't use the same assertions for monotype-ness as the other ops.
    "/": "rel_primitive_divide_monotype",
    "levenshtein": "rel_primitive_levenshtein",
    "split": "rel_primitive_string_split",
    "split_part": "rel_primitive_string_split",
    "regex_match": "rel_primitive_regex_match",
}

primitive_type_reorderings = {
    "rel_primitive_like_match": [1, 0],
}

agg_to_lqp = {
    "min": "rel_primitive_min",
    "max": "rel_primitive_max",
    "sum": "rel_primitive_add_monotype",
    "count": "rel_primitive_add_monotype", # count is a sum of 1s
    "rel_primitive_solverlib_ho_appl": "rel_primitive_solverlib_ho_appl",
}

rel_to_lqp_monotype = {
    "+": "rel_primitive_add_monotype",
    "-": "rel_primitive_subtract_monotype",
    "*": "rel_primitive_multiply_monotype",
    "<=": "rel_primitive_lt_eq_monotype",
    ">=": "rel_primitive_gt_eq_monotype",
    ">": "rel_primitive_gt_monotype",
    "<": "rel_primitive_lt_monotype",
    "//": "rel_primitive_trunc_divide_monotype",
    "maximum": "rel_primitive_max",
    "minimum": "rel_primitive_min",
}

# Insert extra terms where a raicode primitive expects more terms, and there are possible
# defaults.
def _extend_primitive_terms(name: str, terms: list[lqp.RelTerm], term_types: list[lqp.Type]) -> tuple[list[lqp.RelTerm], list[lqp.Type]]:
    if name == "rel_primitive_construct_datetime" and len(terms) == 7:
        # construct_datetime does not provide a timezone or milliseconds so we
        # default to 0 milliseconds and UTC timezone.
        terms = [*terms[:-1], mk_value(0), mk_value("UTC"), terms[-1]]
        term_types = [
            *term_types[:-1],
            mk_type(lqp.TypeName.INT),
            mk_type(lqp.TypeName.STRING),
            term_types[-1],
        ]

    elif name == "rel_primitive_parse_decimal" and len(terms) == 2:
        assert term_types
        py_precision = term_types[1].parameters[0].value
        bit_value = mk_value(digits_to_bits(py_precision))
        precision_value = mk_value(term_types[1].parameters[1].value)
        terms = [
            mk_specialized_value(bit_value),
            mk_specialized_value(precision_value),
            terms[0],
            terms[1],
        ]
        term_types = [mk_type(lqp.TypeName.INT), mk_type(lqp.TypeName.INT), *term_types]

    return (terms, term_types)

# Reorder terms where the raicode primitive expects them in a different order.
def _reorder_primitive_terms(name: str, terms: list[lqp.RelTerm], term_types: list[lqp.Type]) -> tuple[list[lqp.RelTerm], list[lqp.Type]]:
    reordering = primitive_type_reorderings.get(name, None)
    if reordering:
        assert len(terms) == len(reordering), \
            f"Primitive {name} expected {len(reordering)} terms, got {len(terms)}"
        return ([terms[i] for i in reordering], [term_types[i] for i in reordering])

    return (terms, term_types)

# Check that the primitive terms have the expected types.
# TODO: Fill out for all primitives, or rely on server-side type checking?
def _assert_primitive_terms(name: str, terms: list[lqp.RelTerm], term_types: list[lqp.Type]):
    if is_monotype(name):
        # Make sure that the input terms have the same types
        assert term_types.count(term_types[0]) == len(term_types), \
            f"Expected all terms to have the same type for monotype operator " \
            f"`{name}` but got {term_types} for terms {terms}"
    elif name == "=":
        # Allowed types are monotype, or both number types
        monotype = term_types[0] == term_types[1]
        numeric = is_numeric(term_types[0]) and is_numeric(term_types[1])
        assert monotype or numeric, \
            f"Expected types of `=`to be comparable but got `{[t.type_name for t in term_types]}`"

def build_primitive(
    name: str,
    terms: list[lqp.RelTerm],
    term_types: list[lqp.Type]
) -> lqp.Formula:
    lqp_name = relname_to_lqp_name(name)
    terms, term_types = _extend_primitive_terms(lqp_name, terms, term_types)
    terms, term_types = _reorder_primitive_terms(lqp_name, terms, term_types)
    _assert_primitive_terms(lqp_name, terms, term_types)

    return mk_primitive(lqp_name, terms)

def relname_to_lqp_name(name: str) -> str:
    if name in rel_to_lqp:
        return rel_to_lqp[name]
    elif name in rel_to_lqp_monotype:
        return rel_to_lqp_monotype[name]
    else:
        # If we don't have a mapping for the built-in, we just pass it through as-is.
        return name

def is_monotype(name: str) -> bool:
    return name in rel_to_lqp_monotype

# We take the name and type of the variable that we're summing over, so that we can generate
# recognizable names for the variables in the reduce operation and preserve the type.
def lqp_avg_op(names: UniqueNames, op_name: str, sum_name: str, sum_type: lqp.Type) -> lqp.Abstraction:
    count_type = mk_type(lqp.TypeName.INT)
    vars = [
        (mk_var(names.get_name(sum_name)), sum_type),
        (mk_var(names.get_name("counter")), count_type),
        (mk_var(names.get_name(sum_name)), sum_type),
        (mk_var(names.get_name("one")), count_type),
        (mk_var(names.get_name("sum")), sum_type),
        (mk_var(names.get_name("count")), count_type),
    ]

    x1 = vars[0][0]
    x2 = vars[1][0]
    y1 = vars[2][0]
    y2 = vars[3][0]
    sumv = vars[4][0]
    count = vars[5][0]

    body = lqp.Conjunction(
        args=[
            mk_primitive("rel_primitive_add_monotype", [x1, y1, sumv]),
            mk_primitive("rel_primitive_add_monotype", [x2, y2, count])
        ],
        meta=None
    )
    return lqp.Abstraction(vars=vars, value=body, meta=None)

# Default handler for aggregation operations in LQP.
def lqp_agg_op(names: UniqueNames, op_name: str, aggr_arg_name: str, aggr_arg_type: lqp.Type) -> lqp.Abstraction:
    x = mk_var(names.get_name(f"x_{aggr_arg_name}"))
    y = mk_var(names.get_name(f"y_{aggr_arg_name}"))
    z = mk_var(names.get_name(f"z_{aggr_arg_name}"))
    ts = [(x, aggr_arg_type), (y, aggr_arg_type), (z, aggr_arg_type)]

    name = agg_to_lqp.get(op_name, op_name)
    body = mk_primitive(name, [x, y, z])

    return lqp.Abstraction(vars=ts, value=body, meta=None)

def lqp_operator(names: UniqueNames, op_name: str, aggr_arg_name: str, aggr_arg_type: lqp.Type) -> lqp.Abstraction:
    # TODO: Can we just pass through unknown operations?
    if op_name not in agg_to_lqp:
        raise NotImplementedError(f"Unsupported aggregation: {op_name}")

    return lqp_agg_op(names, op_name, aggr_arg_name, aggr_arg_type)
