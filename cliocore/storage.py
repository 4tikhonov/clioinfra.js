#!/usr/bin/python

from pymongo import MongoClient
import sys
import datetime
import json
import re

class Storage:
    def __init__(self, dbname):
        client = MongoClient()
        db = client.get_database(dbname)
	self.connection = db
	self.result = ''
	self.resultarray = []
	self.handlequery = ''

    def search_by_key(self, field, keyword):
        if keyword:
            regx = re.compile(keyword, re.IGNORECASE)
            self.result = self.connection.data.find({field: regx}, {'handle': 1, 'title': 1, 'units': 1})

        return self.result

    def data2store(self, dbname, data):
        collection = self.connection.data
        data['date'] = datetime.datetime.utcnow()
        self.result = collection.insert(data)
        return self.result 

    def readdata(self, key, val):
       collection = self.connection.data
       try:
           result = collection.find({key: val})
       except:
	   result = ''
       return result

    def removedata(self, key, val):
       self.result = self.collection.remove({key: val})
       return self.result

    def datasetadd(self, filename, csvfile, handle, dataset, title, units, fileID):
       txt = open(filename)
       data = {}
       data['csvframe'] = ''
       data['handle'] = handle
       data['dataset'] = dataset
       data['title'] = title
       data['units'] = units
       data['datasetID'] = fileID
       data['data'] = '' # datasetjson
       data['len'] = 0
       if csvfile:
	   csvtxt = open(csvfile)
	   datasettext = str(csvtxt.read())
	   data['len'] = sys.getsizeof(datasettext)
	   data['csvframe'] = datasettext

       result = data2store(data)
       return result

    def readdataset(self, handle, dataset):
        if handle:
            storage = readdata('handle', handle)
        if dataset:
            storage = readdata('dataset', dataset)
        for item in storage:
            if item['data']:
	        self.resultarray.append(item['data'])
        return self.resultarray

    def readdatasets(self, query):
        result = self.connection.data.find(query)
        return result

    def formdatasetquery(self, handles, datasets):
        for handle in handles:
            hdict = "{\"handle\": \"" + str(handle) + "\"}"
            self.handlequery = self.handlequery + str(hdict) + ","
        for dataset in datasets:
	    hdict = "{\"dataset\": \"" + str(dataset) + "\"}"
            self.handlequery = self.handlequery + str(hdict) + ","

        self.handlequery = self.handlequery[:-1]
        self.handlequery = "{\"$or\": [%s]}" % str(self.handlequery)
        return self.handlequery
