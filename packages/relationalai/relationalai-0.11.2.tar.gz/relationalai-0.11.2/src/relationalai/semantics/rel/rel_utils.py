"""
Helpers to generate Rel, many taken from the original PyRel implementation.
"""
from __future__ import annotations
import re
from relationalai.semantics.metamodel import ir, types, factory as f

# Rel primitive relations used by the compiler
# TODO: how to deal with varargs?
RelPrimitiveOuterJoin = f.relation("rel_primitive_outer_join", [])

# List of higher order relations in Rel
HIGHER_ORDER = set([
    "::std::common::count",
    "::std::common::sum",
    "::std::common::mean",
    "::std::common::max",
    "::std::common::min",
    "::std::common::sort",
    "::std::common::reverse_sort",
    "::std::common::top",
    "::std::common::bottom",
])

# Mappings of IR operators to the equivalent in Rel
OPERATORS = {
    # binary
    # TODO: maybe add the binary operators

    # aggregates
    "count": "pyrel_count",
    "sum": "::std::common::sum",
    "avg": "::std::common::mean",
    "max": "::std::common::max",
    "min": "::std::common::min",

    # std
    "range": "::std::common::range",
    "hash": "rel_primitive_hash_tuple_uint128",
    "uuid_to_string": "::std::common::uuid_string",

    # dates
    "date_year": "::std::common::date_year",
    "date_month": "::std::common::date_month",
    "date_week": "::std::common::date_week",
    "date_day": "::std::common::date_day",
    "date_add": "::std::common::date_add",
    "date_subtract": "::std::common::date_subtract",
    "dates_period_days": "pyrel_dates_period_days",
    "datetimes_period_milliseconds": "pyrel_datetimes_period_milliseconds",
    "datetime_add": "::std::common::datetime_add",
    "datetime_week": "::std::common::datetime_week",
    "datetime_subtract": "::std::common::datetime_subtract",
    "construct_datetime_ms_tz": "::std::common::^DateTime",
    "date_format": "::std::common::format_date",
    "datetime_format": "::std::common::format_datetime",
    "construct_date_from_datetime": "::std::common::^Date",

    # periods
    "millisecond": "::std::common::^Millisecond",
    "second": "::std::common::^Second",
    "minute": "::std::common::^Minute",
    "hour": "::std::common::^Hour",
    "day": "::std::common::^Day",
    "week": "::std::common::^Week",
    "month": "::std::common::^Month",
    "year": "::std::common::^Year",

    # math
    "abs": "::std::common::abs",
    "natural_log": "::std::common::natural_log",
    "sqrt": "std::common::sqrt",
    "maximum": "::std::common::maximum",
    "minimum": "::std::common::minimum",
    "//": "::std::common::trunc_divide",
    "isinf": "::std::common::Infinity",
    "isnan": "::std::common::NaN",
    "ceil": "::std::common::ceil",
    "floor": "::std::common::floor",
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

    # strings
    "string": "::std::common::string",
    "concat": "::std::common::concat",
    "starts_with": "::std::common::starts_with",
    "ends_with": "::std::common::ends_with",
    "contains": "::std::common::contains",
    "substring": "::std::common::substring",
    "num_chars": "pyrel_num_chars",
    "like_match": "::std::common::like_match",
    "lower": "::std::common::lowercase",
    "upper": "::std::common::uppercase",
    "strip": "rel_primitive_trim",
    "levenshtein": "rel_primitive_levenshtein",
    "replace": "rel_primitive_replace",
    "split": "::std::common::string_split",
    "split_part": "::std::common::string_split",
    "regex_match": "rel_primitive_regex_match",

    # ints
    "parse_int64": "::std::common::parse_int",
    "parse_int128": "::std::common::parse_int128",

    # floats
    "parse_float": "::std::common::parse_float",

    # pragmas
    "rule_reasoner_sem_vo": "rel_primitive_force_faq_var_order",
    "rule_reasoner_phys_vo": "rel_primitive_force_var_order",
}

