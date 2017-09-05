# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 09:21:44 2017

@author: user
"""

import os, sys
from datetime import datetime
import pandas as pd
import uuid
import overpass
from osgeo import gdal, osr, ogr

''' get information on georeference system and
    bounding box coordinates from mapfiles'''


def createUUID():
    '''Return a universally unique identifier'''
    uniqueID = str(uuid.uuid1())
    return uniqueID


def getGeoRef(georefFile):
    '''Return the EPSG Code from georeferenced file information'''
    if georefFile.endswith(".tif"):
        grefFile = gdal.Open(georefFile)
        prj = grefFile.GetProjection()
        srs = osr.SpatialReference(wkt=prj)
        auth = srs.GetAttrValue("AUTHORITY", 0)
        code = srs.GetAttrValue("AUTHORITY", 1)
    elif georefFile.endswith(".shp"):
        driver = ogr.GetDriverByName('ESRI Shapefile')
        dataset = driver.Open(georefFile)
        layer = dataset.GetLayer()
        srs = layer.GetSpatialRef()
        auth = srs.GetAttrValue("AUTHORITY", 0)
        code = srs.GetAttrValue("AUTHORITY", 1)
    elif georefFile.endswith(".geojson") or georefFile.endswith(".json"):
        driver = ogr.GetDriverByName('GeoJSON')
        dataset = driver.Open(georefFile)
        layer = dataset.GetLayer()
        srs = layer.GetSpatialRef()
        auth = srs.GetAttrValue("AUTHORITY", 0)
        code = srs.GetAttrValue("AUTHORITY", 1)
    else:
        auth = None
        code = None
    return auth, code


def getBBox(georefFile):
    '''Return the bounding box coordinates of the map sheet '''
    grefFile = gdal.Open(georefFile)
    inEPSG = getGeoRef(georefFile)
    inSpatialRef = osr.SpatialReference()
    try:
        inSpatialRef.ImportFromEPSG(int(inEPSG[1]))
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(int(4326))
        transform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
        cols = grefFile.RasterXSize
        rows = grefFile.RasterYSize
        geotransform = grefFile.GetGeoTransform()
        westLon = originX = geotransform[0]
        northLat = originY = geotransform[3]
        pixelWidth = geotransform[1]
        pixelHeight = geotransform[5]
        Width = cols*pixelWidth
        Height = rows*pixelHeight
        eastLon = originX+Width
        southLat = originY+Height
        latlong1 = transform.TransformPoint(westLon, northLat)
        latlong2 = transform.TransformPoint(eastLon, southLat)
        return latlong2[1], latlong1[0], latlong1[1], latlong2[0]
    except:
        pass


def getPlaceNames(georefFile):
    '''Return the OSM place names within the bounding box of the map sheet '''
    api = overpass.API()
    try:
        coords = getBBox(georefFile)
        query = '(node["place"="village" ](%s,%s,%s,%s);node["place"="suburb" ]\
                  (%s,%s,%s,%s);node["place"="town" ](%s,%s,%s,%s); \
                  node["place"="city" ](%s,%s,%s,%s);)' % \
                  (coords[0], coords[1], coords[2], coords[3],
                   coords[0], coords[1], coords[2], coords[3],
                   coords[0], coords[1], coords[2], coords[3],
                   coords[0], coords[1], coords[2], coords[3])
        response = api.Get(query)
        towns = response["features"]
        for town in towns:
            props = town["properties"]
            try:
                yield props["name"]
            except:
                pass
    except Exception as e:
        print(e)
        print("INFO: No information on geonames available for %s." % georefFile)

if __name__ == "__main__":
    inpath = r'C:\Users\user\Desktop\georef'
    georef_file_dir = inpath

    header_ref = ["Datei", "UUID", "RefAuth", "RefCode", "SouthLat", "WestLon", "NorthLat", "EastLon"]
    header_place = ["Datei", "Placenames"]
    err_ref_df = pd.DataFrame()  # create dataframes for error logs
    err_place_df = pd.DataFrame()
    liste_ref = []
    liste_place = []

    counter = 0
    for path, subdir, files in os.walk(inpath):
        for topomap in files:
            if topomap.endswith(".tif"):
                base = os.path.basename(topomap)
                filename = os.path.splitext(base)[0]
                georefFile = os.path.join(georef_file_dir, topomap)
                try:
                    uid = createUUID()      # create uuid for each mapfile
                    auth, code = getGeoRef(georefFile)   # extract authority and code of georeference
                    south, west, north, east = getBBox(georefFile)   # extract bbox coordinates
                    data_ref = [topomap, uid, auth, code, south, west, north, east]
                    liste_ref.append(data_ref)
                    counter += 1
                except Exception as e:
                    print(e)
                    err_ref_df = err_ref_df.append({"File": topomap}, ignore_index=True)  # write errornous files to log dataframe
                try:
                    places = list(getPlaceNames(georefFile))  # extract geonames inside bbox
                    data_place = [topomap, places]
                    liste_place.append(data_place)
                except Exception as e:
                    print(e)
                    err_place_df = err_place_df.append({"File": topomap}, ignore_index=True)
                sys.stdout.write("\r%s" % (counter))

    ref_df = pd.DataFrame(liste_ref, columns=header_ref)  # create dataframe for metadata on georeference
    ref_df.to_csv('metadata_georef_maps.csv', encoding='UTF-8', index=False)  # save to csv

    place_df = pd.DataFrame(liste_place, columns=header_place)
    place_df.to_csv('metadata_places_maps.csv', encoding='UTF-8', index=False)  # save to csv

    if not err_ref_df.empty:
        err_ref_df.to_csv('log_GEOREF_unprocessed_files_%s.csv' % (datetime.now().strftime("%Y%m%d-%H%M%S")), index=False, header=False)  # save error logs
    if not err_place_df.empty:
        err_place_df.to_csv('log_PLACE_unprocessed_files_%s.csv' % (datetime.now().strftime("%Y%m%d-%H%M%S")), index=False, header=False)
