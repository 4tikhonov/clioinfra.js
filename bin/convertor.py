#!/usr/bin/python

import ConfigParser
import getopt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, dataset_analyzer
from data2excel import create_excel_dataset
from sys import argv
from historical_data import save_historical_dataset
from random import randint
import openpyxl
from openpyxl.cell import get_column_letter
import numpy as np
from excel2data import excelvalidator, parsehandle, dataextractor, downloadfile, load_api_data, getfiles
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import removedata, data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, content2dataframe, dataset_analyzer, dataset2panel, request_geocoder
import codecs
from StringIO import StringIO

def loaddataset_fromfile(config, filename):
    f = codecs.open(filename, "r", "utf-8")
    content = f.read()
    csvio = StringIO(content)
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    return dataframe

process = 'on'

if process:
    try:
        myopts, args = getopt.getopt(sys.argv[1:],"F:p:f:H:r:d:k:D:I:")
    except getopt.GetoptError as e:
        print (str(e))
        print("Usage: %s -y year -d datatype -r region -f filename -DDEBUG -o output" % sys.argv[0])
        sys.exit(2)

    (handle, rhandle, customdv) = ('', '', '')
    for o, a in myopts:
        if o == '-F':
            fullpath=a
        if o == '-p':
            path=a
        if o == '-f':
            filename=a
        if o == '-k':
            customkey=a
        if o == '-D':
            customdv=a
	if o == '-I':
	    fileID=a

    pid = 'clio'
    (jsonfile, csvfile, tmptitle, tmpunits) = dataextractor(fullpath, path, pid, fileID)

handles = []
remote = 'on'

# Geocoder
config = configuration()
config['remote'] = 'yes'
(geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, '')
dataframe = loaddataset_fromfile(config, csvfile)
dataset = dataframe
title = dataframe.columns[1]
units = dataframe.ix[0][1]
metadata = {}
switch = 'modern'
if config:
    metadataitem = {}
    if title:
        metadataitem['title'] = title
        metadataitem['units'] = units

        if switch == 'modern':
            activeindex = modern.index
            coder = modern
            class1 = switch
        else:
            activeindex = historical.index
            coder = historical

        (moderndata, historicaldata) = loadgeocoder(config, dataset, '')
        if switch == 'modern':
            maindata = moderndata
        else:
            # Do conversion to webmapper system
            if not historicaldata:
                maindata = moderndata
                webmapperindex = []
                for code in maindata.index:
                    try:
                        webmappercode = oecd2webmapper[int(code)]
                    except:
                        webmappercode = -1
                    webmapperindex.append(webmappercode)
                maindata.index = webmapperindex
                maindata = maindata[maindata.index > 0]
            else:
                maindata = historicaldata

        (cfilter, notint) = selectint(maindata.columns)

        codes = selectint(maindata.index)
        geo = load_geocodes(config, switch, codes, maindata, geolist)
        for colname in notint:
            maindata = maindata.drop(colname, axis=1)
        # Drop num if in dataframe
        if '1' in maindata.columns:
            maindata = maindata.drop('1', axis=1)
        dataframe[handle] = maindata
        metadata[handle] = metadataitem

print metadata['title']
