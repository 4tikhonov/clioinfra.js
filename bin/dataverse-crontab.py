#!/usr/bin/python

import urllib2 
import simplejson
import json
from dataverse import Connection
import sys
import os
from subprocess import Popen, PIPE, STDOUT
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration

def loadjson(apiurl):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

config = configuration()

connection = Connection(host, token)
dataverse = connection.get_dataverse('clioinfra')

for item in dataverse.get_contents():
    # u'protocol': u'hdl', u'authority': u'10622' u'identifier': u'R8EJJF'
    try:
        handle = str(item['protocol']) + ':' + str(item['authority']) + "/" + str(item['identifier'])
        datasetid = item['id']
        url = "https://" + str(host) + "/api/datasets/" + str(datasetid) + "/versions/1.0?&key=" + str(token)
        print item
	dataframe = loadjson(url)
        for fileitem in dataframe['data']['files']:
	    runimport = os.path.abspath(os.path.join(os.path.dirname(__file__)))
	    runimport = str(runimport) + "/import.py -d 'https://" + str(host) + "' -H '" + str(handle) + ":" + str(datasetid) + ":" + str(fileitem['datafile']['id']) + "' -k " + str(token)
	    #print fileitem['datafile']['id']
            p = Popen(runimport, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            response = p.stdout.read()
	    print response
    except:
	skip = 1

