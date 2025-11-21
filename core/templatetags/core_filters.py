from django import template

register = template.Library()


@register.filter(name='split')
def split(value, delimiter=','):
    """Split a string by delimiter and return a list"""
    if not value:
        return []
    return [item.strip() for item in str(value).split(delimiter) if item.strip()]


@register.filter(name='trim')
def trim(value):
    """Trim whitespace from a string"""
    if not value:
        return ''
    return str(value).strip()


