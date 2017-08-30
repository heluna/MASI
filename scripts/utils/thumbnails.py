# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 13:49:41 2017
@author: H.Kollai
"""
# create thumbnails for images

from PIL import Image
import os


def createThumb(image):
    '''Create thumbnails for images'''

    im = Image.open(image)
    size = (512, 512)
    filename, extension = os.path.splitext(image)
    output = filename + ".thumbnail"
    if image != output:
        try:
            im.thumbnail(size)
            im.save(output, "JPEG")
        except IOError:
                print("Failed to process " + input)