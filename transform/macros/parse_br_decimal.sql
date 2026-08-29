{#
  Brazilian-locale decimal string -> DOUBLE. Mirrors etl/silver.py's Python
  version from the pre-dbt pipeline: strip any thousands dot defensively,
  swap the decimal comma for a dot, TRY_CAST (never errors the model run —
  a genuine parse failure surfaces as a NULL, which the not_null schema
  tests on each staging model would catch).

  Handles the one non-obvious case in this data: rare scientific notation
  with a comma decimal, e.g. "4,0000000000000001E-2" -> "4.0000000000000001E-2"
  -> 0.04, which DuckDB's float parser accepts natively once the comma is a dot.
#}
{% macro parse_br_decimal(column_expr) %}
    try_cast(replace(replace({{ column_expr }}, '.', ''), ',', '.') as double)
{% endmacro %}
