#!/usr/bin/python

import urllib2 
import simplejson
import json
import pandas as pd
import re
import numpy as np
import ast
import sys
import os
#from pandas.io.json import json_normalize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from advancedstatistics import loadpanel, data2statistics, read_measure, statistics_tojson, panel2dict
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel,  moderncodes
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata
from historical import load_historical, histo
from paneldata import panel2dict, paneldatafilter, panel2csv

def test_stats():
    jsonapi = "http://dpe.sandbox.socialhistoryservices.org/api/datasets?handle=Panel[%27hdl%3A10622/4X6NCK%27%2C%20%27hdl%3A10622/I0YK5M%27%2C%20%27hdl%3A10622/ZWRBOY%27]"
    yearmin = '1990'
    yearmax = '2010'
    ctrlist = ''
#    ctrlist = '76,578,620,554'

    dataframe = load_api_data(jsonapi, '')

    allcodes = {}
    panel = []
    for dataitem in dataframe: 
        handle = dataitem['handle']        
        (dataset, codes) = paneldatafilter(dataitem['data'], int(yearmin), int(yearmax), ctrlist, handle)    
        if not dataset.empty:                
            panel.append(dataset)
    return panel

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
                    
def statistics_tojson(maindataframe, modern):
    html = '<table border=1 style="border: solid 0.5px;">'
    codehtml = ''
    codehtml = codehtml + '<tr>'

    for handle in maindataframe:
        infodata = maindataframe[handle]
	datahtml = ''
        htmlhandle = "<tr><td>" + str(handle) + "</td><td>Country</td>"
	code = 76
	m = infodata[code]
	for measure in sorted(m):
	    htmlhandle = htmlhandle + "<td>" + str(measure) + "</td>"        
	htmlhandle = htmlhandle + "</tr>"

        codehtml = ''
        for code in infodata:
	    noname = ''
	    try:
	        country = str(modern[code])
	    except:
	 	country = str(code)
		noname = 1

	    active = 0
            countryitem = "<tr><td>&nbsp;</td>\n\t<td>" + country + "</td>\n"
            data = infodata[code]
            minvalue = read_measure('Mean', data)              
            if minvalue != None:
                for measure in sorted(data):            
                    values = {}      
                    value = ''
                    try:
                        values = json.loads(data[measure])
                        for x in values:
                            value = values[x]
                    except:
                        value = data[measure]       

		    if not value:
			value = "&nbsp;"
                    countryitem = countryitem + "\t<td>" + str(value) + "</td>\n"      
		    active = 1
            
            if active:                
		if noname:
                    datahtml = datahtml + countryitem + "</tr>\n"   

       	htmlhandle = htmlhandle + datahtml
        html = html + htmlhandle 
    html = html + "</table>"
    return html

def panel2dict(data):
    data = cleanedpanel.reset_index().to_dict()
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
    header = header + str('Year')
    
    return (header, data, countries, handles, vhandles) 
        
panel = test_stats()
if panel:
    totalpanel = pd.concat(panel)
    cleanedpanel = totalpanel.dropna(axis=1, how='any')
    cleanedpanel = totalpanel

thisyear = 2010
config = configuration()
modern = moderncodes(config['modernnames'], config['apiroot'])
(header, data, countries, handles, vhandles) = panel2dict(cleanedpanel)           
ctrlimit = 200
result = panel2csv(header, data, thisyear, countries, handles, vhandles, ctrlimit, modern)
maindataframe = data2statistics(handles, cleanedpanel)
showhtml = statistics_tojson(maindataframe, modern)
print showhtml
