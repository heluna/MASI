#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 09:10:58 2017

This code is under MIT licence

Copyright (C) 2017 Helen Kollai
"""
import time, re
import logging
import os, sys
import argparse
import traceback
import csv

#  third-party module
from utils.DublinCoreTerms import DublinCore

# own module
from metaextractors import metaextractor


logger = logging.getLogger()

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

# -----------------------------------------------------------------------------


class EXTRACTOR(object):

    '''
    Runs crawler and extracts metadata from map files and writes metadata
    to iso19115 compatible xml file. If no georeferenced file given the
    source file is expected to be georeferenced.
    '''

    def __init__(self, base_outdir):
        self.base_outdir = base_outdir

    def extract(self, request):
        inpath = request[0]
        if not os.path.isdir(self.base_outdir):
            os.makedirs(self.base_outdir)
        if not request[4]:
            georef_file_dir = inpath
        xslfile = request[3]

        counter = 0
        print("Number of processed files:")
        for path, subdir, files in os.walk(inpath):
            for topomap in files:
                if topomap.endswith(".tif"):
                    base = os.path.basename(topomap)
                    filename = os.path.splitext(base)[0]
                    outputFile = "{0}.xml".format(filename)
                    outputPath = os.path.join(self.base_outdir, outputFile)
                    georefFile = os.path.join(georef_file_dir, topomap)
                    try:
                        metaextractor.writeXml(xslfile, topomap, georefFile, outputPath)
                        counter += 1
                    except Exception as e:
                        print(e)
                    sys.stdout.write("{0}\r".format(counter))

            break


class TRANSFORMATOR(object):

    def __init__(self, base_outdir):
        self.base_outdir = base_outdir

    def transform(self, request):
        print("Hello: I have been transforming")


class GENERATOR(object):

    def __init__(self, base_outdir):
        self.base_outdir = base_outdir
        self.DC_NS = 'http://www.dublincore.org/schemas/xmls/qdc/2008/02/11/dc.xsd'

    def generate(self, request):

        # set parameters
        project = '' if request[1] is None else str(request[1])
        inpath = request[0]
        schema = '' if request[2] is None else str(request[2])
#        schema = request[2]
        delimiter = input('Please define the delimiter of the input file (","/"\\t"/";"):')
        outpath = '/'.join([self.base_outdir, project + schema + "metadata", 'xml'])
        if not os.path.isdir(outpath):
            os.makedirs(outpath)

        # csv file to parse
        fn = '%s' % inpath

        # mapfile
        mapfile = "{0}{1}mapping.csv" .format(project, schema)

        """ Parse a CSV or TSV file """
        mapdc = dict()
        fields = list()
        try:
            with open(fn, 'r') as fp:
                ofields = re.split(delimiter, fp.readline().rstrip('\n').strip())
                print('|- Original fields:\n\t{0}' .format(ofields))

                if os.path.isfile(mapfile):
                            print('|- Use existing mapfile\t{0}' .format(mapfile))
                            with open(mapfile, "r") as infile:
                                r = csv.reader(infile, delimiter='>')
                                for row in r:
                                    fields.append(row[1].rstrip('\n').strip())
                else:
                            print('|- Generate mapfile:\t{0}'.format(mapfile))
                            with open(mapfile, "w") as outfile:
                                w = csv.writer(outfile, delimiter='>', lineterminator='\n')
                                for of in ofields:
                                    mapdc[of.strip()] = input('Target field for {0} : ' .format(of.strip()))
                                    fields.append(mapdc[of.strip()].strip())
                                    w.writerow([of.strip(), mapdc[of.strip()]])

                if not delimiter == ',':
                            inputtable = csv.DictReader(fp, fieldnames=fields, delimiter='\t')
                else:
                            inputtable = csv.DictReader(fp, fieldnames=fields, delimiter=delimiter)
                            print('|- Generate XML files in {0}' .format(outpath))

                for row in inputtable:
                    if schema == "dc":
                        dc = self.makedc(row)
                        if 'dc:identifier' in row:
                                        output = "".join(row['dc:identifier'].split())+'.xml'
                                        print('  |--> {0}' .format(output))
                                        self.writefile(outpath+'/'+output, dc)
                        else:
                                        print(' ERROR : At least target field dc:identifier must be specified')
                                        os.remove(mapfile)
                                        sys.exit()
                    elif schema == "iso19115":
                        print("Using ISO19115 Transformation")
                    else:
                        print(' ERROR : Standard not supported')
                        sys.exit()
        except IOError as e:
            (errno, strerror) = e.args
            print("Error ({0}): {1}".format(errno, strerror))
            raise SystemExit

        return -1

    def makedc(self, row):
        """ Generate a Dublin Core XML object from a CSV/TSV """
        metadata = DublinCore()
        with open('mapfiles/dcelements.txt', 'r') as f:
            dcelements = f.read().splitlines()
        for dcelem in dcelements:
            setattr(metadata, dcelem.capitalize(), row.get('dc:'+dcelem, ''))

        with open('mapfiles/dcterms.txt', 'r') as f:
            dcterms = f.read().splitlines()
        for dcterm in dcterms:
            setattr(metadata, dcterm.capitalize(), row.get('dcterms:'+dcterm, ''))
        return metadata

    def writefile(self, name, obj):
        """ Writes Dublin Core XML object to a file """
        if isinstance(obj, DublinCore):
            with open(name, 'w') as out:
                out.write(obj.makeXML(self.DC_NS))


# ----------------------------------------------------------------------------


def setup_custom_logger(name, verbose):

    ''' Returns messages on events and exeptions for various effective levels '''

    log_format = '%(levelname)s :  %(message)s'
    log_level = logging.CRITICAL
    if verbose == 1:
        log_format = '%(levelname)s in  %(module)s\t%(funcName)s\t%(lineno)s : %(message)s'
        log_level = logging.ERROR
    elif verbose == 2:
        log_format = '%(levelname)s in %(module)s\t%(funcName)s\t%(lineno)s : %(message)s'
        log_level = logging.WARNING
    elif verbose == 3:
        log_format = '%(levelname)s at %(asctime)s in L %(lineno)s : %(message)s'
        log_level = logging.INFO
    elif verbose > 3:
        log_format = '%(levelname)s at %(asctime)s %(msecs)d in L %(lineno)s : %(message)s'
        log_level = logging.DEBUG

    formatter = logging.Formatter(fmt=log_format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(handler)
    return logger


def options_parser():

    ''' Parser for command-line options and arguments '''

    parser = argparse.ArgumentParser(description = "Description of Metadata management tool: ",
                    prog = 'metamanager.py',
                    epilog='For any further information please contact Helen Kollai by email helen.kollai@gmail.com')

    parser.add_argument('-v', '--verbose', action = "count", help = "increase output verbosity (e.g., -vv is more than -v)", default = False)
    parser.add_argument('--mode', '-m', metavar = 'PROCESSINGMODE', help = '\nThis specifies the processing mode. Supported modes are (g)enerating, extracting from (slub)website, (t)ransforming.')
    parser.add_argument('--source', '-s', help = "A path to files (e.g. .csv, .xml, .tif) you want to process", default = None, metavar = 'PATH')
    parser.add_argument('--outdir', '-d', help = "The relative root dir in which all processed files will be saved. (default is 'metadata')", default = 'metadata', metavar = 'PATH')
    parser.add_argument('--project', '-p', help = "The name of the project of processed data", default = None, metavar = 'STRING')
    parser.add_argument('--target_schema', help = "Meta data schema of the target", default = None, metavar = 'STRING')
    parser.add_argument('--xslt', '-x', help = "A path to xslt file for standards-compliant transformation. (default is 'iso19115.xslt')", default = 'iso19115.xslt', metavar = 'PATH')
    parser.add_argument('--georef', '-r', help = "A path to georeferenced files.", default = None, metavar = 'PATH')

    return parser


def pstat_init(modes, mode, source, schema):

    ''' Setting up processing mode and related information '''

    if mode not in modes:
        if mode:
            print(("[ERROR] Mode '" + mode + "' is not supported"))
        else:
            print(("[ERROR] Please define a processing mode"))
        sys.exit(-1)

    # initialize status, count and timing of processes
    plist = ['g', 'slub', 't']
    pstat = {'status': {}, 'text': {}, 'short': {}}

    for proc in plist:
        pstat['status'][proc] = 'no'
        if proc in mode:
            pstat['status'][proc] = 'to be done'

    stext = str(source)
    schematext = str(schema)

    pstat['text']['g'] = 'Generate XML files from raw information'
    pstat['text']['slub'] = 'Extract metadata from files in ' + stext
    pstat['text']['t'] = 'Transform simple XML to standard conform XML in ' + schematext

    pstat['short']['g'] = 'Generation'
    pstat['short']['slub'] = 'Extraction'
    pstat['short']['t'] = 'Transformation'

    return (mode, pstat)


def process_generate(GEN, rlist):
    # genstart = time.time()

    logging.info('  |  %-30s \n\t|- %-10s |@ %-10s |' % (rlist, 'Started', time.strftime("%H:%M:%S")))
    results = GEN.generate(rlist)

    if results == -1:
        logging.error("Couldn't generate metadata according request %s" % rlist)

    # gentime = time.time() - genstart


def process_transform(TRA, rlist):
    # transtart = time.time()

    logging.info('  |  %-30s \n\t|- %-10s |@ %-10s |' % (rlist, 'Started', time.strftime("%H:%M:%S")))
    results = TRA.transform(rlist)

    if results == -1:
        logging.error("Couldn't transform metadata according request %s" % rlist)

    # transtime = time.time() - transtart


def process_extract(EXT, rlist):
    # extstart = time.time()

    logging.info('  |  %-30s \n\t|- %-10s |@ %-10s |' % (rlist, 'Started', time.strftime("%H:%M:%S")))
    results = EXT.extract(rlist)

    if results == -1:
        logging.error("Couldn't extract metadata according request %s" % rlist)

    # exttime = time.time() - extstart


def process(options, pstat):

    procOptions = ['source', 'outdir', 'project', 'target_schema', 'xslt', 'georef']
    mandParams = ['source']  # mandatory processing params
    for param in mandParams:
        if not getattr(options, param):
            logger.critical("Processing parameter '%s' is required" % param)
            sys.exit(-1)
    reqlist = [options.source, options.project, options.target_schema, options.xslt, options.georef]

    # check job request (processing) options
    for opt in procOptions:
        if hasattr(options, opt):
            logger.debug(' |- %s:\t%s' % (opt.upper(), getattr(options, opt)))

    # GENERATION mode:
    if pstat['status']['g'] == 'to be done':
        print('\n|- Metadata generation started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
        GEN = GENERATOR(options.outdir)
        process_generate(GEN, reqlist)

    # TRANSFORMATION mode:
    if pstat['status']['t'] == 'to be done':
        print('\n|- Metadata transformation started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
        TRA = TRANSFORMATOR(options.outdir)
        process_transform(TRA, reqlist)

    # EXTRACTION mode:
    if pstat['status']['slub'] == 'to be done':
        print('\n|- Metadata extraction started : %s' % time.strftime("%Y-%m-%d %H:%M:%S"))
        EXT = EXTRACTOR(options.outdir)
        process_extract(EXT, reqlist)


def main():
    global TimeStart
    TimeStart = time.time()

    # check the version from svn:
    global ToolVersion
    ToolVersion = '0.1'

    modes = ['g', 'generation', 'slub', 'extraction', 't', 'transformation']

    global options
    p = options_parser()
    options = p.parse_args()

    (mode, pstat) = pstat_init(modes, options.mode, options.source, options.target_schema)

    now = time.strftime("%Y-%m-%d %H:%M:%S")
    setup_custom_logger('root', options.verbose)

    # print out general info:
    print('\nVersion:  \t%s' % ToolVersion)
    print('Mode: \t%s\n \t%s' % (pstat["text"][mode], pstat["status"][mode]))
    print("Start : \t%s\n" % now)

    try:
        # start the process:
        process(options, pstat)
        exit()
    except Exception as e:
        logging.critical("[CRITICAL] Program is aborted because of a critical error! Description:")
        logging.critical("%s" % traceback.format_exc())
        exit()
    finally:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info("\tEnd : %s" % now)


if __name__ == "__main__":
    main()
