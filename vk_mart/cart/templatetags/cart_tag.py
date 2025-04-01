from django import template

register = template.Library()

@register.simple_tag
def sample_tag():
    return "This is a sample tag"


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0