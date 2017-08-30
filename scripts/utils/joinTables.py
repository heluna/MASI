# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 13:50:35 2017

@author: user
"""

import pandas as pd

'''join tables based on a key'''

def join_tables(table1, table2, key, output):
    df1 = pd.read_csv(table1, encoding='ISO-8859-1', index_col=False, dtype=str, delimiter=';')
    df2 = pd.read_csv(table2, encoding='UTF-8', index_col=False, dtype=str, delimiter=',')
    df3 = pd.merge(df1, df2, on=key, how='left')
    df3.to_csv(output, index=False, dtype=str, sep=";", encoding='UTF-8')