def rel_operator(ir_op):
    """ Maps an operator from the metamodel IR into the equivalent Rel operator. """
    if ir_op in OPERATORS:
        return OPERATORS[ir_op]
    else:
        return ir_op

def rel_typename(ir_type: ir.Type):
    """ Get the name of the type to use in Rel. """
    if isinstance(ir_type, ir.DecimalType):
        return f'pyrel_Decimal_{ir_type.precision}_{ir_type.scale}'
    if isinstance(ir_type, ir.ScalarType):
        if ir_type == types.Sha1:
            return 'Sha1'
        elif ir_type == types.Enum:
            return '::std::common::UInt128'
        elif ir_type == types.EntityTypeVar:
            return '::std::common::UInt128'
        elif ir_type == types.Hash:
            return "::std::common::UInt128"
        elif ir_type == types.UInt128:
            return '::std::common::UInt128'
        elif ir_type == types.RowId:
            return '::std::common::UInt128'
        elif ir_type == types.Bool:
            return '::std::common::Boolean'
        elif types.is_builtin(ir_type):
            return f'::std::common::{ir_type.name}'
        elif ir_type.super_types:
            # assuming the compiler narrowed this down somehow
            return rel_typename(ir_type.super_types.some())
        else:
            # user-defined types without a super type are user defined entities
            return '::std::common::UInt128'
    else:
        # TODO: how should we deal with Union types here?
        return '::std::common::Any'

# SEE: REL:      https://docs.relational.ai/rel/ref/lexical-symbols#keywords
#      CORE REL: https://docs.google.com/document/d/12LUQdRed7P5EqQI1D7AYG4Q5gno9uKqy32i3kvAWPCA
RESERVED_WORDS = [
    "and",
    "as",
    "bound",
    "declare",
    "def",
    "else",
    "end",
    "entity",
    "exists",
    "false",
    "for",
    "forall",
    "from",
    "ic",
    "if",
    "iff",
    "implies",
    "in",
    "module",
    "namespace",
    "not",
    "or",
    "requires",
    "then",
    "true",
    "use",
    "where",
    "with",
    "xor"
]

rel_sanitize_re = re.compile(r'[^\w:\[\]\^" ,]|^(?=\d)', re.UNICODE)
unsafe_symbol_pattern = re.compile(r"[^a-zA-Z0-9_]", re.UNICODE)

def sanitize(input_string, is_rel_name_or_symbol = False):
    # Replace non-alphanumeric characters with underscores
    if is_rel_name_or_symbol and "[" in input_string:
        string_parts = input_string.split('[', 1)
        sanitized_name_or_symbol = sanitize_identifier(string_parts[0])
        sanitized_rest = re.sub(rel_sanitize_re, "_", string_parts[1])
        sanitized = f"{sanitized_name_or_symbol}[{sanitized_rest}"
    else:
        if "::" in input_string: # TODO: This is a temp solution to avoid sanitizing the namespace
            sanitized = re.sub(rel_sanitize_re, "_", input_string)
        else:
            sanitized = sanitize_identifier(input_string)

    # Check if the resulting string is a keyword and append an underscore if it is
    if sanitized in RESERVED_WORDS:
        sanitized += "_"

    return sanitized

def sanitize_identifier(name: str) -> str:
    """
    Return a string safe to use as a top level identifier in rel, such as a variable or relation name.

    Args:
        name (str): The input identifier string.

    Returns:
        str: The sanitized identifier string.
    """

    if not name:
        return name

    safe_name = ''.join(c if c.isalnum() else '_' for c in name)
    if safe_name[0].isdigit():
        safe_name = '_' + safe_name
    if  safe_name in RESERVED_WORDS:
        safe_name = safe_name + "_" # preferring the pythonic pattern of `from_` vs `_from`
    return safe_name
