from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='render_inline_blanks')
def render_inline_blanks(text, question_id):
    """
    Replace _____ with inline input fields for fill-in-the-blank questions
    """
    if not text:
        return text
    
    # Replace each occurrence of _____ with an input field
    # Using a counter to give unique names if there are multiple blanks
    counter = [0]
    
    def replace_blank(match):
        counter[0] += 1
        input_html = (
            f'<input type="text" '
            f'name="question_{question_id}{"_" + str(counter[0]) if counter[0] > 1 else ""}" '
            f'class="blank-input" '
            f'required '
            f'style="border: none; border-bottom: 2px solid #0d6efd; padding: 4px 8px; '
            f'min-width: 100px; text-align: center; font-size: 1em; '
            f'background: #f8f9fa; border-radius: 4px 4px 0 0; margin: 0 4px;">'
        )
        return input_html
    
    # Replace all occurrences of _____
    result = re.sub(r'_____+', replace_blank, text)
    
    return mark_safe(result)
