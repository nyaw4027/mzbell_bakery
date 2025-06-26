from django import template

register = template.Library()

@register.filter
def add_mul(value, arg):
    """
    Usage: {{ value|add_mul:'1,150' }} -> (value + 1) * 150
    """
    try:
        add_val, mul_val = map(int, arg.split(','))
        return (int(value) + add_val) * mul_val
    except:
        return value
