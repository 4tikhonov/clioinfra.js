#!/usr/bin/python

import json
import sys
import os
import simplejson
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl
from sys import argv

handles = []
remote = 'on'
handle = "hdl:10622/DIUBXI"
handles.append(handle)
config = configuration()

if remote:
    dataset = loaddataset_fromurl(config['apiroot'], handle)
else:
    dataset = loaddataset(handles)


ccode = '150'
year = '2004'
x = dataset.ix[str(ccode)][str(year)] 
#print dataset.to_html
print x
