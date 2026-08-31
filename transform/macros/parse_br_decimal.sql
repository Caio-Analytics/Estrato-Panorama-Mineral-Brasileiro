{# Brazilian decimal string -> DOUBLE, incl. rare comma-decimal scientific notation #}
{% macro parse_br_decimal(column_expr) %}
    try_cast(replace(replace({{ column_expr }}, '.', ''), ',', '.') as double)
{% endmacro %}
