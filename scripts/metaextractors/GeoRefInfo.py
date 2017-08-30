# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 09:21:44 2017

@author: user
"""

import os, sys
from datetime import datetime
import pandas as pd

# own modules
import metaextractor as ex

''' get information on georeference system and bounding box coordinates from mapfiles'''

inpath = r'C:\Users\user\Desktop\MetadataManager'
georef_file_dir = inpath

header = ["Datei", "UUID", "RefAuth", "RefCode", "SouthLat", "WestLon", "NorthLat", "EastLon"]
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
                uuid = ex.createUUID()      # create uuid for each mapfile
                auth, code = ex.getGeoRef(georefFile)   # extract authority and code of georeference
                south, west, north, east = ex.getBBox(georefFile)   # extract bbox coordinates
                data = [topomap, uuid, auth, code, south, west, north, east]
                liste.append(data)
                counter += 1
            except Exception as e:
                print(e)
                err_df = err_df.append({"File": topomap}, ignore_index=True)  # write errornous files to log dataframe
            sys.stdout.write("\r%s" % (counter))

my_df = pd.DataFrame(liste, columns=header)  # create dataframe for metadata on georeference
my_df.to_csv(r'C:\MASI\metadata_georef_maps.csv', encoding='UTF-8', index=False)  # save to csv

if not err_df.empty:
    err_df.to_csv(r'C:\MASI\log_unprocessed_files_%s.csv' % (datetime.now().strftime("%Y%m%d-%H%M%S")), index=False, header=False)  # save error log
