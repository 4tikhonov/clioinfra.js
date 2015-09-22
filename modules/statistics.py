#!/usr/bin/pyth

import urllib2 
import simplejson
import json
import pandas as pd
import re
import vincent
import numpy as np
from pandas.io.json import json_normalize

def load_api_data(apiurl, fileID):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f, "utf-8")
    return dataframe

def loadnames(dataframe):
    header = dataframe[1]
    names = {}
    for name in header:
        try:
            names[name] = int(header[name])
        except:
            names[name] = header[name]
    return names

def transform(dataframe, names):
    transframe = {}
    for item in dataframe:
        for code in item:
            thisyear = names[code]
            value = item[code]            
            if not value:
                value = np.nan
            
            try:
                dataset = transframe[thisyear]
            except:
                dataset = []
                
            dataset.append(value)        
            transframe[thisyear] = dataset

    return transframe

def createdata(jsonapi):
    dataframe = load_api_data(jsonapi, '')
    names = loadnames(dataframe)
    dataframe.pop(0)
    dataframe.pop(0)
    t = transform(dataframe, names)
    c = pd.DataFrame(t)
    c = c.drop('Code', axis=1)
    c = c.set_index('Continent, Region, Country')
    
    return c


