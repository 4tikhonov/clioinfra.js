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

def buildgeocoder(geocoder, config, query):
    geodict = []
    geolist = {}
    (cfilter, notint) = selectint(geocoder.index)
    
    i = 0
    for cID in cfilter:
        geoitem = {}
        countryitem = geocoder.ix[str(cID)]
        geoitem['id'] = geocoder.ix[str(cID)][config['webmappercode']]
        geoitem['validfrom'] = geocoder.ix[str(cID)]['start date'] 
        geoitem['validuntil'] = geocoder.ix[str(cID)]['end date'] 
        years = '(' + str(int(geocoder.ix[str(cID)]['start year'])) + '-' + str(int(geocoder.ix[str(cID)]['end year'])) + ')'
        geoitem['label'] = geocoder.ix[str(cID)]['country name'] + ' ' + str(years)
        geoitem['year'] = str(geocoder.ix[str(cID)][config['webmappercountry']]) + ' ' + years
        geoitem['name'] = str(geocoder.ix[str(cID)][config['webmappercountry']])
	geolist[int(geoitem['id'])] = geoitem['label']
        
        if query:
            result = re.search(query, geoitem['name'], flags=re.IGNORECASE)
            if result:
                if geoitem['year']:
                    geodict.append(geoitem)        
        else:
            geodict.append(geoitem)
        i = i + 1
        
    return (geodict, geolist)

# Geocoder vocabulary
def load_geocodes(switch, codes, maindata, geolist):
    geocodes = {}
    if switch == 'modern':
        for code in codes[0]:
            try:
                ctr = str(maindata.ix[code][config['webmappercountry']])            
            except:
                ctr = str(maindata.ix[code][config['moderncountry']])
            
            geocodes[int(code)] = ctr
    elif switch == 'historical':
        for code in codes[0]:
            ctr = geolist[code]            
            geocodes[int(code)] = ctr        
    return geocodes

# Select int values
def selectint(cols):
    (isint, notint) = ([], [])
    for colname in cols:
        tmpvar = ''
        try:
            tmpvar = int(colname)
            isint.append(tmpvar)
        except:
            notint.append(colname)
    return (isint, notint)

def loadgeocoder(dataset, action):
    (modern, historical) = ('', '')
    geocoder = dataset
    if action == 'geocoder':
        geocoder = dataset.iloc[:, 1:12]
    else:
        geocoder = geocoder.ix[3:]
    if action == 'test':
        return (geocoder, geocoder)
    geocoder = geocoder.convert_objects(convert_numeric=True)
    geocoder = geocoder.replace(r'', np.nan, regex=True)
    geocoder = geocoder.replace('NaN', np.nan, regex=True)
    if 'ccode' in geocoder:
        modern = geocoder[pd.notnull(geocoder['ccode'])]
        historical = geocoder[pd.isnull(geocoder['ccode'])]
        modern.index = modern['ccode']
    else:
	#geocoder = geocoder.ix[3:]
	modern = geocoder[pd.notnull(geocoder['Code'])]
	historical = []
	modern.index = modern['Code']  
    
    return (modern, historical)

def buildstatistics(config, dataset, classification):
    stats = {}
    cols = []
    newpanel = dataset
            
    (iscolumns, deletecolumns) = selectint(newpanel.columns)
    for colname in deletecolumns:
        newpanel = newpanel.drop(colname, axis=1)
        #newpanel = newpanel.ix[3:]
    #return (newpanel, stats)
    df = newpanel
    df = df.convert_objects(convert_numeric=True)
    df = df.replace(r'', np.nan, regex=True)
    sum_row = {col: df[col].sum() for col in df}
    #return (df, stats)
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

def countrystats(config, dataset, classification):
    stats = {}
    cols = []
    newpanel = dataset
    if classification == 'modern':
    # Delete all columns without data in modern classification
        newpanel = newpanel.drop(config['moderncode'], axis=1)
        newpanel = newpanel.drop('Continent, Region, Country', axis=1)
        if 'Unnamed: 0' in dataset:
            newpanel = newpanel.drop('Unnamed: 0', axis=1)
        if '1' in dataset:
            newpanel = newpanel.drop('1', axis=1)

    # Delete all extra columns without data
    elif classification == 'historical':
        newpanel = newpanel.drop(config['webmappercode'], axis=1)
        cols = newpanel.columns
        deletecolumns = []
        for colname in cols:
            year = ''
            try:
                year = int(colname) 
            except:
                deletecolumns.append(colname) 
        for colname in deletecolumns:
            newpanel = newpanel.drop(colname, axis=1)

    newpanel = newpanel.ix[3:]
    df = newpanel
    df = df.convert_objects(convert_numeric=True)
    df = df.replace(r'', np.nan, regex=True)
    #return (df, deletecolumns)
    sum_row = {col: df[col].sum() for col in df}
    #return (df, stats)
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

def loaddataset_fromurl(config, handle):
    url = str(config['apiroot']) + "/api/datasets?handle=Panel[%27" + handle + "]&format=csv"
    res = requests.get(url)
    csvio = StringIO(res.content)
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    df = ''
    
    # Classification (None|Modern|Historical)
    classtype = 'None'
    maincode = config['moderncode']
    webmappercode = config['webmappercode']

    # Look for code in the column names 
    if maincode in dataframe:
        classtype = 'modern'
        df = adjustdataframe(dataframe)
        df.index = df[maincode]

    # Check first rows if code is present there
    if classtype == 'None':
        if maincode in dataframe[:2].values:
	    classtype = 'modern'
            df = adjustdataframe(dataframe)    
            df.index = df[maincode]    

    if classtype == 'None':
        if webmappercode in dataframe:
	    classtype = 'historical'
	    df = dataframe
            df.index = df[webmappercode]
        
    return (classtype, df)

def treemap(config, dataset, classification, ctrfilter, coder):
    jsonresult = "{\n\"name\": \"treemap\",\n\"children\": [\n"
    (df, result) = buildstatistics(config, dataset, classification)
    for idc in result:
	active = 'yes'
	if ctrfilter:
	    active = 'no'
	    if int(idc) in ctrfilter:
	        active = 'yes'

	if active == 'yes':
            value = result[idc]
            try:
		(ctr, ctrID) = ('', 0)
	        if classification == 'modern':
		    ctrID = int(idc)
		else:
		    ctrID = int(idc)
	        if ctrID:
		    ctr = str(coder.ix[ctrID][config['webmappercountry']])
		if classification == 'historical':
		    ctr = str(ctr) + ' (' + str(int(coder.ix[ctrID]['start year'])) + '-' + str(int(coder.ix[ctrID]['end year'])) + ')'
                jsonresult = jsonresult + "\t{ \"name\": \"" + str(ctr) + "\", \"size\": " + str(value) + " },\n"
            except:
                skip = idc

    jsonresult = jsonresult[:-2]
    jsonresult = jsonresult + "\n]}"
    return jsonresult

