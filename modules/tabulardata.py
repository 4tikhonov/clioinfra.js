#!/usr/bin/python

import urllib2 
import simplejson
import json
import pandas as pd
import re
import vincent
import numpy as np
import sys
import os
import math
from pandas.io.json import json_normalize
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata

def load_api_data(apiurl, fileID):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f, "utf-8")
    return dataframe

def json_dict(sqlnames, jsondataname, data):
        jsonlist = []
        jsonhash = {}

        for valuestr in data:
            datakeys = {}
            for i in range(len(valuestr)):
               name = sqlnames[i]
               value = valuestr[i]
               datakeys[name] = value
               #print "%s %s", (name, value)
            jsonlist.append(datakeys)

        jsonhash[jsondataname] = jsonlist;
        json_string = json.dumps(jsonhash, encoding="utf-8", sort_keys=True, indent=4)

        return json_string

# Create json to fill up map
def data2json(modern, codes, panelcells):    
    lookup = {}
    color = '#1F78B4'
    dataitem = []
    dataset = {}
    
    for item in panelcells:         
        lookup[item[0]] = item
        
    for code in modern:
        country = modern[code]
        # Default
        value = 'NaN'
        thiscolor = '#ffffff'

        dataitem = {}
        if country in lookup:                        
            value = item[2]  
            thiscolor = color
        
        # Creating json dataset
        dataitem['value'] = value
        dataitem['color'] = thiscolor                
            
        if country:
            dataset[country] = dataitem
        
    return dataset

# Get all modern boundaries
def moderncodes(handle, apiroot):
    apifile = str(handle) + ".json"
    jsonapi = apiroot + "/collabs/static/data/" + apifile
    dataframe = load_api_data(jsonapi, '')
    loccodes = loadcodes(dataframe)
    return loccodes

def loadcodes(dataframe):
    clioframe = pd.DataFrame(dataframe)
    countries = clioframe[clioframe.columns[1]]
    codes = clioframe[clioframe.columns[0]]

    code2country = {}
    for i in range(len(codes)):
        code = codes[i]
        country = countries[i]
        code2country[code] = country
        
    return code2country
    
def countryset(countrieslist, codes):
    countries = []
    ctrlist = []
    clist = []
    dates = {}
    if countrieslist:
        countries = countrieslist.split(',')
        for c in sorted(countries):
            clist.append(str(c))
            try:
                ctrlist.append(codes[int(c)])
            except:
                ctrlist.append('Unknown')
    else:
        for c in sorted(codes):
            try:
                ctrlist.append(str(codes[c]))
            except:
                ctrlist.append('Unknown')
            
    dates["date"] = ctrlist
    return (clist, dates)

def createframe(indicator, loccodes, dataframe, customyear, fromY, toY, customctrlist, DEBUG):
    yearline = dataframe[1]
    measure = ''
    values = []
    allyears = []
    dframe = {}
    cframe = {}
    dates = {}
    
    (years, vocab) = ({}, {})
    for line in yearline:
        try:
            if not customyear:
                years[line] = int(yearline[line])
            elif int(customyear) == int(yearline[line]):
                years[line] = int(yearline[line])
            allyears.append(int(yearline[line]))
        except:
            if not indicator:
                indicator = line
                vocab[line] = yearline[line]

    counter = 0
    for line in dataframe:
        (country, itemID) = ('', 0)
        for item in sorted(line):
            #print str(itemID) + ' ' + str(line[item])
            
            row = []
            value = line[item]
            if not country:
                if itemID == 0:
                    country = value
                    indicator = item
                    if not measure:
                        if line[item] == 'Code':
                            measure = ' '
                        else:
                            measure = line[item]
            try:
                thisyear = years[item]      
                active = 0
                if int(country):
                    active = 1
                    
                # country filter
                if customctrlist:
                    active = 0
                    if str(country) in set(customctrlist):
                        active = 1
                        
                # years filter (from year)
                if active and fromY:
                    if int(thisyear) >= int(fromY):
                        active = 1                        
                    else:
                        active = 0
                        
                # years filter (to year)
                if active and toY:
                    if int(thisyear) <= int(toY):
                        active = 1                        
                    else:
                        active = 0
                                            
                if active:                    
                    try:
                        dataitem = dates[thisyear]
                    except:
                        dataitem = []
                                                
                    if value:
                        v = value
                    else:
                        #value = 'NaN'
			donothing = 1

                    if value:                        
                        dataitem.append(value)
                        dates[thisyear] = dataitem                                            
                        
                        #print str(thisyear) + ' ' + str(country) + ' ' + str(value) + '\n'
                        row.append(thisyear)
                        row.append(country)
                        row.append(indicator)
                        row.append(measure)                        
                        row.append(loccodes[country])                                                
                        row.append(country)
                        row.append(value)
                        if value:
                            values.append(value)
                        row.append(counter)
                        counter = counter + 1                                                
                        
            except:
                do = 1
                if DEBUG:
                    print line[item]
                    
            itemID = itemID + 1
            if row:                                
                theyear = int(row[0])
                code = int(row[1])        
                try:
                    dframe = cframe[theyear]
                except:
                    dframe = []
                   
                dframe.append(row)
                cframe[theyear] = dframe            
    
    sortyears = sorted(allyears)
    return (cframe, sortyears, values, dates)

