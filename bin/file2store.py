#!/usr/bin/python

import json
import sys
import os
import simplejson
import re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from sys import argv

script, filename = argv

handles = []
handlequery = ''
if filename:
    print filename
    pid = re.search('(\w+).json', filename)
    if pid:
        dataset = pid.group(1) 
        handle = "hdl:10622/" + dataset
	datasetadd(filename, handle, dataset)
	print handle

