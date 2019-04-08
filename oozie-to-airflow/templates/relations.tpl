{% for relation in relations %}
{{ relation.from_name }}.set_downstream({{ relation.to_name }})
{% endfor %}