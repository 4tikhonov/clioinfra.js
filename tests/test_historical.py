#!/usr/bin/python
import urllib2 
import simplejson
import json
import sys
import pandas as pd
import random
import vincent
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from pandas.io.json import json_normalize
import re

def loadjson(apiurl):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def datasetreader(handle):
    coder = {}
    apiroot = "http://dpe.sandbox.socialhistoryservices.org/api/datasets?handle=" + handle
    dataset = loadjson(apiroot)    
    return dataset

handle = "hdl:10622/DRIPQL"
datasets = datasetreader(handle)
for item in datasets:
    maindata = item['data']
    
clioframe = pd.DataFrame(maindata)
codes = ['1501','1498', '871']
maincode = 'Webmapper numeric code'
result = {}
navicolumns = {}
c = clioframe.columns.tolist()
dataID = 0
ycodes = []
for code in codes:
    datafilter = clioframe[clioframe[maincode] == code]
    data = datafilter
    #.transpose()
    c = datafilter.columns.tolist()
    values = datafilter.get_values()
    # Delete extra columns
    for item in data:
        try:
            #print item
            year = int(item)
        except:
            del data[item]
            navicolumns[item] = item
    if dataID == 0:
        data.reset_index(col_fill=[code])
        totaldf = data
        dataID = dataID + 1
        ycodes.append(int(code))
    else:        
        data.reset_index(col_fill=[code])
        totaldf = pd.merge(totaldf, data, how='outer')
        ycodes.append(int(code))
        
    result[code] = data
    
totaldf.index = [ycodes]
print totaldf.to_html
