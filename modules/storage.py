#!/usr/bin/python

from pymongo import MongoClient
import sys
import datetime

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
    collection = db.test
    try:
        result = db.test.find({key: val})
    except:
	result = ''

    return result


