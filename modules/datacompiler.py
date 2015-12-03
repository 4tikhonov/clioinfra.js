#!/usr/bin/python
import json
import sys
import os
import re
import simplejson
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, dataset_analyzer, content2dataframe
from data2excel import create_excel_dataset
from sys import argv
from historical_data import save_historical_dataset
from random import randint
import openpyxl
from openpyxl.cell import get_column_letter
import numpy as np

def dataframe_compiler(config, fullpath, handle, switch, datafilter):
    handles = []
    ctrlist = []
    metadata = {}

    # Load Geocoder
    (classification, dataset, title, units) = content2dataframe(config, config['geocoderhandle'])

    (geocoder, geolist, oecd2webmapper) = buildgeocoder(dataset, config, '')
    (modern, historical) = loadgeocoder(config, dataset, 'geocoder')
    coderyears = []
    # Default years selection
    for i in range(1500, 2016):
        coderyears.append(i)
    # Years selected
    if datafilter['startyear']:
        coderyears = []
        for i in range(int(datafilter['startyear']), int(datafilter['endyear'])):
            coderyears.append(i)

    # Reading dataset
    (class1, dataset, title, units) = content2dataframe(config, handle)

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
        # Do conversion to webmapper system if there are no historical data
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
	    # Drop not recognized locations
            maindata = maindata[maindata.index > 0]
        else:
            maindata = historicaldata

    if title:
        metadata['title'] = title
    else:
        metadata['title'] = ''

    if units:
        metadata['units'] = units
    else:
        metadata['units'] = ''

    (cfilter, notint) = selectint(maindata.columns)
    
    codes = selectint(maindata.index)
    geo = load_geocodes(config, switch, codes, maindata, geolist)
    for colname in notint:
        maindata = maindata.drop(colname, axis=1)

    # Apply filters
    if datafilter:
        (datasubset, ctrlist) = datasetfilter(maindata, datafilter)
    else:
	datasetset = maindata

    # Create Excel file out from dataframe
    (yearscolumns, notyears) = selectint(maindata.columns)
    (countryinfo, notcountry) = selectint(maindata.index)

    (finalsubset, icoder, isyear, ctrfilter, nodata) = dataset_analyzer(datasubset, coder, yearscolumns)
    # Apply filter to countries
    if datafilter['ctrlist']:
        tmpcoder = icoder.ix[ctrlist]
        icoder = pd.DataFrame(tmpcoder)

    if fullpath:
        datafile = create_excel_dataset(fullpath, icoder, metadata, icoder.columns, coderyears, finalsubset, isyear, ctrfilter)
    return (fullpath, finalsubset)
