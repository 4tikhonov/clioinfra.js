#!/usr/bin/python

import urllib2 
import simplejson
import json
import sys
from pandas.io.json import json_normalize
import re

def loadjson(apiurl):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def years_per_dataset(url):
    data = loadjson(url)
    years = {}
    for item in data['years']:
        years[item['year']] = item['count']

    return years
