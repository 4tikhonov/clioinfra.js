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
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, dataset_analyzer
from data2excel import create_excel_dataset
from sys import argv
from historical_data import save_historical_dataset
from random import randint
import openpyxl
from openpyxl.cell import get_column_letter
import numpy as np

handles = []
remote = 'on'
config = configuration()

# Geocoder
handle = config['geocoderhandle']
if remote:
    (classification, dataset, title, units) = loaddataset_fromurl(config, handle)
else:
    dataset = loaddataset(handles)

(geocoder, geolist) = buildgeocoder(dataset, config, '')
(modern, historical) = loadgeocoder(config, dataset, 'geocoder')
coderyears = []
for i in range(1500, 2015):
    coderyears.append(i)

# Reading dataset
handle = "hdl:10622/WNGZ4A"
#handle = "hdl:10622/DIUBXI"
handles = []
handles.append(handle)
switch = 'historical'
#switch = 'modern'

if remote:
    (class1, dataset, title, units) = loaddataset_fromurl(config, handle)
else:
    dataset = loaddataset(handles)

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
    maindata = historicaldata

(cfilter, notint) = selectint(maindata.columns)
    
codes = selectint(maindata.index)
geo = load_geocodes(config, switch, codes, maindata, geolist)
for colname in notint:
    maindata = maindata.drop(colname, axis=1)
print title

# Test filters
# Use case 1
datafilter = {}
datafilter['startyear'] = '1500'
datafilter['endyear'] = '2010'
datafilter['ctrlist'] = ''
#datafilter['ctrlist'] = '528,14,18,67'
datasubset = datasetfilter(maindata, datafilter)
#print datasubset.to_html

# Create Excel file out from dataframe
fullpath = config['webtest'] + "/subdata_set.xlsx"
(yearscolumns, notyears) = selectint(maindata.columns)
(countryinfo, notcountry) = selectint(maindata.index)
metadata = {}
metadata['title'] = 'testtitle'
metadata['units'] = 'testunits'
if title:
    metadata['title'] = title
if units:
    metadata['units'] = units

a = datetime.now()
(finalsubset, icoder, isyear, ctrfilter, nodata) = dataset_analyzer(datasubset, coder, yearscolumns)
datafile = create_excel_dataset(fullpath, icoder, metadata, icoder.columns, coderyears, finalsubset, isyear, ctrfilter)
b = datetime.now()
d = b - a
print "Time: " + str(d.seconds) + " seconds"
print datafile
#yearscolumns
#xset.ix[67][1831]
