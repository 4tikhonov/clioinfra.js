#!/usr/bin/python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from topics import load_alltopics
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/dataframe100_0.json"
branch = 'clio1clio'
html = load_alltopics(api, branch)
print html
