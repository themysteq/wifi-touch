# -*- coding: utf-8 -*-
__author__ = 'mysteq'
from django import template

register = template.Library()


@register.filter(name='get_dot_key')
def get_dot_key(value, arg):
    return value.get(arg, None)