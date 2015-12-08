#!/usr/bin/python
import urllib2 
import math
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
    oecd = {}
    geocoder = geocoder.convert_objects(convert_numeric=True)
    geocoder.index = geocoder[config['webmappercode']]
    (cfilter, notint) = selectint(geocoder.index)
    
    i = 0
    for cID in cfilter:
        geoitem = {}
        geoitem['id'] = ''
	ignore = 0
	try:
            countryitem = geocoder.ix[cID]
	    mainID = int(geocoder.ix[cID][config['webmappercode']])
	    geoitem['id'] = int(geocoder.ix[cID][config['webmappercode']])
            geoitem['validfrom'] = int(geocoder.ix[cID]['start year']) 
            geoitem['validuntil'] = int(geocoder.ix[cID]['end year']) 
            years = '(' + str(int(geocoder.ix[cID]['start year'])) + '-' + str(int(geocoder.ix[cID]['end year'])) + ')'
            geoitem['label'] = geocoder.ix[cID][config['webmappercountry']] + ' ' + str(years)
            geoitem['year'] = str(geocoder.ix[cID][config['webmappercountry']]) + ' ' + years
            geoitem['name'] = str(geocoder.ix[cID][config['webmappercountry']])
	    geolist[int(geoitem['id'])] = geoitem['label']
	    try:
	        oecd[int(geocoder.ix[cID][config['webmapperoecd']])] = int(geoitem['id'])
		#oecd[cID] = cID
	    except:
		skipoecd = 'on'
	except:
	    ignore = cID
        
        if ignore == 0:
	    if query:
                result = re.search(query, geoitem['name'], flags=re.IGNORECASE)
                if result:
                    if geoitem['name']:
                        geodict.append(geoitem)        
            else:
	        if geoitem['id']:
                    geodict.append(geoitem)
        i = i + 1
        
    return (geodict, geolist, oecd)

# Geocoder vocabulary
def load_geocodes(config, switch, codes, maindata, geolist):
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

def loadgeocoder(config, dataset, action):
    (modern, historical) = ('', '')
    geocoder = dataset
    if action == 'geocoder':
        geocoder = dataset.iloc[:, 1:10]
    else:
        geocoder = geocoder.ix[3:]
    if action == 'test':
        return (geocoder, geocoder)
    geocoder = geocoder.convert_objects(convert_numeric=True)
    geocoder = geocoder.replace(r'', np.nan, regex=True)
    geocoder = geocoder.replace('NaN', np.nan, regex=True)
    if 'ccode' in geocoder:
        modern = geocoder[pd.notnull(geocoder['ccode'])]
	historical = geocoder
        modern.index = modern['ccode']
	historical.index = historical[config['webmappercode']]
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

def loaddataset(config, handle):
    handles = []
    handles.append(handle)
    hquery = formdatasetquery(handles,'')
    d = readdatasets('datasets', json.loads(hquery))
    alldata = ''

    for dataset in d:
        alldata = str(dataset['csvframe'])
	thishandle = dataset['handle']
	units = dataset['units']
	title = dataset['title']

    csvio = StringIO(str(alldata))
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    maincode = 'Code'
    #df = adjustdataframe(dataframe)
    #df.index = df[maincode]
    #print df.index
    return (dataframe, handle, title, units)

def loaddataset_fromurl(config, handle):
    url = str(config['apiroot']) + "/api/datasets?handle=Panel[%27" + handle + "]&format=csv"
    res = requests.get(url)
    csvio = StringIO(res.content)
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    df = ''
    return dataframe
    
def content2dataframe(config, handle):
    (title, units, df) = ('', '', '')
    if config['remote']:
	dataframe = loaddataset_fromurl(config, handle)
    else:
	(dataframe, handle, title, units) = loaddataset(config, str(handle))
	
    # Classification (None|Modern|Historical)
    classtype = 'None'
    maincode = config['moderncode']
    webmappercode = config['webmappercode']
    # Get title and units
    if not title:
        title = dataframe.columns[1]
        units = dataframe.ix[0][1]

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
        if webmappercode in dataframe[:2].values:
	    classtype = 'historical'
	    df = dataframe
	    df.columns = df.ix[1]
            df.index = df[webmappercode]
        
    return (classtype, df, title, units)

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

