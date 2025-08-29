from django import template

register = template.Library()

@register.filter
def isdigit(value):
    return str(value).isdigit()
