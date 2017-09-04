# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 12:11:07 2016

@author: Helen Kollai
"""
# -*- coding: utf-8 -*-

import os, sys
from urllib.request import urlopen
from bs4 import BeautifulSoup

# set path of project directory to import own modules
parentPath = os.path.abspath('..')
sys.path.insert(0, parentPath)
sys.path.append(os.path.abspath('.'))

from utils import slicer



''' method for for crawling metadata content from SLUB website'''


def readUrl(filename):
    url2open = "http://www.deutschefotothek.de/gallery/freitext/{0}"\
            .format(filename)  # join base URL with filename
    try:
        url = urlopen(url2open)  # open URL to map
        html_text_map = BeautifulSoup(url, "lxml")  # read content of html
    except Exception as e:
        print(e)
    finally:
        url.close()

    try:
        for links in html_text_map.select('div.listItemLeft a["href"]', limit=1):
            link = links['href']     # get URL to map metadata
        url_meta = urlopen(link[:-len(filename)])  # open URL to metadata
        html_text_meta = BeautifulSoup(url_meta, "lxml")  # read content of html
    except Exception as e:
        print(e)
    finally:
        url_meta.close()

    # extract relevant content from metadata strings
    metadata0 = html_text_meta.select('div.detailsContent p.detailsBodyPar')[0].text
    metadata1 = html_text_meta.select('div.detailsContent p.detailsBodyPar')[1].text
    date = slicer.after(metadata0, ",")      # map dating
    sheet = slicer.between(metadata0, "; ", ",")    # sheet number
    series = slicer.between(metadata0, ": ", ";")   # map series
    sheetname = slicer.between(metadata1, "Beschreibung: ", ". -")  # sheetname

    return date, sheet, series, sheetname
