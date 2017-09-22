y# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 12:11:07 2016

@author: Helen Kollai
"""
# -*- coding: utf-8 -*-

from urllib.request import urlopen

import os, re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


''' methods for slicing metadata string by relative position to characters'''


def between(value, a, b):
    pos_a = value.find(a, 0, len(value))  # Find and validate before-part.
    if pos_a == -1:
        return None
    pos_b = value.find(b)  # Find and validate after part.
    if pos_b == -1:
        return None
    adjusted_pos_a = pos_a + len(a)  # Return middle part.
    if adjusted_pos_a >= pos_b:
        return None
    return value[adjusted_pos_a:pos_b]


def before(value, a):
    pos_a = value.find(a)  # Find first part and return slice before it.
    if pos_a == -1:
        return None
    return value[0:pos_a]


def after(value, a):
    pos_a = value.rfind(a)  # Find and validate first part.
    if pos_a == -1:
        return None
    adjusted_pos_a = pos_a + len(a)    # Returns chars after the found string.
    if adjusted_pos_a >= len(value):
        return None
    return value[adjusted_pos_a:]


def splitString(value, a):
    parts = value.split(a)  # split string by delimiting string/character
    return parts


''' methods for crawling metadata content from SLUB website'''


def readUrl(filename):
    slub_cat = "http://www.deutschefotothek.de/gallery/freitext/{0}"\
            .format(filename)  # join base URL with filename

    # find map in SLUB catalogue
    try:
        url = urlopen(slub_cat)  # open URL to map
        html_text_map = BeautifulSoup(url, "lxml")  # read content of html
    except Exception as e:
        print(e)
    finally:
        url.close()

    # find metadata of map in SLUB catalogue
    try:
        for links in html_text_map.select('div.listItemLeft a["href"]', limit=1):
            link = links['href']    # get URL to map metadata
        url_meta = urlopen(link[:-len(filename)])  # open URL to metadata
        html_text_meta = BeautifulSoup(url_meta, "lxml")  # read content of html
        linkage = link[:-len(filename)]
    except Exception as e:
        print(e)
    finally:
        url_meta.close()

    # extract relevant content from metadata strings
    metadata0 = html_text_meta.select('div.detailsContent p.detailsBodyPar')[0].text
    metadata1 = html_text_meta.select('div.detailsContent p.detailsBodyPar')[1].text
    metadata2 = html_text_meta.select('div.detailsContent p.detailsBodyPar')[2].text

    series = between(metadata0, ": ", ";")  # extract map series
    if series == "Neue Topographische Karte des Königreichs Württemberg im Maßstab von 1:25000" or series == "Topographischer Atlas des Grossherzogthums Baden" or series == "Topographische Karte von Baden":
        sheet = filename[14:18]
    elif series == "Topographische Karte von Bayern":
        sheet_a = between(metadata0, "; ", ",")
        sheet_b = "(Sonderblattschnitt Bayern)"
        sheet = sheet_a + " " + sheet_b
    else:
        sheet = between(metadata0, "; ", ",")    # extract sheet number

    if metadata2.startswith("Datierung"):  # extract map dating
        date = after(metadata2, ": ")
    else:
        date = after(metadata0, ",")

    sheetname = between(metadata1, "Beschreibung: ", ". -")  # extract map name

    beschreibung = splitString(metadata1, ". -")
    if "1:25000" in beschreibung[1]:
        massstab = beschreibung[1].strip(" .")
        datierung = "keine Angaben"
        verleger = beschreibung[2].strip(" .")
    else:
        datierung = beschreibung[1].strip(" .").title()  # extract date stamps
        massstab = beschreibung[2].strip(" .")           # extract scale
        verleger = beschreibung[3].strip(" .")           # extract publisher

    daten = datierung.split(",")  # split date stamp string

    ausgab = [s for s in daten if "Ausg" in s or "Neuausg" in s or "ausg." in s]
    ausgab1 = ''.join(ausgab)
    ausgabe = list(map(int, re.findall(r'\d+', ausgab1)))  # edition

    aufnahm = [s for s in daten if "Aufn" in s or "Aufge" in s]
    aufnahm1 = ''.join(aufnahm)
    aufnahme = list(map(int, re.findall(r'\d+', aufnahm1)))  # aquisition

    nachtra = [s for s in daten if "Nachtr" in s or "N." in s]
    nachtra1 = ''.join(nachtra)
    nachtrag = list(map(int, re.findall(r'\d+', nachtra1)))  # additions

    herausg = [s for s in daten if "Hrsg" in s]
    herausg1 = ''.join(herausg)
    herausgabe = list(map(int, re.findall(r'\d+', herausg1)))  # publication

    berein = [s for s in daten if "Berein" in s]
    berein1 = ''.join(berein)
    bereinigung = list(map(int, re.findall(r'\d+', berein1)))  # revision

    bericht = [s for s in daten if "Bericht" in s or "B." in s]
    bericht1 = ''.join(bericht)
    berichtigung = list(map(int, re.findall(r'\d+', bericht1)))  # correction

    druck = [s for s in daten if "Gedr" in s or "Aufldr" in s or "Aufl.-Dr" in s or "Auflagendr" in s]
    druck1 = ''.join(druck)
    gedruckt = list(map(int, re.findall(r'\d+', druck1)))  # print

    return [date, sheet, series, sheetname, link, datierung, massstab, verleger, ausgabe, aufnahme, nachtrag, herausgabe, bereinigung, berichtigung, gedruckt, linkage]


if __name__ == "__main__":
    file_dir = r'C:\Users\user\Desktop\georef'

    header = ["Datei", "Serie", "Blattnummer", "Blattname", "Datierung", "Massstab", "Verleger", "Ausgabe", "Aufnahme", "Nachtrag", "Herausgabe", "Bereinigung", "Berichtigung", "Gedruckt", "Linkage", "Fulllink"]
    meta_df = pd.DataFrame(columns=header)  # create dataframe
    err_df = pd.DataFrame()

    # append dataframe with extracted metadata for every map file processed
    for path, subdir, files in os.walk(file_dir):
        for mapfile in files:
            try:
                if mapfile.endswith(".tif"):  # all mapfiles in current dir and sub-dir
                    base = os.path.basename(mapfile)
                    filename = os.path.splitext(base)[0]
                    res = readUrl(filename)
                    results = [mapfile, res[2], res[1], res[3], res[5], res[6], res[7], res[8], res[9], res[10], res[11], res[12], res[13], res[14], res[15], res[4]]
                    if any(x is not None for x in results):
                        dataset = pd.Series(results, index=header)
                        meta_df = meta_df.append(dataset, ignore_index=True)
            except:
                print("Errors occured while extracting file: %s (File skipped)" % (mapfile))
                err_df = err_df.append({"File": mapfile}, ignore_index=True)  # log the unprocessed files

    meta_df.to_csv('metadata_slub_maps.csv', index=False)  # save to csv

    if not err_df.empty:
        err_df.to_csv('log_SLUB_unprocessed_files_%s.csv' % (datetime.now().strftime("%Y%m%d-%H%M%S")), index=False, header=False)  # save error log
