# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 15:33:24 2017
@author: H.Kollai
"""

# create symbolic links to files in separate folder
# requires local administrator rights in windows environment


import os
from glob import glob


def createSymLink():
    try:
        for src_path in glob('src/*'):
            os.symlink(os.path.relpath(src_path, 'dst/'),
                       os.path.join('dst', os.path.basename(src_path)))
        print("Symbolic Links sucessfully created")
    except RuntimeError as e:
        print("Fehler:", e)
