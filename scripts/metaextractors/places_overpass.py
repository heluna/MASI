# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 10:04:54 2017

@author: user
"""

import metaextractor as ex
import os, sys, time
from datetime import datetime
import pandas as pd

'''recieve place names for bounding box of maps from Overpass API'''

inpath = r'M:\EINGANGSDATEN\geodaten\original\topographie\Altkarten_SLUB\Georef_beschnitten_TIFF'
georef_file_dir = inpath

header = ["Datei", "Placenames"]
err_df = pd.DataFrame()  # create dataframe for error log
liste = []

counter = 0
for path, subdir, files in os.walk(inpath):
    for topomap in files:
        if topomap.endswith(".tif"):
            try:
                base = os.path.basename(topomap)
                filename = os.path.splitext(base)[0]
                georefFile = os.path.join(georef_file_dir, topomap)
                places = list(ex.getPlaceNames(georefFile))  # extract geonames inside bbox
                data = [topomap, places]
                liste.append(data)
                counter += 1
                #print(places)
            except Exception as e:
                print(e)
                err_df = err_df.append({"File": topomap}, ignore_index=True)  # write errornous files to log dataframe
            sys.stdout.write("\r%s" % (counter))
        time.sleep(120)

my_df = pd.DataFrame(liste, columns=header)  # create dataframe for metadata on georeference
my_df.to_csv('metadata_places_maps.csv', encoding='UTF-8', index=False)  # save to csv

if not err_df.empty:
    err_df.to_csv('log_unprocessed_files_%s.csv' % (datetime.now().strftime("%Y%m%d-%H%M%S")), index=False, header=False)  # save error log
