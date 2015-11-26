#!/usr/bin/python
import urllib2 
import simplejson
import json
import sys
import pandas as pd
import numpy as np
import random
import vincent
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from pandas.io.json import json_normalize
import re
import openpyxl
from openpyxl.cell import get_column_letter
import requests
from StringIO import StringIO
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), './modules')))
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from sys import argv

def loadgeocoder(dataset):
    geocoder = dataset.iloc[:, 1:12]
    geocoder = geocoder.ix[3:]
    geocoder = geocoder.convert_objects(convert_numeric=True)
    geocoder = geocoder.replace(r'', np.nan, regex=True)
    geocoder = geocoder.replace('NaN', np.nan, regex=True)
    modern = geocoder[pd.notnull(geocoder['ccode'])]
    historical = geocoder[pd.isnull(geocoder['ccode'])]
    modern.index = modern['ccode']
    
    return (modern, historical)

def countrystats(dataset):
    stats = {}
    newpanel = dataset.drop('Code', axis=1)
    newpanel = newpanel.drop('Continent, Region, Country', axis=1)
    newpanel = newpanel.drop('Unnamed: 0', axis=1)
    newpanel = newpanel.ix[3:]
    df = newpanel
    df = df.convert_objects(convert_numeric=True)
    df = df.replace(r'', np.nan, regex=True)
    sum_row = {col: df[col].sum() for col in df}
    codes = df.index
    cols = df.sum()
    total = cols.sum()    
    for code in codes:    
        percent = 0
        try:
            localsum = df.ix[code].sum()
            if localsum > 0:
                percent = (localsum / total) * 100
        except:
            skip = 1
        
        if percent > 0:
            stats[code] = percent
    return (df, stats)

def adjustdataframe(df):
    cols = df.columns
    checkcount = 0
    for colname in cols:
        noname = re.match("Unnamed", colname)
        if noname:
            checkcount = checkcount + 1
        
    if checkcount > 5:
        tmpdatacolumns = df.ix[1]        
        datacolumns = []
        for varcol in tmpdatacolumns:
            pyear = re.search(r'(\d{4})', str(varcol))            
            if pyear:
                thiscol = str(pyear.group(0))
            else:
                thiscol = varcol
            datacolumns.append(thiscol)
        
        df.columns = datacolumns
    return df

def loaddataset(handles):
    hquery = formdatasetquery(handles,'')
    d = readdatasets('datasets', json.loads(hquery))
    alldata = ''

    for dataset in d:
        alldata = str(dataset['csvframe'])

    dataframe = pd.read_csv(alldata, sep='\t', dtype='unicode')
    maincode = 'Code'
    #df = adjustdataframe(dataframe)
    #df.index = df[maincode]
    #print df.index
    return df

def loaddataset_fromurl(apiroot, handle):
    url = apiroot + "/api/datasets?handle=Panel[%27" + handle + "]&format=csv"
    res = requests.get(url)
    csvio = StringIO(res.content)
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    df = ''
    
    # Classification (None|Modern|Historical)
    classtype = 'None'
    maincode = 'Code'
    webmappercode = 'Webmapper numeric code'
    if maincode in dataframe:
	classtype = 'modern'
        df = adjustdataframe(dataframe)    
        df.index = df[maincode]    

    if classtype == 'None':
        if webmappercode in dataframe:
	    classtype = 'historical'
	    df = dataframe
            df.index = df[webmappercode]
        
    return (classtype, df)
