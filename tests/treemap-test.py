#!/usr/bin/python

import json
import sys
import os
import simplejson
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, countrystats, loaddataset_fromurl, loadgeocoder
from sys import argv
import pandas as pd
import numpy as np

handles = []
remote = 'on'
handle = "hdl:10622/LIKXCZ"
config = configuration()

if remote:
    (classification, dataset) = loaddataset_fromurl(config['apiroot'], handle)
else:
    dataset = loaddataset(handles)

(modern, historical) = loadgeocoder(dataset)    
handles = []
handles.append(handle)
if remote:
    (class1, dataset) = loaddataset_fromurl(config['apiroot'], config['geocoderhandle'])
else:
    dataset = loaddataset(handles)

#modern.ix[76]['country']
#historical.ix[1]
#dataset.ix[56]

def treemap(dataset):
    jsonresult = ''
    (df, result) = countrystats(dataset)
    for idc in result:
        value = result[idc]    
        try:
            ctr = dataset.ix[idc]['Continent, Region, Country']
            print "\t{ \"name\": \"" + str(ctr) + "\", \"size\": " + str(value) + "}, "
        except:
            skip = idc

    return jsonresult

res = treemap(dataset)
print res
