#!/usr/bin/python

import xlwt
import sys
import os
import json
import simplejson
import numexpr as ne
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from data2excel import create_excel_dataset
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel, moderncodes, data2json
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from datacompiler import dataframe_compiler
from historical import load_historical, histo
from datasets import *

hist = {}
switch = 'modern'

# Test case
handles = ["4X6NCK", "F16UDU","ZWRBOY"]
handles = ["hdl:10622/4X6NCK"]
#handles = ["hdl:10622/QNTAZA"]
#handles = ["hdl:10622/F9418N"]
#handles = ["hdl:10622/4VGTV9"]
handles = ["hdl:10622/I0YK5M"]
handles = ["hdl:10622/KICLW5"]
handles = ["hdl:10622/ACOPHR"]
customyear = '1901'
fromyear = '1500'
toyear = '2000'
customcountrycodes = '380,250,276,804,174,108,232,528,756'
logflag = 0
DEBUG = 0
ne.set_num_threads(5)
        
config = configuration()
config['remote'] = ''
if fromyear:
    historical = 0
    if historical:
        api = config['apiroot'] + "/collabs/static/data/historical.json"
        (regions, countries, ctr2reg) = histo(api)
        hist = countries

# In: (handles, customcountrycodes, fromyear, toyear, customyear, hist, logflag)
#    (header, panelcells, codes, x1, x2, x3, x4, x5) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logflag)
# Out: (header, panelcells, code2ctr, datahub, data, handle2ind, unit2ind, original)

#print panelcells
#print codes
#modern = moderncodes(config['modernnames'], config['apiroot'])
#jsondata = data2json(modern, codes, panelcells)
#result = json.dumps(jsondata, ensure_ascii=False, sort_keys=True, indent=4)
#print result

datafilter = {}
logscale = ''
datafilter['startyear'] = '1500'
datafilter['endyear'] = '2010'
datafilter['ctrlist'] = '528,14,18,67'
datafilter['ctrlist'] = '528'
datafilter['ctrlist'] = ''
selectedyear = 0
if int(selectedyear) > 0:
    datafilter['startyear'] = selectedyear
    datafilter['endyear'] = selectedyear  
#datafilter['ctrlist'] = '1523'
#datafilter['ctrlist'] = ''

a = datetime.now()
(geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, '')
b = datetime.now()
d = b - a
#print modern.index
print "Geocoder time: " + str(d.seconds) + " seconds"

a = datetime.now()
(origdata, maindata, metadata) = request_datasets(config, switch, modern, historical, handles, geolist)
b = datetime.now()
d = b - a
#print origdata.to_html()
print "Dataset load time: " + str(d.seconds) + " seconds"

(subsets, panel) = ({}, [])
for handle in handles:
    #handle = 'hdl:10622/I0YK5M'
    (datasubset, ctrlist) = datasetfilter(maindata[handle], datafilter)
#    for colyear in datasubset.columns:
#        if datasubset[colyear].count() == 0:
#            datasubset = datasubset.drop(colyear, axis=1)

    datasubset['handle'] = handle
    if not datasubset.empty:
        panel.append(datasubset)
        subsets[handle] = datasubset    
	print "Added to subsets...\n"

print subsets[handles[0]].columns
logscale = ''
a = datetime.now()
(datacells, original) = dataset2panel(config, subsets[handles[0]], modern, logscale)
b = datetime.now()
d = b - a
#print origdata.to_html()
print "Dataset panel load time: " + str(d.seconds) + " seconds"
#print datacells

excel_test1 = 'on'

if excel_test1:
    a = datetime.now()
    fullpath = "/home/dpe/clioinfra.js/clioinfra/collabs/static/test.xlsx"
    (outfilefinal, finalsubset) = dataframe_compiler(config, fullpath, handle, switch, datafilter)
    b = datetime.now()
    d = b - a
    print "Dataset storing to Excel time: " + str(d.seconds) + " seconds"
    print fullpath

excel_test2 = ''
if excel_test2:
    # Create Excel
    if switch == 'modern':
        activeindex = modern.index
        coder = modern
        class1 = switch
    else:
        activeindex = historical.index
        coder = historical

    metadata = {}
    (title, units) = ('', '')
    metadata['title'] = 'testtitle'
    metadata['units'] = 'testunits'
    if title:
        metadata['title'] = title
    if units:
        metadata['units'] = units

    datasubset = subsets[handles[0]]
    #print datasubset.to_html()
    (yearscolumns, notyears) = selectint(datasubset.columns)
    #coderyears = [1900, 2010];
    coderyears = yearscolumns
    (finalsubset, icoder, isyear, ctrfilter, nodata) = dataset_analyzer(datasubset, coder, yearscolumns)
    print finalsubset.to_html()
    datafile = create_excel_dataset(fullpath, icoder, metadata, icoder.columns, coderyears, finalsubset, isyear, ctrfilter)
    print datafile
