from django import template

register = template.Library()

@register.filter
def formato_telefono(value):
    """
    Formatea un teléfono como (XXX) XXX-XXXX
    """
    s = str(value)
    if len(s) == 10:
        return f"({s[:3]}) {s[3:6]}-{s[6:]}"

    if len(s) > 12:
        return f"[{s[:2]}] ({s[2:5]}) {s[5:8]}-{s[8:]}"

    return value
