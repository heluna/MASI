# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 14:32:11 2017

@author: user
"""
from lxml import etree
import os.path, pandas

def list_to_xml(datalist, rootname):
    '''Transform a metadata record to a flat XML string'''

    root = etree.Element(rootname)

    for fld in datalist:
        col=fld[0]
        dat=str(fld[1]) # may need to be careful of unicode encoding issues
                        # when reading data from Excel

        child=etree.SubElement(root,col)
        child.text=dat

    return root

def transform(inxml,xslfile):
    xslfile=os.path.abspath(xslfile).replace('\\','/') #xslt doesn't like backslashes in absolute paths...
    xsl = etree.parse(xslfile)
    xslt = etree.XSLT(xsl)
    return xslt(inxml)

xslfile = r'C:\Users\user\Desktop\MetadataManager\iso19115.xslt'
 
data = pandas.read_csv(r'F:\HOME\kollai\Skripte_versionen\Results\metadata_join_slub_georef.csv', encoding='UTF-8', delimiter=';', usecols=['UUID', 'WestLon', 'EastLon', 'SouthLat', 'NorthLat'], dtype=str, index_col=False)
#Column headers from the Excel spreadsheet
header=['name','mdFileID','westBL','eastBL','southBL','northBL']

#Data pulled out of the spreadsheet
#You would loop over all rows and do a transform on each row

for row in data.iterrows():
    inxml = list_to_xml(zip(header,row),"ExcelMetadata")
    print(etree.tostring(inxml))
#The above prints - <ExcelMetadata><column1>A value</column1><xmin>1.2345</xmin><ymin>5.4321</ymin><xmax>2.3456</xmax><ymax>6.5432</ymax><thelastcolumn>last value</thelastcolumn></ExcelMetadata>

iso19139 = transform(inxml,xslfile)
print(str(iso19139))