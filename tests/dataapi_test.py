#!/usr/bin/python

import xlwt
import sys
import os
import json
import simplejson
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel, moderncodes, data2json
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from historical import load_historical, histo
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, content2dataframe, dataset_analyzer, request_geocoder, request_datasets, dataset2panel

hist = {}
switch = 'modern'

# Test case
handles = ["4X6NCK", "F16UDU","ZWRBOY"]
handles = ["hdl:10622/4X6NCK"]
#handles = ["hdl:10622/QNTAZA"]
#handles = ["hdl:10622/F9418N"]
#handles = ["hdl:10622/4VGTV9"]
handles = ["hdl:10622/I0YK5M"]
customyear = '1901'
fromyear = '1500'
toyear = '2000'
customcountrycodes = '380,250,276,804,174,108,232,528,756'
logflag = 0
DEBUG = 0
        
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
datafilter['startyear'] = '1950'
datafilter['endyear'] = '2010'
datafilter['ctrlist'] = '528,14,18,67'
#datafilter['ctrlist'] = '523'
#datafilter['ctrlist'] = '1523'
#datafilter['ctrlist'] = ''
(geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config)
(origdata, maindata) = request_datasets(config, switch, modern, historical, handles, geolist)

(subsets, panel) = ({}, [])
for handle in handles:
    #handle = 'hdl:10622/I0YK5M'
    (datasubset, ctrlist) = datasetfilter(maindata[handle], datafilter)
    datasubset['handle'] = handle
    if not datasubset.empty:
        panel.append(datasubset)
    
    subsets[handle] = datasubset    
datapanel = dataset2panel(subsets[handle], geocoder, oecd2webmapper)
print datapanel