def combinedata(countries, dataset, code2loc):
    datastring = ''
    aggrstring = 'date,value\n'
    aggrvalue = 0
    aggr = {}
    # Plot header
    datastring = 'date\t'
    if datastring:
        for code in sorted(countries):
            try:
                ctr = code2loc[int(code)]
                datastring = datastring + str(ctr) + '\t'
            except:
                ctr = str(code)            
    datastring = datastring + '\n'
    
    # Plot data
    for year in sorted(dataset):
        dataframe = dataset[year]
        datastring = datastring + str(year) + '\t'   
        
        for code in sorted(countries):  
            country = ''
	    foundloc = 0
            for dataitem in dataframe:
                value = dataitem[6] 
                country = int(dataitem[1])
                                
                if int(code) == country:
                    datastring = datastring + ' ' + str(value) + '\t'
		    foundloc = 1
                    try:
                        aggr[year] = aggr[year] + value
                    except:
                        aggr[year] = value                

	    # No data for country
	    if foundloc < 1:
		ctr = ''
		try:
		    ctr = code2loc[int(code)]
		    value = 'NaN'
		    datastring = datastring + ' ' + str(value) + '\t'
		    aggr[year] = value
		except:
		    nocountry = 1
                    
        datastring = datastring + '\n'        
            
    for year in sorted(aggr):
        aggrstring = aggrstring + str(year) + ',' + str(aggr[year]) + '\n'
        
    return (datastring, aggrstring)

def tableapis(handle, customcountrycodes, fromyear, toyear, customyear):
    # years in filter
    config = {}
    indicator = ''
    config = configuration()
    DEBUG = 0

    apifile = str(handle) + ".json"
    jsonapi = config['apiroot'] + "/collabs/static/data/" + apifile
    dataframe = load_api_data(jsonapi, '')
    loccodes = loadcodes(dataframe)
    (ctr, header) = countryset(customcountrycodes, loccodes)
    (frame, years, values, dates) = createframe(indicator, loccodes, dataframe, customyear, fromyear, toyear, ctr, DEBUG)
    names = ['indicator', 'm', 'ctrcode', 'country', 'year', 'intcode', 'value', 'id']

    (csvdata, aggrdata) = combinedata(ctr, frame, loccodes)

    return (years, frame, csvdata, aggrdata)

def data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logflag):
    data = {}
    for handle in handles:
        (y, frame, csvdata, aggrdata) = tableapis(handle, customcountrycodes, fromyear, toyear, customyear)
        data[handle] = frame
    
    datahub = {}
    countryhub = {}
    datapanel = {}
    handle2ind = {}
    code2ctr = {}
    unit2ind = {}
    for handle in data:
	try:
            item = data[handle]
	except:
	    item = {}

        for year in item:
            values = item[year]
        
            try:
                dhub = datahub[year]
            except:
                dhub = []
            
            for x in values:
                country = x[4]
                code = x[5]
                code2ctr[code] = country
                datayear = x[0]
                indicator = x[2]
                value = x[6]
		unit2ind[handle] = x[3]
            
		# If log scale
		if logflag:
		    value = math.log(value)

                # Combine key
                datakey = str(code) + ':' + str(year) + ':' + str(handle)
                datapanel[datakey] = value

                handle2ind[handle] = indicator
                countryhub[code] = country
                datahub[year] = countryhub

    # Header
    headers = 'Country,Year,'
    header = ['Country', 'Year']
    for handle in data:
	try:
            indicator = handle2ind[handle]
            headers = headers + str(indicator) + ','
            header.append(str(indicator))
	except:
	    notfound = 1
    
    #print header
    panelcells = []
    for code in sorted(countryhub):
        xcell = []
        cell = []
        xcell.append(country)
        for year in sorted(datahub):        
            xcell.append(year)
            pindex = str(code) + ':' + str(year)
            selcountry = code
            # Historical classification
            if hist:
                try:
                    selcountry = hist[int(code)]
                except:
                    missing = 1
            else:
            # Modern classification
                try:
                    selcountry = code2ctr[code]
                except:
                    selcountry = code
                
            cell = [selcountry, year]
            for handle in data:
                datakey = str(pindex) + ':' + str(handle)
                indicator = handle2ind[handle]
                try:
                    value = datapanel[datakey]
                except:
                    value = ''
            
                cell.append(value)
                #print '\t' + str(indicator) + ':' + str(value)
                
            panelcells.append(cell)

    return (header, panelcells, code2ctr, datahub, data, handle2ind, unit2ind)

