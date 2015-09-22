#!/usr/bin/python

import urllib2 
import simplejson
import json
import pandas as pd
import re
import vincent
from pandas.io.json import json_normalize

def load_api_data(apiurl, fileID):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f, "utf-8")
    return dataframe
    
def json_list(datacontainer, data):
        jsonlist = []
        jsonhash = {}

        jsonhash[datacontainer] = data
        json_string = json.dumps(jsonhash, encoding="utf-8", sort_keys=True, indent=4)

        return json_string
    

# <codecell>

def extract_boundaries(clioframe):
    index = 1
    histboundaries = {}

    countries = []
    for name in clioframe[clioframe.columns[0]]:
        if name == 'Year':
            #print index 
            pindex = index - 1
            countriespd = clioframe.ix[pindex]
            countries = []
            i = 0
            for loc in countriespd:
                if i:
                    countries.append(loc)
                i = i + 1
        else:
	    checkyear = re.match(r'^\d{4}', str(name))
	    try:
	        if checkyear.group(0):
                    histboundaries[name] = countries
	    except:
	 	notyear = 1	

        index = index + 1
    return histboundaries

def data2json(histboundaries):
    jsonset = ''
    for year in histboundaries:
        try:
            year = int(year)
            loc = histboundaries[year]
            names = ['countries']
            jsondata = json_list(str(year), loc)
            if jsonset:
                jsonset = jsonset + '\n' + jsondata
            else:
                jsonset = jsondata
        except:
            noyear = 1
    return jsonset
            
def getboundaries(rootapi, dataset):
    countries = {}
    for id in range(1,4):
        datafile = dataset + str(id) + ".json"
        jsonapi = rootapi + "/collabs/static/data/" + datafile
        dataframe = load_api_data(jsonapi, '')

        clioframe = pd.DataFrame(dataframe)
        clioframe.head()
        hb = extract_boundaries(clioframe)
	if hb:
	    countries.update(hb)
    return countries 


