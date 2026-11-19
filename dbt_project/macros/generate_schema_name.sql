{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- elif custom_schema_name == 'staging' or custom_schema_name == 'intermediate' -%}
        talentflow_staging
    {%- elif custom_schema_name == 'analytics' -%}
        talentflow_analytics
    {%- else -%}
        talentflow_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
