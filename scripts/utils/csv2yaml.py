# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 17:42:37 2017

@author: user
"""
import pandas as pd
import os, uuid
from datetime import datetime
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


def createUUID():
    '''Return a universally unique identifier'''
    uniqueID = str(uuid.uuid1())
    return uniqueID


def getISOTime():
    '''Return the current date and time in ISO format'''
    time = datetime.now().replace(microsecond=0)
    iso_time = time.isoformat()
    return iso_time


class MyYAML(YAML):
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


metadata_org = pd.read_csv(r"C:\Users\user\Desktop\pygeometa\final\crawled_metadata_slub_maps_uuid_georef_places.csv", encoding='UTF-8', delimiter=';', dtype=str, index_col=False)
meta_com = pd.read_csv(r"C:\Users\user\Desktop\pygeometa\final\metadata_common_MASi_georef.csv", delimiter=';', header=None, encoding='UTF-8')
meta_com.set_index(0, inplace=True)
meta_common = meta_com.T

for index, row in metadata_org.iterrows():

    scale = row['Massstab'].split(':')
    dates = row[8:15].sort_values(ascending=True)
    title = 'Historische Topographische Karte ' + row['Massstab'] +', '+'Blatt '+ row['Blattnummer'] + ', ' + row['Blattname'] + ', ' + row['Veroeffentlichung']
    abstract = "Die Karte '" + row['Blattname']+ "' mit der Blattnummer "+ row['Blattnummer'] + " ist Teil der Kartenserie '"  + row['Serie'] + "'. " + "Die Karte wurde " + row['Veroeffentlichung'] +" veröffentlicht. " + "Weitere Angaben zur Datierung: " + row['Datierung'] + "."

    datestamp = getISOTime()
    if pd.notnull(row['Places']):
        places = row['Places'].replace('[', '').replace(']', '').replace("'", '')
        places = places.replace(", ", ",")
    else:
        places = None
    GEMETconcepts = meta_common['keyThesa_concepts'].values[0].split(', ')[0] + ', '+ meta_common['keyThesa_concepts'].values[0].split(', ')[1]
    GEMETconceptsDate = meta_common['keyThesa_concepts'].values[0].split(', ')[2]
    INSPIREthemes = meta_common['keyThesa_INSPIRE'].values[0].split(', ')[0] + ', '+ meta_common['keyThesa_INSPIRE'].values[0].split(', ')[1]
    INSPIREthemesDate = meta_common['keyThesa_INSPIRE'].values[0].split(', ')[2]

    base = os.path.basename(row["Datei"])   # define output filename and path
    filename = os.path.splitext(base)[0]
    outfile = "".join(filename)+'.yml'
    outpath = r"C:\Users\user\Desktop\pygeometa\YAML"

    with open(os.path.join(outpath, outfile), 'wb') as new_yaml:
        with open(r"C:\Users\user\Desktop\pygeometa\YAMLtemplates\template_MASI.yml", "r") as template:
            a = template.read()

# metadata
        yaml = MyYAML(typ='rt')
        yaml_data = yaml.load(a)
        yaml_data['metadata']['identifier'] = createUUID()
        yaml_data['metadata']['language'] = meta_common['mdLang'].values[0]
        yaml_data['metadata']['charset'] = meta_common['mdChar'].values[0]
        yaml_data['metadata']['hierarchylevel'] = meta_common['hierLevel'].values[0]
        yaml_data['metadata']['datestamp'] = datestamp
        yaml_data['metadata']['mdMaintenance']['maintenancefrequency'] = meta_common['mdMaint'].values[0]

# spatial
        if 'RefCode' in row:
            yaml_data['spatial']['crs']['code'] = row['RefCode']
            yaml_data['spatial']['crs']['authority'] = row['RefAuth']
        yaml_data['spatial']['scale'] = scale[1]
        if pd.notnull(row['WestLon']):
            yaml_data['spatial']['westLon'] = row['WestLon']
            yaml_data['spatial']['eastLon'] = row['EastLon']
            yaml_data['spatial']['southLat'] = row['SouthLat']
            yaml_data['spatial']['northLat'] = row['NorthLat']
        else:
            yaml_data['spatial']['westLon'] = 'unknown'
            yaml_data['spatial']['eastLon'] = 'unknown'
            yaml_data['spatial']['southLat'] = 'unknown'
            yaml_data['spatial']['northLat'] = 'unknown'

# identification
        yaml_data['identification']['language'] = meta_common['dataLang'].values[0]
        yaml_data['identification']['title'] = title
        yaml_data['identification']['abstract'] = abstract
        for datetype, datum in dates[:dates.last_valid_index()].iteritems():
            if datetype == 'Aufnahme':
                if ',' in datum:
                    daten = datum.split(', ')
                    datum = []
                    for elem in daten:
                        elem.strip()
                        datum.append(elem)
                    datum.sort()
                    yaml_data['identification']['dates']['creation'] = datum[0]
                else:
                    yaml_data['identification']['dates']['creation'] = datum
            elif datetype == 'Herausgabe':
                if ',' in datum:
                    daten = datum.split(', ')
                    datum = []
                    for elem in daten:
                        elem.strip()
                        datum.append(elem)
                    datum.sort()
                    yaml_data['identification']['dates']['distribution'] = datum[-1]
                else:
                    yaml_data['identification']['dates']['distribution'] = datum
            elif datetype == 'Veroeffentlichung':
                yaml_data['identification']['dates']['publication'] = datum
            elif datetype == 'Nachtrag':
                if ',' in datum:
                    daten = datum.split(', ')
                    datum = []
                    for elem in daten:
                        elem.strip()
                        datum.append(elem)
                    datum.sort()
                    yaml_data['identification']['dates']['revision'] = datum[-1]
                else:
                    yaml_data['identification']['dates']['revision'] = datum
        yaml_data['identification']['identifier'] = row['UUID']
        yaml_data['identification']['purpose'] = meta_common['purpose'].values[0]
        yaml_data['identification']['presForm'] = meta_common['presForm'].values[0]
        yaml_data['identification']['series'] = row['Serie']
        yaml_data['identification']['keywords']['place']['keywords'] = places
        yaml_data['identification']['keywords']['place']['keywords_type'] = 'place'
        yaml_data['identification']['keywords']['theme']['keywords'] = meta_common['keywords_theme'].values[0]
        yaml_data['identification']['keywords']['theme']['keywords_type'] = 'theme'
        yaml_data['identification']['keywords']['discipline']['keywords'] = meta_common['keywords_discipline'].values[0]
        yaml_data['identification']['keywords']['discipline']['keywords_type'] = 'discipline'
        yaml_data['identification']['keywords']['GEMET']['keywords'] = meta_common['keywords_GEMET_conc'].values[0]
        yaml_data['identification']['keywords']['GEMET']['keywords_thesa'] = GEMETconcepts
        yaml_data['identification']['keywords']['GEMET']['keywords_thesa_date'] = GEMETconceptsDate
        yaml_data['identification']['keywords']['INSPIRE']['keywords'] = meta_common['keywords_GEMET_insp'].values[0]
        yaml_data['identification']['keywords']['INSPIRE']['keywords_thesa'] = INSPIREthemes
        yaml_data['identification']['keywords']['INSPIRE']['keywords_thesa_date'] = INSPIREthemesDate
        yaml_data['identification']['topiccategory'] = [meta_common['tpCat'].values[0]]
        yaml_data['identification']['useConstraints']['code'] = meta_common['useConstr'].values[0]
        if int(dates['Veroeffentlichung']) < 1901:
            yaml_data['identification']['useConstraints']['otherConstraints'] = meta_common['licencePre'].values[0]
        else:
            yaml_data['identification']['useConstraints']['otherConstraints'] = meta_common['licencePost'].values[0]
        if dates[0] == dates[dates.last_valid_index()]:
            yaml_data['identification']['temporal_position'] = dates[0]
        else:
            if ',' in dates[0]:
                daten = dates[0].split(', ')
                daten.sort()
                yaml_data['identification']['temporal_begin'] = daten[0]
            else:
                yaml_data['identification']['temporal_begin'] = dates[0]
            yaml_data['identification']['temporal_end'] = dates[dates.last_valid_index()]
        yaml_data['identification']['dataMaintenance']['maintenancefrequency'] = meta_common['resMaint'].values[0]
        yaml_data['identification']['resourceFormat']['formatName'] = meta_common['formatName'].values[0]
        yaml_data['identification']['resourceFormat']['formatVersion'] = meta_common['formatVer'].values[0]

# contact
        yaml_data['contact']['main']['organization'] = meta_common['pocOrgName'].values[0]
        yaml_data['contact']['main']['phone'] = meta_common['pocvoiceNum'].values[0]
        yaml_data['contact']['main']['fax'] = meta_common['pocfaxNum'].values[0]
        yaml_data['contact']['main']['address'] = meta_common['pocdelPoint'].values[0]
        yaml_data['contact']['main']['city'] = meta_common['poccity'].values[0]
        yaml_data['contact']['main']['postalcode'] = meta_common['pocpostCode'].values[0]
        yaml_data['contact']['main']['country'] = meta_common['poccountry'].values[0]
        yaml_data['contact']['main']['email'] = meta_common['poceMailAdd'].values[0]
        yaml_data['contact']['main']['url'] = meta_common['pocUrl'].values[0]

        yaml_data['contact']['resContact']['organization'] = meta_common['custOrgName'].values[0]
        yaml_data['contact']['resContact']['phone'] = meta_common['custvoiceNum'].values[0]
        yaml_data['contact']['resContact']['fax'] = meta_common['custfaxNum'].values[0]
        yaml_data['contact']['resContact']['address'] = meta_common['custdelPoint'].values[0]
        yaml_data['contact']['resContact']['city'] = meta_common['custcity'].values[0]
        yaml_data['contact']['resContact']['postalcode'] = meta_common['custpostCode'].values[0]
        yaml_data['contact']['resContact']['country'] = meta_common['custcountry'].values[0]
        yaml_data['contact']['resContact']['email'] = meta_common['custeMailAdd'].values[0]
        yaml_data['contact']['resContact']['url'] = meta_common['custUrl'].values[0]

# distribution
        yaml_data['distribution']['formatName'] = meta_common['formatName'].values[0]
        yaml_data['distribution']['formatVersion'] = meta_common['formatVer'].values[0]
        yaml_data['distribution']['transfer']['link']['url'] = row['Linkage']
        #yaml_data['distribution']['transfer']['link']['type'] = meta_common['pocdelPoint'].values[0]
        #yaml_data['distribution']['transfer']['link']['name'] = meta_common['poccity'].values[0]
        #yaml_data['distribution']['transfer']['link']['description'] = meta_common['pocpostCode'].values[0]
        yaml_data['distribution']['transfer']['link']['function'] = 'information'

# quality
        yaml_data['quality']['scope'] = meta_common['Dqscope'].values[0]
        yaml_data['quality']['lineage'] = meta_common['lineageStat'].values[0]


        x = yaml.dump(yaml_data)
        new_yaml.write(x.encode('utf-8'))

