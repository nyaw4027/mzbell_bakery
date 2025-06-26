from django import template

register = template.Library()

@register.filter
def add_mul(value, args):
    try:
        add_val, mul_val = map(int, args.split(','))
        return (int(value) + add_val) * mul_val
    except (ValueError, TypeError):
        return f"Error[{value}|{args}]"
