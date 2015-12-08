#!/usr/bin/python

import ConfigParser
import getopt
import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, dataset_analyzer
#from data2excel import create_excel_dataset
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
from data2excel import create_excel_dataset
from os import listdir
from os.path import isfile, join
import re

def loaddataset_fromfile(config, filename):
    f = codecs.open(filename, "r", "utf-8")
    content = f.read()
    csvio = StringIO(content)
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    return dataframe

fullpath = "/home/tikhonov/completedatasets14Sept2015/GDPperCapita.xlsx"
allfiles = ["/home/tikhonov/completedatasets14Sept2015/GDPperCapita.xlsx", "/home/tikhonov/completedatasets14Sept2015/TotalCO2Emissions.xlsx"]
outdir = "/home/tikhonov/data/historical.all"

path = "/home/tikhonov/tmp"
mypath = "/home/tikhonov/data/clio2/completedatainclKeesJonat1Nov2015"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
fileID = "test"

config = configuration()
config['remote'] = 'yes'
(geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, 'geocoder')
def compiledataset(csvfile):
    handles = []
    remote = 'on'

    # Geocoder
    config = configuration()
    config['remote'] = 'yes'
    dataframe = loaddataset_fromfile(config, csvfile)
    dataset = dataframe
    title = dataframe.columns[1]
    units = dataframe.ix[0][1]
    metadata = {}
    switch = 'modern'
    switch = 'historical'
    #dataset = dataset.convert_objects(convert_numeric=True)
    dataset.columns = dataset.ix[1]
    dataset.index = dataset[config['moderncode']]
    if '1' in dataset.columns:
        dataset = dataset.drop('1', axis=1)

    #dataset = dataset[2:]
    (intcodes, notint) = selectint(dataset.columns)
    #for colname in notint:
    #    dataset = dataset.drop(colname, axis=1)
    dataset.columns = notint + intcodes
    return (dataset, title, units)

#(dataset, title, units) = compiledataset(csvfile)
#dataset

# <codecell>

def geocoding(switch, dataset, modern, historical):
#if config:
    switch = 'historical'
    metadata = {}
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

        maindata = maindata.convert_objects(convert_numeric=True)                
        (cfilter, notint) = selectint(maindata.columns)

        codes = selectint(maindata.index)
        geo = load_geocodes(config, switch, codes, maindata, geolist)
        #for colname in notint:
            #maindata = maindata.drop(colname, axis=1)
        # Drop num if in dataframe
        if '1' in maindata.columns:
            maindata = maindata.drop('1', axis=1)
        #dataframe[pid] = maindata
        metadata[handle] = metadataitem
    return (maindata, metadata, coder)
        
def conversion(maindata, moderndata, historicaldata):
#if config:
    if switch == 'modern':
        if '1' in moderndata.columns:
            moderndata = moderndata.drop('1', axis=1)
        maindata = moderndata
        maindata.columns = moderndata.columns
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
            #maindata.columns = moderndata.columns[1]
            maindata = maindata[maindata.index > 0]
        else:
            maindata = historicaldata
    
    (cfilter, notint) = selectint(maindata.columns)
    
    codes = selectint(maindata.index)
    geo = load_geocodes(config, switch, codes, maindata, geolist)
    for colname in notint:
        maindata = maindata.drop(colname, axis=1)
    return maindata

def store_dataset(fullpath, maindata, metadata, coder):
    #fullpath = "subdata_set_last.xlsx"
    # Use case 1
    datafilter = {}
    datafilter['startyear'] = '1500'
    datafilter['endyear'] = '2016'
    #datafilter['ctrlist'] = '528,14,18,67'
    datafilter['ctrlist'] = '528'
    datafilter['ctrlist'] = '1523'
    datafilter['ctrlist'] = ''
    if datafilter['startyear']:
        coderyears = []
        for i in range(int(datafilter['startyear']), int(datafilter['endyear'])):
            coderyears.append(i)
    (datasubset, ctrlist) = datasetfilter(maindata, datafilter)

    (yearscolumns, notyears) = selectint(maindata.columns)
    (countryinfo, notcountry) = selectint(maindata.index)
            
    a = datetime.now()    
    (finalsubset, icoder, isyear, ctrfilter, nodata) = dataset_analyzer(datasubset, coder, yearscolumns)
    if datafilter['ctrlist']:
        tmpcoder = icoder.ix[ctrlist]
        icoder = pd.DataFrame(tmpcoder)
    datafile = create_excel_dataset(fullpath, icoder, metadata[handle], icoder.columns, coderyears, finalsubset, isyear, ctrfilter)
    b = datetime.now()
    d = b - a
    print "Time: " + str(d.seconds) + " seconds"
    return datafile

for ffile in onlyfiles:
    pid = 'clio'
    fullpath = mypath + '/' + ffile
    isexcel = re.match('(.+)\.xls', ffile)
    if isexcel:
        newfile = isexcel.group(1) + "-historical.xlsx"
        fulloutfile = outdir + "/" + newfile
        print fulloutfile
        pid = newfile
        handle = pid
        print handle
        (jsonfile, csvfile, tmptitle, tmpunits) = dataextractor(fullpath, path, pid, fileID)
        (dataset, title, units) = compiledataset(csvfile)
        switch = 'historical'
        (maindata, metadata, coder) = geocoding(switch, dataset, modern, historical)    
        (moderndata, historicaldata) = loadgeocoder(config, maindata, '')
        maindata = conversion(maindata, moderndata, historicaldata)
        print metadata[handle]['title']
        outfile = store_dataset(fulloutfile, maindata, metadata, coder)
        print outfile

