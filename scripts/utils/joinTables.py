# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 13:50:35 2017

@author: user
"""

import pandas as pd

'''join tables based on a key'''


def join_tables(table1, table2, key):
    df1 = pd.read_csv(table1, encoding='UTF-8', index_col=False, dtype=str, delimiter = ";")
    df2 = pd.read_csv(table2, encoding='UTF-8', index_col=False, dtype=str, delimiter = ";", usecols=["Datei", "SouthLat", "WestLon", "NorthLat", "EastLon" ])
    df3 = pd.merge(df1, df2, on=key, how='left')
    return df3

if __name__ == "__main__":
    tab2 = r"C:\Users\user\Desktop\pygeometa\final\crawled_metadata_slub_maps_uuid_georef_places.csv"
    tab1 = r"C:\Users\user\Desktop\pygeometa\final\crawled_metadata_slub_maps_uuid_places.csv"
    key = 'Datei'
    out = r'C:\Users\user\Desktop\pygeometa\final\crawled_metadata_slub_maps_uuid_places_bbox.csv'

    join_tables(tab1, tab2, key).to_csv(out, index=False, dtype=str, sep=";", encoding= "utf-8")

#ISO-8859-1