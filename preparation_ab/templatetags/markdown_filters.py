
import markdown
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="render_markdown")
def render_markdown(value):
    if not value:
        return ""

    # Escape HTML first to prevent unsafe HTML injection.
    safe_text = escape(str(value))

    # Convert Markdown formatting into HTML.
    html = markdown.markdown(
        safe_text,
        extensions=["fenced_code", "tables"],
    )

    return mark_safe(html)
