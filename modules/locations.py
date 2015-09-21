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

def regions_parser(locations):
    regions = {}
    countries = {}
    ctr2reg = {}
    for item in locations:
        if not item['ctr']:
            try:
                ccode = int(item['ccode'])
                pcode = int(item['pcode'])
            except:
                ccode = ''
                
            if ccode:               
                if pcode:
                    regions[item['country']] = ccode  
        else:
            try:
                ccode = int(item['ccode'])
            except:
                ccode = ''
                
            pcode = int(item['pcode'])
            country = item['country']
            countries[ccode] = country
                
            try:
                if ctr2reg[pcode]:
                    continent = ctr2reg[pcode]
            except:
                continent = []
                    
            continent.append(ccode)
            ctr2reg[pcode] = continent
    return (regions, countries, ctr2reg)

def load_locations(api):
    locs = loadjson(api)
    (regions, countries, ctr2reg) = regions_parser(locs)

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
