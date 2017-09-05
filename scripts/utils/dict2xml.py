# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 18:05:29 2017

@author: user
"""

from xml.etree import ElementTree
import os

def dict_to_xml(dict_, parent_node=None, parent_name=''):
    def node_for_value(name, value, parent_node, parent_name):
        """
        creates the <li><input><label>...</label></input></li> elements.
        returns the <li> element.
        """
        value= os.path.join(parent_name, value)
        node= ElementTree.SubElement(parent_node, 'li')
        child= ElementTree.SubElement(node, 'input')
        child.set('type', 'checkbox')
        child.set('id', value)
        child= ElementTree.SubElement(child, 'label')
        child.set('for', value)
        child.text= name
        return node

    # create an <ul> element to hold all child elements
    if parent_node is None:
        node= ElementTree.Element('ul')
        node.set('id', 'master')
    else:
        node= ElementTree.SubElement(parent_node, 'ul')

    # add the sub-elements
    for key,value in dict_.items():
        if isinstance(value, dict):
            child= node_for_value(key, key, node, parent_name)
            dict_to_xml(value, child, key)
        else:
            node_for_value(key, value, node, parent_name)
    return node



my_dict ={'Desktop': {'bar': {'buz': '/home/michael/t/Desktop/bar/buz',
                     'fuz': '/home/michael/t/Desktop/bar/fuz'},
             'foo': {'buz': '/home/michael/t/Desktop/foo/buz',
                     'fuz': '/home/michael/t/Desktop/foo/fuz'}},
 'Documents': {'bar': {'buz': '/home/michael/t/Documents/bar/buz',
                       'fuz': '/home/michael/t/Documents/bar/fuz'},
               'foo': {'buz': '/home/michael/t/Documents/foo/buz',
                       'fuz': '/home/michael/t/Documents/foo/fuz'},
               'good title': '/home/michael/t/Documents/good title'},
 'test.py': '/home/michael/t/test.py'}
    
element= dict_to_xml(my_dict)

from xml.dom import minidom

xml= ElementTree.tostring(element)
xml= minidom.parseString(xml)
xml= xml.toprettyxml(indent='  ')