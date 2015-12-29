#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2 
import simplejson
import json
import pandas as pd
import re
import vincent
import numpy as np
import ast
from pandas.io.json import json_normalize
from datasets import loaddataset, request_geocoder, loaddataset_fromurl, request_datasets, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, content2dataframe, dataset_analyzer, dataset2panel
from data2excel import panel2excel

def build_panel(config, switch, handles, datafilter):

    (geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, '')
    
    (origdata, maindata, metadata) = request_datasets(config, switch, modern, historical, handles, geolist)
    (subsets, panel) = ({}, [])
    logscale = ''
    for handle in handles:    
        (datasubset, ctrlist) = datasetfilter(maindata[handle], datafilter)
        if not datasubset.empty:
            datasubset = datasubset.dropna(how='all')
            try:
                if np.nan in datasubset.index:
                    datasubset = datasubset.drop(np.nan, axis=0)
            except:
                skip = 'yes'

            datasubset['handle'] = handle
            metadata['url'] = 0
            panel.append(datasubset)
            subsets[handle] = datasubset 
            (panelcells, originalvalues) = dataset2panel(config, subsets[handle], historical, logscale)
        
    totalpanel = pd.concat(panel)
    try:
        if np.nan in totalpanel.index:
            totalpanel = totalpanel.drop(np.nan, axis=0)
    except: 
	skip = 'yes'

    if switch == 'historical':
        geocoder = historical
    else:
        geocoder = modern
    # Remove columns with empty years

    for colyear in totalpanel.columns:
        if totalpanel[colyear].count() == 0:
            totalpanel = totalpanel.drop(colyear, axis=1)

    (allyears, nyears) = selectint(totalpanel.columns)
    print totalpanel.index
    panels = []
    known = {}
    matrix = {}
    #return (str(totalpanel.to_html()), '', '', '')
    for code in totalpanel.index:
	try:
            country = geocoder.ix[int(code)][config['webmappercountry']]
	except:
	    country = ''

        for thisyear in allyears:
            thiskey = str(int(code)) + str(thisyear)
            
            if thiskey not in known:
                dataitem = [country]
                dataitem.append(thisyear)
                known[thiskey] = thisyear
		matrix[thiskey] = ''
        
                for handle in handles:
                    tmpframe = totalpanel.loc[totalpanel['handle'] == handle]
                    try:
                        thisval = tmpframe.ix[int(code)][thisyear]
			matrix[thiskey] = thisval
                    except:
                        thisval = ''
                    dataitem.append(thisval)
                    
		# Filter out np.NaN
		if str(thisval) != 'nan':
		    if country:
		        if matrix[thiskey]:
                            panels.append(dataitem)

    # Build header
    header = ['Country', 'Year']
    for handle in handles:
        header.append(metadata[handle]['title'])
    
    return (header, panels, metadata, totalpanel)

def paneldatafilter(dataframe, yearmin, yearmax, ctrlist, handle):        
    years = dataframe[1]    
    ctrfilter = []
    
    if ctrlist:
        countries = ctrlist.split(',')        
        for c in countries:
            ctrfilter.append(int(str(c)))
                
    active = {}
    for i in sorted(years, reverse=True):
        year = ''
        try:
            year = int(years[i])
        except:
            year = ''
            
        if year:
            active[i] = 0
            if year >= yearmin:                
                if year < yearmax:
                    active[i] = 1                    
        else:
            active[i] = 1

    newdata = []
    for item in sorted(dataframe, reverse=True):
        cells = []
        for i in item:            
            if active[i] > 0:                
                cells.append(item[i])
        newdata.append(cells)

    dataframe = newdata
    dataframe.pop(0)    
    strcolumns = dataframe[0]
    columns = []
    names = {}
    colid = 0
    for col in strcolumns:
        try:
            columns.append(int(col))
        except:
            columns.append(col)
        names[col] = colid
        colid = colid + 1
    columns.append('handle')
            
    dataframe.pop(0)    
    tmpdataset = []
    colid = 0
    for item in dataframe:    
        item.append(handle)
        codenum = names['Code']
        try:
            code = int(item[codenum])
        except:
            code = item[codenum]
                     
        if code in ctrfilter:
            tmpdataset.append(item)                        
        if not ctrfilter:
            tmpdataset.append(item)
        colid = colid + 1
           
    dataset = pd.DataFrame(tmpdataset, columns=columns)   
    data = dataset.drop('Continent, Region, Country', axis=1)
    codes = data['Code']
    data = data.set_index('Code')    
            
    return (data, codes)    

