{% macro datediff_days(end_date, start_date) %}
    {%- if target.type == 'bigquery' -%}
        date_diff(cast({{ end_date }} as date), cast({{ start_date }} as date), day)
    {%- else -%}
        datediff('day', cast({{ start_date }} as date), cast({{ end_date }} as date))
    {%- endif -%}
{% endmacro %}

{% macro date_trunc_month(date_col) %}
    {%- if target.type == 'bigquery' -%}
        date_trunc(cast({{ date_col }} as date), month)
    {%- else -%}
        date_trunc('month', cast({{ date_col }} as date))
    {%- endif -%}
{% endmacro %}

{% macro safe_cast_date(column_name) %}
    {%- if target.type == 'bigquery' -%}
        safe_cast({{ column_name }} as date)
    {%- else -%}
        try_cast({{ column_name }} as date)
    {%- endif -%}
{% endmacro %}
