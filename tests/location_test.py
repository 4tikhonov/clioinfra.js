#!/usr/bin/python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from locations import load_locations
api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/dataframe94_0.json"
html = load_locations(api)
print html
