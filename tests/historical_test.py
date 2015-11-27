#!/usr/bin/python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from historical import load_historical, histo
api = "http://dpe.sandbox.socialhistoryservices.org/collabs/static/data/historical.json"
html = load_historical(api)
print html
#(regions, countries, ctr2reg) = histo(api)
#print countries[528]
