#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 09:05:07 2016

@author: Helen Kollai
"""

from lxml import etree
import os
import csv
from datetime import datetime
from datetime import date
import uuid

# own modules
from utils import crawlSLUB
from utils import GeoRefInfo as gref


def getISOTime():
    '''Return the current date and time in ISO format'''
    time = datetime.now().replace(microsecond=0)
    iso_time = time.isoformat()
    return iso_time

def createUUID():
    '''Return a universally unique identifier'''
    uniqueID = str(uuid.uuid1())
    return uniqueID


def list_to_xml(datalist, rootname, mapfile, georefFile):

    '''Collect metadata from csv, web and file and return basic XML string'''
    base = os.path.basename(mapfile)
    filename = os.path.splitext(base)[0]

    root = etree.Element(rootname)
    for fld in datalist:
        col = fld[0]
        dat = str(fld[1])
        child = etree.SubElement(root, col)
        child.text = dat
    child1 = etree.SubElement(root, "mdDateSt")
    child1.text = getISOTime()

    # ----metadata UUID-----
    child2 = etree.SubElement(root, "mdFileID")
    child2.text = gref.createUUID()

    # ------data identification--------------------------
    child4 = etree.SubElement(root, "dataIdInfo")
            # ------keywords
    child42a = etree.SubElement(child4, "descKeys")
    generator = gref.getPlaceNames(georefFile)
    for value in generator:
        child42a1 = etree.SubElement(child42a, "keyword")
        child42a1.text = value
    child42a2 = etree.SubElement(child42a, "keyTyp")
    child42a2.text = "place"
            # ------keywords theme
    child42b = etree.SubElement(child4, "descKeys")
    theme_keys = list(root.iter('keyword_theme'))
    for x in theme_keys:
        child = etree.SubElement(child42b, "keyword")
        child.text = x.text
    child42b2 = etree.SubElement(child42b, "keyTyp")
    child42b2.text = "theme"
            # ------keywords discipline
    child42c = etree.SubElement(child4, "descKeys")
    disci_keys = list(root.iter('keyword_discipline'))
    for x in disci_keys:
        child = etree.SubElement(child42c, "keyword")
        child.text = x.text
    child42c2 = etree.SubElement(child42c, "keyTyp")
    child42c2.text = "discipline"
            # ------keywords general
    child42d = etree.SubElement(child4, "descKeys")
    child42d1 = etree.SubElement(child42d, "keyword")
    child42d1.text = "Karte"
#    child42d2 = etree.SubElement(child42d, "keyword")
#    child42d2.text = "Geographisch kodierte Daten"
    child42d3 = etree.SubElement(child42d, "thesaName")
    child42d31 = etree.SubElement(child42d3, "resTitle")
    child42d31.text = "GEMET - concepts, version 3.1, 2012-07-20"
                    # ------keywords temporal
    child42f = etree.SubElement(child4, "descKeys")
    child42f1 = etree.SubElement(child42f, "keyword")
    child42f1.text = "historisch"
    child42f2 = etree.SubElement(child42f, "keyTyp")
    child42f2.text = "temporal"
                # ------keywords general
    child42e = etree.SubElement(child4, "descKeys")
    child42e1 = etree.SubElement(child42e, "keyword")
    child42e1.text = "Geographische Bezeichnungen"
    child42e2 = etree.SubElement(child42e, "thesaName")
    child42e21 = etree.SubElement(child42e2, "resTitle")
    child42e21.text = "GEMET - INSPIRE themes, version 1.0, 2008-06-01"
    # ------data citation
    child43 = etree.SubElement(child4, "idCitation")
    child431 = etree.SubElement(child43, "resTitle")
    child432 = etree.SubElement(child43, "resAltTitle")
    child433 = etree.SubElement(child43, "datasetSeries")
    child4331 = etree.SubElement(child433, "seriesName")
    child434 = etree.SubElement(child43, "resRefDate")
    child4341 = etree.SubElement(child434, "refDate")
    child4342 = etree.SubElement(child434, "refDateType")
    citation = crawlSLUB.readUrl(filename)
    try:
        int(citation[0])
        child4341.text = date(int(citation[0]), 1, 1).isoformat()
        child431.text = "Historische Topographische Karte 1:25000, Messtischblatt %s, %s, %s" % (citation[1], citation[3], citation[0])
        child432.text = "HTK25 %s %s" % (citation[1], citation[0])
    except:
        child431.text = "Historische Topographische Karte 1:25000, Messtischblatt %s, %s" % (citation[1], citation[3])
        child432.text = "HTK25 %s" % (citation[1])
    child4342.text = "creation"
    child4331.text = citation[2]
    child435 = etree.SubElement(child43, "presForm")
    child435.text = root.find("presForm").text

    # ------data abstract
    child44 = etree.SubElement(child4, "idAbs")
    child44.text = 'Das Kartenblatt "%s" mit der Blattnummer %s ist Bestandteil der Kartenserie "%s" im Maßstab 1:25000. Das vorliegende Blatt wurde im Jahr %s erzeugt. ' % \
        (citation[3], citation[1], citation[2], citation[0])
    # ------data format
    child45 = etree.SubElement(child4, "dsFormat")
    child451 = etree.SubElement(child45, "formatName")
    child451.text = root.find("formatName").text
    child452 = etree.SubElement(child45, "formatVer")
    child452.text = root.find("formatVer").text
    # ------resolution
    child46 = etree.SubElement(child4, "dataScale")
    child461 = etree.SubElement(child46, "equScale")
    child461.text = root.find("equScale").text
    # ------topic category
    child47 = etree.SubElement(child4, "tpCat")
    child47.text = root.find("tpCat").text
    # ------data purpose
    child48 = etree.SubElement(child4, "idPurp")
    child48.text = root.find("idPurp").text
    # ------ressource maintenance
    child49 = etree.SubElement(child4, "resMaint")
    child49.text = root.find("resMaint").text
    # ------data language
    child49a = etree.SubElement(child4, "dataLang")
    child49a.text = root.find("dataLang").text

    # ------md contact--------------------------
    child5 = etree.SubElement(root, "mdContact")
    child51 = etree.SubElement(child5, "rpIndName")
    child51.text = root.find("rpIndName").text
    child52 = etree.SubElement(child5, "rpOrgName")
    child52.text = root.find("rpOrgName").text
    child53 = etree.SubElement(child5, "rpPosName")
    child53.text = root.find("rpPosName").text
    child54 = etree.SubElement(child5, "rpCntInfo")
    child541 = etree.SubElement(child54, "cntPhone")
    child5411 = etree.SubElement(child541, "voiceNum")
    child5411.text = root.find("voiceNum").text
    child542 = etree.SubElement(child54, "cntAddress")
    child5421 = etree.SubElement(child542, "delPoint")
    child5421.text = root.find("delPoint").text
    child5422 = etree.SubElement(child542, "city")
    child5422.text = root.find("city").text
    child5423 = etree.SubElement(child542, "adminArea")
    child5423.text = root.find("adminArea").text
    child5424 = etree.SubElement(child542, "postCode")
    child5424.text = root.find("postCode").text
    child5425 = etree.SubElement(child542, "country")
    child5425.text = root.find("country").text
    child5426 = etree.SubElement(child542, "eMailAdd")
    child5426.text = root.find("eMailAdd").text
    child55 = etree.SubElement(child5, "role")
    child55.text = root.find("role").text

    # ------constraints--------------------------
    child6 = etree.SubElement(root, "mdConst")
    child61 = etree.SubElement(child6, "Consts")
    child611 = etree.SubElement(child61, "useLimit")
    try:
        int(citation[0])
        if int(citation[0]) < 1900:
            licence = "Dieses Werk ist lizenziert unter einer Creative Commons Namensnennung - Weitergabe unter gleichen Bedingungen 4.0 International Lizenz."
        else:
            licence = "Copyright SLUB / Deutsche Fotothek Lizenz: Freier Zugang - Rechte vorbehalten."
        child611.text = "Nutzungseinschränkungen: " + licence
    except:
        child611.text = "Nutzungseinschränkungen: unbekannt"

    # ------Data quality info--------------------------
    child7 = etree.SubElement(root, "dqInfo")
    child71 = etree.SubElement(child7, "dqScope")
    child711 = etree.SubElement(child71, "scpLevel")
    child711.text = root.find("mdHrLv").text
    child72 = etree.SubElement(child7, "dataLineage")
    child721 = etree.SubElement(child72, "statement")
    child721.text = "Dieser digitale Datensatz wurde durch das Scannen einer analogen Karte erzeugt. Eigentümer der analogen Karte ist die Sächsische Landesbibliothek - Staats- und Universitätsbibliothek Dresden. Die Digitalisierung erfolgte durch den Eigentümer. Nach dem Scannen wurden das Kartenblatt georeferenziert. Dieser Prozess erfolgte über einen Crowdsourcing-Ansatz im virtuellen Kartenforum 2.0."  

    return root


def transform(xslfile, mapfile, georefFile):
    '''Transform basic XML string into a ISO19139 conform XML string'''
    xsl = etree.parse(xslfile)
    xslt = etree.XSLT(xsl)
    with open("metadata.csv") as f:
        data = [list(line) for line in csv.reader(f, delimiter=';')]
        data2 = list(zip(data[0], data[1]))
        inxml = list_to_xml(data2, "MI_Metadata", mapfile, georefFile)

    return xslt(inxml)


def writeXml(xslfile, mapfile, georefFile, outputFile):
    '''Write ISO conform metadata to XML file'''
    iso19139 = transform(xslfile, mapfile, georefFile)
    iso19139.write(outputFile,
                   pretty_print=True, xml_declaration=True, encoding='UTF-8')

if __name__ == "__main__":
    print(getISOTime())
