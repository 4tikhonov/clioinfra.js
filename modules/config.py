#!/usr/bin/python

import urllib2 
import simplejson
import json
import pandas as pd
import re
import ConfigParser
import sys

def configuration():
   config = {}
   cpath = "/etc/apache2/clioinfra.conf"
   cparser = ConfigParser.RawConfigParser()
   cparser.read(cpath)
 
   path_items = cparser.items( "config" )
   for key, value in path_items:
	config[key] = value

   return config

def loadjson(apiurl):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def findpid(handle):
    ids = re.search(r'hdl\:\d+\/(\w+)', handle, re.M|re.I)
    (pid, fileid, revid, cliohandle, clearpid) = ('', '', '', '', '')
    if ids:
	clearpid = ids.group(0)
        pid = ids.group(1)
        files = re.search(r'hdl\:\d+\/\w+\:(\d+)\:(\d+)', handle, re.M|re.I)
        if files:
            fileid = files.group(1)
            revid = files.group(2)
            cliohandle = pid + str(fileid) + '_' + str(revid)
    return (pid, revid, cliohandle, clearpid)

def pidfrompanel(pid):
    # Check Panel
    pids = []
    (thispid, revpid, cliopid) = ('', '', '')
    match = re.match(r'Panel\[(.+)\]', pid)
    if match:
        pidstr = match.group(1)
        # Remove quotes
        clearpids = re.sub('["\']+', '', pidstr)
        ptmpids = clearpids.split(',')
        for fullhandle in ptmpids:            
            (thispid, revpid, cliopid, clearpid) = findpid(fullhandle)            
            pids.append(thispid)
    
    return pids

def load_dataverse(apiurl):
    dataframe = loadjson(apiurl)

    info = []
    # Panel
    panel = {}
    panel['url'] = 'url'
    panel['name'] = 'Panel data'
    panel['topic'] = 'Topic'
    panel['pid'] = 'Panel'
    panel['citation'] = 'citation'
    info.append(panel)

    for item in dataframe['data']['items']:
        datasets = {}
        datasets['url'] = item['url']
        datasets['pid'] = item['global_id']
        datasets['name'] = item['name']
        datasets['topic'] = item['description']
        datasets['citation'] = item['citation']
        info.append(datasets)
    
    return info

def load_metadata(dataset):
    config = configuration()
    (pid, fileid, cliohandle, clearpid) = findpid(dataset)
    data = {}
    if pid:
        query = pid
        apiurl = config['dataverseroot'] + "/api/search?q=" + query + '&key=' + config['key'] + '&type=dataset&per_page=1000'
        data = load_dataverse(apiurl)
    return (data, pid, fileid, cliohandle)

def dataverse2indicators(branch):
    config = configuration()
    rows = 10
    start = 0
    page = 1
    condition = True # emulate do-while
    datasets = {}
    while (condition):
        url = config['dataverseroot'] + '/api/search?q=*' + "&key=" + config['key'] + "&start=" + str(start) 
	#+ "&type=dataset"
        if branch:
            url = url + "&subtree=" + branch
        data = json.load(urllib2.urlopen(url))
        total = data['data']['total_count']
        for i in data['data']['items']:
            url = i['url']
            handles = re.search(r'(\d+)\/(\w+)', url, re.M|re.I)
            handle = ''
            if handles:
                handle = 'hdl:' + handles.group(1) + '/' + handles.group(2)
		handle = handle + ':114:115'
	    
            datasets[i['name']] = handle

        start = start + rows
        page += 1
        condition = start < total

    return datasets
