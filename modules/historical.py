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

def histregions_parser(locations):
    regions = {}
    countries = {}
    ctr2reg = {}
    for item in locations:
        if item['ctr']:
            try:
                ccode = int(item['ccode'])
                pcode = int(item['parent code'])
            except:
                ccode = ''
                
            if ccode:               
                if pcode:
                    regions[item['parent name']] = int(item['parent code'])  
        else:
            try:
                ccode = int(item['ccode'])
            except:
                ccode = ''
                
        pcode = int(item['parent code'])
        country = item['country']
        # Found time
        try:
            validfromtoken = item['validfrom']
            validtotoken = item['validuntil']
            fromre = re.search(r'\d{4}', validfromtoken)
            validfrom = fromre.group(0)
            tore = re.search(r'\d{4}', validtotoken)
            validto = tore.group(0)
            country = country + ' (' + str(validfrom) + '-' + str(validto) + ')'
        except:
            validfrom = ''
            validto = ''
	    country = str(country) + ' (xxxx - 2012)'
            
        countries[ccode] = country
                
        try:
            if ctr2reg[pcode]:
                continent = ctr2reg[pcode]
        except:
            continent = []
                    
        continent.append(ccode)
        ctr2reg[pcode] = continent
    return (regions, countries, ctr2reg)

def load_historical(api):
    locs = loadjson(api)
    (regions, countries, ctr2reg) = histregions_parser(locs)

    html = ''
    for region in sorted(regions):
        pcode = regions[region]
        html = html + "<optgroup label=\"" + str(region) + "\">\n"
        if pcode:
            ctr = ctr2reg[pcode]
            for ccode in ctr:
                country = countries[ccode]
                html = html + "\t<option value=\"" + str(ccode) + "\">" + country + "</option>" + "\n"
        html = html + "</optgroup>\n" 
    return html
    
def histo(api):
    locs = loadjson(api)
    (regions, countries, ctr2reg) = histregions_parser(locs)
    
    return (regions, countries, ctr2reg)
    
