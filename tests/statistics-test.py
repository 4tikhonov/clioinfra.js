#!/usr/bin/python

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
import pandas as pd
from statistics import createdata

jsonapi = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/dataframe27_0.json"
data = createdata(jsonapi)
d = data.describe()
show = d.transpose()
print show.to_html()
