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

def histregions_parser(locations, cfilter):
    regions = {}
    countries = {}
    ctr2reg = {}
    oecd2webmapper = {}
    geocoder = []
    for item in locations:
	geoitem = {}
        if item['ctr']:
            try:
                ccode = int(item['ccode'])
                pcode = int(item['parent code'])
		gcode = item['geoinfra_id']
		if gcode:
    		    result = re.search('(\d+)', gcode)
    		    if result:
        		geoid = result.group(0)
    		    else:
        		geoid = country
		geoitem['id'] = geoid
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
	geoitem['name'] = country	
        # Found time
        try:
            validfromtoken = item['validfrom']
            validtotoken = item['validuntil']
            fromre = re.search(r'\d{4}', validfromtoken)
            validfrom = fromre.group(0)
            tore = re.search(r'\d{4}', validtotoken)
            validto = tore.group(0)
	    geoitem['label'] = country + ' (' + validfromtoken + ' - ' + validtotoken + ')' 
            country = country + ' (' + str(validfrom) + '-' + str(validto) + ')'
	    geoitem['validfrom'] = validfromtoken
	    geoitem['validuntil'] = validtotoken
	    geoitem['year'] = country
        except:
            validfrom = ''
	    geoitem['year'] = ''
            validto = ''
	    country = str(country) + ' (xxxx - 2012)'
            
        countries[ccode] = country
	if gcode:
	    oecd2webmapper[ccode] = gcode 
                
        try:
            if ctr2reg[pcode]:
                continent = ctr2reg[pcode]
        except:
            continent = []
                    
        continent.append(ccode)
        ctr2reg[pcode] = continent
	if cfilter:
    	    result = re.search(cfilter, country, flags=re.IGNORECASE)
    	    if result:
		if geoitem['year']:
	            geocoder.append(geoitem)
	else:
	    if geoitem['year']:
	        geocoder.append(geoitem)
    return (regions, countries, ctr2reg, oecd2webmapper, geocoder)

def load_historical(api):
    locs = loadjson(api)
    (regions, countries, ctr2reg, webmapper, geocoder) = histregions_parser(locs, '')

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
    
def histo(api, cfilter):
    locs = loadjson(api)
    (regions, countries, ctr2reg, webmapper, geocoder) = histregions_parser(locs, cfilter)
    
    return (regions, countries, ctr2reg, webmapper, geocoder)
    
