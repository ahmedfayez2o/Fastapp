from django import template

register = template.Library()

@register.filter
def length_is(value, arg):
    """
    Returns a boolean of whether the value's length is the argument.
    Usage:
        {% if my_list|length_is:"3" %}
        {% endif %}
    """
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False 