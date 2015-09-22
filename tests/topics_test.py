#!/usr/bin/python
import sys
sys.path.append('/home/strikes/clioinfra/modules')
from topics import load_alltopics
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/dataframe100_0.json"
branch = 'clio1clio'
html = load_alltopics(api, branch)
print html
