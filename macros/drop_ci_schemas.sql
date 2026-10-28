{# Usage: dbt run-operation drop_ci_schemas --args '{prefix: CI_PR_12}' --target ci #}
{% macro drop_ci_schemas(prefix) %}
  {% set rows = run_query("select schema_name from " ~ target.database ~ ".information_schema.schemata").rows %}
  {% for row in rows %}
    {% if row[0].startswith(prefix | upper ~ '_') %}
      {% do run_query("drop schema if exists " ~ target.database ~ "." ~ row[0] ~ " cascade") %}
      {{ log("dropped " ~ row[0], info=True) }}
    {% endif %}
  {% endfor %}
{% endmacro %}
