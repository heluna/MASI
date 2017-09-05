# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 13:50:35 2017

@author: user
"""

import pandas as pd

'''join tables based on a key'''


def join_tables(table1, table2, key):
    df1 = pd.read_csv(table1, encoding='ISO-8859-1', index_col=False, dtype=str)
    df2 = pd.read_csv(table2, encoding='ISO-8859-1', index_col=False, dtype=str)
    df3 = pd.merge(df1, df2, on=key, how='left')
    return df3

if __name__ == "__main__":
    tab1 = r'C:\Users\user\Desktop\georef\crawled_metadata_slub_maps.csv'
    tab2 = r'C:\Users\user\Desktop\georef\metadata_georef_maps_-place.csv'
    key = 'Datei'
    out = r'C:\Users\user\Desktop\georef\metadata_join.csv'

    join_tables(tab1, tab2, key).to_csv(out, index=False, dtype=str, sep=";")
