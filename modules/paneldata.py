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

def panel2dict(cleanedpaneldata):
    data = cleanedpaneldata.reset_index().to_dict()
    codes = data['Code']
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
        header = header + str(handle) + ','
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

