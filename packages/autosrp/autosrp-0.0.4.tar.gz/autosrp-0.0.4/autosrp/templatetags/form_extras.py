from django import template
register = template.Library()

@register.filter
def add_class(field, css):
    widget = field.field.widget
    attrs = widget.attrs.copy()
    existing = attrs.get('class', '')
    attrs['class'] = (existing + ' ' + css).strip()
    return field.as_widget(attrs=attrs)
