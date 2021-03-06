#!/usr/bin/python
import urllib2 
import simplejson
import json
import sys
import pandas as pd
import random
import vincent
import os
import sys
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from pandas.io.json import json_normalize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), './modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from datasets import loaddataset, topicscoder
import re

def loadjson(apiurl):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def getindicators(url):
    ids = re.findall(r'i\[\d+\]\=(\d+)', url, re.M|re.I)
    return ids

def dataverse_search(apiurl):
    dataframe = loadjson(apiurl)
    config = configuration()
    topics = topicscoder(config)

    info = []
    tmpinfo = []
    panel = {}
    panel['url'] = 'url'
    panel['indicator'] = '<b>&nbsp;Panel data</b>'
    panel['description'] = '<b>&nbsp;All datasets in panel format</b>'
    panel['name'] = '&nbsp;Panel data'
    panel['topic'] = '<b>&nbsp;Selected topics</b>'
    panel['pid'] = 'Panel'
    panel['citation'] = 'citation'

    link = config['apiroot'] + "/collabs/dashboard?dataset="
    handles = []
    for item in dataframe['data']['items']:
        datasets = {}
        datasets['url'] = item['url']
        datasets['pid'] = item['global_id']
	handles.append(datasets['pid'])
        datasets['indicator'] = '&nbsp;' + item['name'] 
	try:
	    datasets['topic'] = '&nbsp;' + topics[item['name']]
	except:
            datasets['topic'] = '&nbsp;' + item['description'] 
	abstract = str(item['description'])
        resume = re.search(r'^(.+?\.)\s+', str(item['description']))
        if resume:
            abstract = resume.group(1)
        datasets['description'] = '&nbsp;' + abstract
        datasets['startyear'] = 1500
        datasets['endyear'] = 2010
	datasets['analyze'] = link + item['global_id'] + '&action=visualize'

        tmpinfo.append(datasets)
    
    panel['pid'] = 'Panel' + str(handles)
    info.append(panel)
    for data in tmpinfo:
	info.append(data) 

    return info

def dataset_search(root, IDS, topics):
    totalq = ''
    config = configuration()
    data = []
    for item in topics:
        thisid = str(item['ID'])

        if thisid in IDS:
            name = item['Name']
            topic = item['parent name']
            name = re.sub("\s+" , "\%20", name)
            totalq = totalq + 'title:%22' + name + '%22OR%20'
        
    if totalq:
        totalq = totalq + '"tttttt"'
        apiurl = root + "/api/search?q=" + totalq + "&key=" + config['key'] + "&type=dataset"
	print apiurl
        data = dataverse_search(apiurl)

    return data
