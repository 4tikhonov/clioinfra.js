#!/usr/bin/python

import json
import sys
import os
import simplejson
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from sys import argv

script, filename = argv

#test = 'readproject'
#test = 'write'
test = 'readdataset'

# Read test
if test == 'readproject':
    x = readdata('projects', 'uri', 'laborconflicts')
    remove = ["date", "_id", "passwd"]
    for item in x:
        print item
        for r in remove:
            item[r] = ''
        jsondata = json.dumps(item)
        print jsondata
        for i in item:
            print i

handles = []
handlequery = ''
if filename:
    handle = "hdl:10622/4X6NCK"
    handles.append(handle)
#    handles.append(str(handle))
    handle = "hdl:10622/I0YK5M"
    #handle = "'hdl:10622/LFQJEM"
    dataset = 'I0YK5M'
    handle = "hdl:10622/CSNWOF"
    handles.append(handle)

hquery = formdatasetquery(handles,'')
#,'{ title: 1, units: 1}')
print hquery
x = json.loads(hquery)
#x = simplejson.load(hquery)
#d = readdatasets('datasets', json.loads(hquery))
print hquery
d = readdatasets('datasets', json.loads(hquery))
for x in d:
    print x['title']
    for i in x:
        print 'F' + str(x[i])

for dataset in d:
    print dataset['data']
#$datasetadd(filename, handle, dataset)
#d = readdataset(handle, '')
#for item in d:
#    print item['handle']

