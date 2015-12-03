#!/usr/bin/python

import json
import sys
import os
import simplejson
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, content2dataframe
from sys import argv

handles = []
config = configuration()
config['remote'] = ''

# Geocoder
handle = config['geocoderhandle']
(classification, dataset, title, units) = content2dataframe(config, config['geocoderhandle'])
#if remote:
#    (classification, dataset) = loaddataset_fromurl(config, handle)
#else:
#    dataset = loaddataset(handles)

(geocoder, geolist, oecdlist) = buildgeocoder(dataset, config, '')
#print geocoder
(modern, historical) = loadgeocoder(config, dataset, 'geocoder') 

switch = 'historical'
switch = 'modern'
if switch == 'modern':
    activeindex = modern.index
    coder = modern
    class1 = switch
else:
    activeindex = historical.index
    coder = historical

handle = "hdl:10622/DIUBXI"
handle = "hdl:10622/WNGZ4A"
handle = "hdl:10622/GZ7O1K"

#if remote:
#    (class1, dataset) = loaddataset_fromurl(config, handle)
#else:
#    dataset = loaddataset(handles)
(class1, dataset, title, units) = content2dataframe(config, handle)

(cfilter, notint) = selectint(activeindex.values)
(moderndata, historicaldata) = loadgeocoder(config, dataset, '')
if switch == 'modern':
    maindata = moderndata
else:
    maindata = historicaldata
 
tree = []
tree = treemap(config, maindata, class1, cfilter, coder)
print tree

ccode = '150'
year = '2004'

test = ''
if test:
#    ccode = '1639'
#    year = '1945'
    x = dataset.ix[str(ccode)][str(year)] 
    dataf = dataset.ix[str(ccode)]
    print dataset.to_html
    print x