def panel2dict(config, cleanedpaneldata, names):
    #data = cleanedpaneldata.reset_index().to_dict()
    #codes = data['Code']
    data = cleanedpaneldata.to_dict()
    codes = []
    if 'Code' in cleanedpaneldata.columns:
        codes = data['Code']
    if config['webmappercode'] in cleanedpaneldata.columns:
        #(codes, notcodes) = selectint(cleanedpaneldata[config['webmappercode']])
	(codes, ncodes) = selectint(cleanedpaneldata.index)

    handlesdata = data['handle']
    handles = {}
    vhandles = {}
    for i in handlesdata:
        thishandle = handlesdata[i]
        try:
            hinfo = handles[thishandle]
        except:
            hinfo = []
        
        hinfo.append(i) 
        handles[thishandle] = hinfo
        for i in hinfo:
            vhandles[i] = thishandle

    rcodes = {}
    i = 0
    countries = {}
    for i in codes:
        code = codes[i]
        try:
            cdata = countries[code]
        except:
            cdata = []
        
        cdata.append(i)
        countries[code] = cdata
        rcodes[code] = i
        i = i +1

    panelout = {}
    header = 'Country,'
    for handle in handles:
        header = header + str(names[handle]) + ','
    #header = header + str('Year')
    
    return (header, data, countries, handles, vhandles) 

def panel2csv(header, data, year, countries, handles, vhandles, limit, codes):
    csvitem = ''    
    ctrid = 0
    #for year in data:
    if year:
        try:
            year = int(year)
            dataset = data[year]              
            for code in countries:            
		found = 0
                cols = countries[code]
		try:
		   thisname = codes[code]
		except:
		   thisname = code

		if ctrid < limit:
                    csvitem = csvitem + str(thisname) + ','            

                for thishandle in handles:     
                    defaultvalue = 'NaN'
                    value = defaultvalue
                    for i in cols:
                        tmphandle = vhandles[i]                    
                        thisvalue = ''                    
                        if thishandle == tmphandle:
                            try:
                                thisvalue = dataset[i]                                                        
				found = 1
                            except:
                                skip = 1
                            if thisvalue:                        
                                value = thisvalue                        
                            
                    #print "\t" + str(code) + ' ' + str(cols) + ' ' + str(thishandle) + ' ' + str(value)                    
		    if ctrid < limit:
                        csvitem = csvitem + str(value) + ','

		if ctrid < limit:
		    csvitem = csvitem[:-1]
                    csvitem = csvitem + "\n"
		if found:
		    ctrid = ctrid + 1
        except:
            skip = 1
    header = header[:-1]
    csvitem = header + "\n" + csvitem
    return csvitem

def data2statistics(handles, clearedpanel):
    maindataframe = {}
    for handle in handles:    
        newpanel = cleanedpanel[cleanedpanel['handle'] == handle]   
        newpanel = newpanel.drop('handle', axis=1)    
        cdataframe = {}
        for code in newpanel.index:
            data = {}
            arrdata = newpanel.ix[code]        
        
            ctrdata = pd.DataFrame(arrdata) 
            # Mean
            data['Mean'] = ctrdata.mean(axis=0).to_json()
            # Min
            data['Min'] = ctrdata.min(axis=0).to_json()
            # Min
            data['Max'] = ctrdata.max(axis=0).to_json()
            # Std
            data['Std'] = ctrdata.std(axis=0).to_json()
            # Count
            data['N'] = ctrdata.count(axis=0).to_json()
            # Yearmin 
            ymin = min(ctrdata.index)
            # Min
            ymax = max(ctrdata.index)        
            period = str(ymin) + '-' + str(ymax)        
            data['Period'] = period
            cdataframe[code] = data
        maindataframe[handle] = cdataframe
        
    return maindataframe

def read_measure(measure, data):
    value = ''
    if measure:            
        values = {}      
        value = ''
        try:
            values = json.loads(data[measure])
            for x in values:
                value = values[x]
        except:
            value = data[measure]            
            
    return value    
                    
def statistics_tojson(maindataframe):
    for handle in maindataframe:
        infodata = maindataframe[handle]
        print str(handle) 
        for code in infodata:
            print "\t" + str(modern[code]) 
            data = infodata[code]
            minvalue = read_measure('Min', data)            
            if minvalue != None:
                for measure in data:            
                    values = {}      
                    value = ''
                    try:
                        values = json.loads(data[measure])
                        for x in values:
                            value = values[x]
                    except:
                        value = data[measure]            
                        
                    print "\t\t" + str(measure) + "\t" + str(value) 
    return 'ok'
