#!/usr/bin/python
import sys
sys.path.append('/home/strikes/clioinfra/modules')
from historical import load_historical, histo
api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/historical.json"
#html = load_historical(api)
#print html
(regions, countries, ctr2reg) = histo(api)
print countries[528]
