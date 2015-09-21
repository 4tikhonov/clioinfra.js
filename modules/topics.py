import urllib2 
import simplejson
import json
import sys
import pandas as pd
import random
import vincent
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from pandas.io.json import json_normalize
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
import re

def loadjson(apiurl):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def topics_parser(alltopics):
    topics = {}
    indicators = {}
    topic2inds = {}
    indline = []
    for item in alltopics:
        #print item
        name = item['Name']
        thisid = int(item['ID'])
        pcode = item['parent ID']
        
        if not pcode:
            topics[name] = thisid
        else:
            indicators[thisid] = name
            
            try:
                indline = topic2inds[pcode]
            except:
                indline = []
                
            indline.append(thisid)
            topic2inds[int(pcode)] = indline
            
    return (topics, indicators, topic2inds)        
        
def load_alltopics(api, branch):
    result = loadjson(api)
    (topics, indicators, topic2inds) = topics_parser(result)
    datasets = dataverse2indicators(branch)

    html = ''
    for topic in sorted(topics):
        topicID = topics[topic]
        html = html + "<optgroup label=\"" + str(topic) + "\">\n"
        indlist = topic2inds[topicID]
        for ind in indlist:
            indicator = indicators[ind]
            try:
                showind = datasets[indicator]
            except:
                showind = ind
	
	    html = html + "\t<option value=\"" + str(showind) + "\">" + indicator + "</option>" + "\n"
        html = html + "</optgroup>\n" 
    return html

