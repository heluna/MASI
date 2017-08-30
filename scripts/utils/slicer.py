# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 14:23:43 2017

@author: Helen Kollai
"""

''' methods for slicing metadata string by relative position to characters'''


def between(value, a, b):
    pos_a = value.find(a, 0, len(value))  # Find and validate before-part.
    if pos_a == -1:
        return None
    pos_b = value.find(b)  # Find and validate after part.
    if pos_b == -1:
        return None
    adjusted_pos_a = pos_a + len(a)  # Return middle part.
    if adjusted_pos_a >= pos_b:
        return None
    return value[adjusted_pos_a:pos_b]


def before(value, a):
    pos_a = value.find(a)  # Find first part and return slice before it.
    if pos_a == -1:
        return None
    return value[0:pos_a]


def after(value, a):
    pos_a = value.rfind(a)  # Find and validate first part.
    if pos_a == -1:
        return None
    adjusted_pos_a = pos_a + len(a)    # Returns chars after the found string.
    if adjusted_pos_a >= len(value):
        return None
    return value[adjusted_pos_a:]


def splitString(value, a):
    parts = value.split(a)  # split string by delimiting string/character
    return parts
