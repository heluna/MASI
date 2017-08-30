# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 12:11:07 2016

@author: Helen Kollai
"""
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
import os, sys, re
import pandas as pd

# set path of project directory to import own modules
parentPath = os.path.abspath('..')
sys.path.insert(0, parentPath)
sys.path.append(os.path.abspath('.'))

from utils import slicer


''' method for crawling metadata content from SLUB website'''


def readUrl(filename):
    url2open = "http://www.deutschefotothek.de/gallery/freitext/{0}"\
            .format(filename)  # join base URL with filename
    try:
        url = urlopen(url2open)  # try to open the created URL
        htmltext = BeautifulSoup(url, "lxml")  # read content of html
        url.close()
    except Exception as e:
        print(e)
        url.close()
    try:    
        for links in htmltext.select('div.listItemLeft a["href"]', limit=1):
            link = links['href']    # search for the URL to map metadata
    except Exception as e:
        print(e) 
    try:
        url_meta = urlopen(link[:-len(filename)]) # open URL with metadata
        htmltext2 = BeautifulSoup(url_meta, "lxml")  # read content of html
        url_meta.close()
        linkage = link[:-len(filename)]
    except Exception as e:
        print(e)
        url_meta.close()
    # extract relevant content from metadata strings
    metadata = htmltext2.select('div.detailsContent p.detailsBodyPar')[0].text
    metadata1 = htmltext2.select('div.detailsContent p.detailsBodyPar')[1].text
    metadata2 = htmltext2.select('div.detailsContent p.detailsBodyPar')[2].text
   # metadata3 = htmltext2.select('div.document_view strong')[0].text
    
    aufnahme = slicer.between(metadata1, "-", ". -")
    print(aufnahme)
    series = slicer.between(metadata, ": ", ";")
    if series == "Neue Topographische Karte des Königreichs Württemberg im Maßstab von 1:25000" or series == "Topographischer Atlas des Grossherzogthums Baden" or series == "Topographische Karte von Baden":
        sheet = filename[14:18]
    elif series =="Topographische Karte von Bayern":
        sheet_1 = slicer.between(metadata, "; ", ",")
        sheet_2 = "(Sonderblattschnitt Bayern)"
        sheet = sheet_1 +" "+sheet_2
    else:
        sheet = slicer.between(metadata, "; ", ",")
    if metadata2.startswith("Datierung"):
        date= slicer.after(metadata2, ": ")
    else:
        date = slicer.after(metadata, ",")
    sheetname = slicer.between(metadata1, "Beschreibung: ", ". -")
    
    beschreibung = slicer.splitString(metadata1, ". -")
    if "1:25000" in beschreibung[1]:
        massstab = beschreibung[1].strip(" .")
        datierung = "keine Angaben"
        verleger = beschreibung[2].strip(" .")
    else:
        datierung = beschreibung[1].strip(" .").title()
        massstab = beschreibung[2].strip(" .")
        verleger = beschreibung[3].strip(" .")

    daten = datierung.split(",")
    ausgab = [s for s in daten if "Ausg" in s or "Neuausg" in s or "ausg." in s]
    ausgab1 = ''.join(ausgab)
    ausgabe = list(map(int, re.findall(r'\d+', ausgab1)))

    aufnahm = [s for s in daten if "Aufn" in s or "Aufge" in s]
    aufnahm1 = ''.join(aufnahm)
    aufnahme = list(map(int, re.findall(r'\d+', aufnahm1)))

    nachtra = [s for s in daten if "Nachtr" in s or "N." in s]
    nachtra1 = ''.join(nachtra)
    nachtrag = list(map(int, re.findall(r'\d+', nachtra1)))

    herausg = [s for s in daten if "Hrsg" in s]
    herausg1 = ''.join(herausg)
    herausgabe = list(map(int, re.findall(r'\d+', herausg1)))

    berein = [s for s in daten if "Berein" in s]
    berein1 = ''.join(berein)
    bereinigung = list(map(int, re.findall(r'\d+', berein1)))

    bericht = [s for s in daten if "Bericht" in s or "B." in s]
    bericht1 = ''.join(bericht)
    berichtigung = list(map(int, re.findall(r'\d+', bericht1)))

    druck = [s for s in daten if "Gedr" in s or "Aufldr" in s or "Aufl.-Dr" in s or "Auflagendr" in s]
    druck1 = ''.join(druck)
    gedruckt = list(map(int, re.findall(r'\d+', druck1)))

    return [date, sheet, series, sheetname, link, datierung, massstab, verleger, ausgabe, aufnahme, nachtrag, herausgabe, bereinigung, berichtigung, gedruckt, linkage]


current_file_dir = os.path.dirname(__file__)
directory = os.path.dirname(os.getcwd())


header=["Datei", "Serie", "Blattnummer", "Blattname", "Datierung", "Massstab", "Verleger", "Ausgabe", "Aufnahme", "Nachtrag", "Herausgabe", "Bereinigung", "Berichtigung", "Gedruckt", "Linkage", "Fulllink" ]
my_df = pd.DataFrame(columns=header)

for path, subdir, files in os.walk(current_file_dir):
    for mapfile in files:
        try:
            if mapfile.endswith(".tif"):
                base = os.path.basename(mapfile)
                filename = os.path.splitext(base)[0]
                res = readUrl(filename)
                results=[mapfile, res[2], res[1], res[3], res[5], res[6], res[7], res[8], res[9], res[10], res[11], res[12], res[13], res[14], res[15], res[4]]
                if any(x is not None for x in results):
                    s2=pd.Series(results, index=header)
                    my_df=my_df.append(s2, ignore_index=True)
                print(results)
        except:
            pass

my_df.to_csv('output_series.csv', ignore_index=True)