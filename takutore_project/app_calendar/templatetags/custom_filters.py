from django import template

register = template.Library()

@register.filter
def dictkey(d, key):
    return d.get(key, [])

@register.filter
def lookup(d, key):
    return d.get(key, [])

@register.filter
def slice_list(value, chunk_size):
    """リストを chunk_size ごとのリストに分割する"""
    chunk_size = int(chunk_size)
    return [value[i:i+chunk_size] for i in range(0, len(value), chunk_size)]