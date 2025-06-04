# hadith_app/templatetags/hadith_extras.py
from django import template
import pprint # Make sure this is imported

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key)) 
    return None

@register.filter(name='pprint')
def pretty_print(value):
    return pprint.pformat(value)

@register.filter(name='get_hadith_border_class')
def get_hadith_border_class(grades_list):
    default_border = "border-gray-300 dark:border-gray-600"
    if not grades_list:
        return default_border
    grade_hierarchy = [
        ('Mawdu', "border-red-600"), ('Very Daif', "border-red-500"), 
        ('Daif', "border-orange-500"), ('Sahih Lighairihi', "border-yellow-500"), 
        ('Hasan', "border-blue-500"), ('Hasan Sahih', "border-green-500"), 
        ('Sahih', "border-green-500"),
    ]
    for grade_text, css_class in grade_hierarchy:
        for grade_obj in grades_list:
            if isinstance(grade_obj, dict) and grade_obj.get('grade') == grade_text:
                return css_class
    return default_border