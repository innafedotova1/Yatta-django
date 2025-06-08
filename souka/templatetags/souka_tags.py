from django import template
import souka.views as views

register = template.Library()

def get_categories():
    return views.cats_db

@register.filter
def dict_get(d, key):
    return d.get(key, {})

@register.filter
def prev_chapter(chapters, current):
    chapters = list(chapters)
    try:
        index = chapters.index(current)
        return chapters[index - 1] if index > 0 else current
    except ValueError:
        return current
