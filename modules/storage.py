#!/usr/bin/python

from pymongo import MongoClient
import sys
import datetime
import json

def data2store(dbname, data):
   client = MongoClient()
   db = client.get_database(dbname)
   collection = db.data
   data['date'] = datetime.datetime.utcnow()
   result = collection.insert(data)
   return result 

def readdata(dbname, key, val):
    client = MongoClient()
    db = client.get_database(dbname)
    collection = db.data
    try:
        result = db.data.find({key: val})
    except:
	result = ''

    return result

def removedata(dbname, key, val):
    client = MongoClient()
    db = client.get_database(dbname)
    collection = db.data
    try:
        result = db.data.remove({key: val})
    except:
        result = ''

    return result

def datasetadd(filename, handle, dataset, title, units):
    dbname = "datasets"
    txt = open(filename)
    data = {}
    data['handle'] = handle
    data['dataset'] = dataset
    data['title'] = title
    data['units'] = units
    datasettext = str(txt.read())
    datasetjson = json.loads(datasettext)
    data['data'] = datasetjson

    result = data2store(dbname, data)
    return result

def readdataset(handle, dataset):
    data = {}
    result = []
    if handle:
        storage = readdata('datasets', 'handle', handle)
    if dataset:
        storage = readdata('datasets', 'dataset', dataset)
    for item in storage:
        if item['data']:
            data = item
	    result.append(data)

    return result

def readdatasets(dbname, query):
    client = MongoClient()
    db = client.get_database(dbname)
    collection = db.data
    result = db.data.find(query)

    return result

def formdatasetquery(handles, datasets):
    handlequery = ''
    for handle in handles:
        hdict = "{\"handle\": \"" + str(handle) + "\"}"
        handlequery = handlequery + str(hdict) + ","
    for dataset in datasets:
	hdict = "{\"dataset\": \"" + str(dataset) + "\"}"
        handlequery = handlequery + str(hdict) + ","

    handlequery = handlequery[:-1]
    handlequery = "{\"$or\": [" + str(handlequery) + "]}"
    return handlequery
