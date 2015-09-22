#!/usr/bin/python
import sys
sys.path.append('/home/strikes/clioinfra/modules')
from locations import load_locations
api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/dataframe94_0.json"
html = load_locations(api)
print html