def datasetfilter(maindata, datafilter):
    yearsfilter = []
    ctrlist = []
    datasubset = ''

    if datafilter['ctrlist']:
        for ctrid in re.split(',', datafilter['ctrlist']):
            ctrlist.append(int(ctrid))
        if ctrlist:
            datasubset = maindata.ix[ctrlist]
    else:
        datasubset = maindata

    (years, notyears) = selectint(datasubset.columns)
    if years:
        datasubset.columns = years
        for thisyear in years:
            if thisyear >= int(datafilter['startyear']):
                if thisyear <= int(datafilter['endyear']):
                    yearsfilter.append(thisyear)

    if yearsfilter:
        datasubset = datasubset[yearsfilter]
    return (datasubset, ctrlist)

def dataset_analyzer(datasubset, coder, yearscolumns):
    xset = datasubset
    xrow = datasubset.T
    finalsubset = datasubset.replace(np.nan, '', regex=True)
    try:
        icoder = coder.ix[1:]
    except:
        icoder = coder
    removefields = ['start date', 'end date', 'ctr', 'code parent', 'country', 'webmapper code']
    for colname in removefields:
        if colname in icoder.columns:
            icoder = icoder.drop(colname, axis=1)
    icoder = icoder.replace(np.nan, '', regex=True)

    (isdata, nodata) = ([], [])
    isyear = pd.DataFrame(xset.sum()).T
    isctr = pd.DataFrame(xrow.sum())
    isctr = isctr.dropna()
    (ctrfilter, notint) = selectint(isctr.index)
    for year in yearscolumns:
        try:
            data = xset[year].values
        except:
            nodata.append(year)
    return (finalsubset, icoder, isyear, ctrfilter, nodata)

def request_datasets(config, switch, modern, historical, handles, geolist):
    (ispanel, dataframe, metadata) = ('', {}, {})    

    for handle in handles:
        metadataitem = {}
        (class1, dataset, title, units) = content2dataframe(config, handle)
	metadataitem['title'] = title
	metadataitem['units'] = units

        if switch == 'modern':
            activeindex = modern.index
            coder = modern
            class1 = switch
        else:
            activeindex = historical.index
            coder = historical

        (moderndata, historicaldata) = loadgeocoder(config, dataset, '')
        if switch == 'modern':
            maindata = moderndata
        else:
            # Do conversion to webmapper system
            if not historicaldata:
                maindata = moderndata
                webmapperindex = []
                for code in maindata.index:
                    try:
                        webmappercode = oecd2webmapper[int(code)]
                    except:
                        webmappercode = -1
                    webmapperindex.append(webmappercode)
                maindata.index = webmapperindex
                maindata = maindata[maindata.index > 0]
            else:
                maindata = historicaldata
    
        (cfilter, notint) = selectint(maindata.columns)
    
        codes = selectint(maindata.index)
        geo = load_geocodes(config, switch, codes, maindata, geolist)
        for colname in notint:
            maindata = maindata.drop(colname, axis=1)       
        # Drop num if in dataframe
        if '1' in maindata.columns:
            maindata = maindata.drop('1', axis=1)
        dataframe[handle] = maindata
	metadata[handle] = metadataitem
    
    return (dataset, dataframe, metadata)

def request_geocoder(config, buildvocabulary):
    # Geocoder
    (geocoder, geolist, oecd2webmapper) = ('', '', '')
    (classification, dataset, title, units) = content2dataframe(config, config['geocoderhandle'])

    dataset = dataset[1:]
    if buildvocabulary:
        (geocoder, geolist, oecd2webmapper) = buildgeocoder(dataset, config, '')
    (modern, historical) = loadgeocoder(config, dataset, 'geocoder')
    return (geocoder, geolist, oecd2webmapper, modern, historical)

def dataset2panel(config, totalpanel, geocoder, logscale):
    datapanel = []
    original = {}
    (codes, notcodes) = selectint(totalpanel.index)
    (years, notyears) = selectint(totalpanel.columns)

    for code in codes:
        for year in years:
            # ['France', 1901, 2826.0, 250]
            try:
                country = str(geocoder.ix[int(code)][config['webmappercountry']])
            except:
                country = 'Unknown country'
            value = totalpanel[year][code]
            if value:
                origvalue = value
		rvalue = "%.1f" % value
                if logscale:
                   try:
                       if logscale == '2':
                          value = math.log(value, int(logscale))
                       elif logscale == '10':
                          value = math.log10(value)
                       else:
                          value = math.log(value)
                          rvalue = "%.5f" % value
                   except:
                       value = 'NaN'
                       rvalue = 'NaN'
                       original[str(rvalue)] = origvalue
                else:
                   original[origvalue] = origvalue
	    original[str(value)] = origvalue
            dataitem = [country, int(year), value, int(code)]
	    # Ignore missing data
	    if str(value) != 'nan':
                datapanel.append(dataitem)

    return (datapanel, original)
