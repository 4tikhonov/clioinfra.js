#!/usr/bin/python

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse
from search import dataset_search, getindicators, loadjson

def search(qurl):
    # Global settings
    root = "http://dv.sandbox.socialhistoryservices.org"

    # Load topics
    topicurl = "http://dpe.sandbox.socialhistoryservices.org/collabs/static/data/dataframe100_0.json"
    topics = loadjson(topicurl)

    # Input
    IDS = getindicators(qurl)

    datasets = dataset_search(root, IDS, topics)
    return datasets

qurl = "http://dpe.sandbox.socialhistoryservices.org/api/dataverse?i[83]=11002&i[84]=10&i[85]=1199&i[86]=16002"
data = search(qurl)
print data
