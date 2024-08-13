from django import template

register = template.Library()


@register.filter
def remove_whitespace(value):
    """Remove all whitespace characters (newlines, tabs, etc.)"""
    if not isinstance(value, str):
        return value
    return " ".join(value.split())
