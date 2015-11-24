#!/usr/bin/python

import urllib2 
import simplejson
import json
import sys
import pandas as pd
import numpy as np
import random
import vincent
import sys
import os
from vincent import Axis, AxisProperties, PropertySet, ValueRef
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from pandas.io.json import json_normalize
import re
import openpyxl
from openpyxl.cell import get_column_letter
import requests
from StringIO import StringIO

url = "http://dpe.sandbox.socialhistoryservices.org/api/datasets?handle=Panel[%27hdl:10622/MRPFJ0:243:244%27]&format=csv"
onlinetest = ''

if onlinetest:
    res = requests.get(url)
    csvio = StringIO(res.content)
    dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
    print dataframe.to_html
else:
    handles = []
    handle = "hdl:10622/MRPFJ0"
    handles.append(handle)
    hquery = formdatasetquery(handles,'')
    print hquery
    d = readdatasets('datasets', json.loads(hquery))
    for x in d:
        csvframe = StringIO(x['csvframe'])
        dataframe = pd.read_csv(csvframe, sep='\t', dtype='unicode')
        print dataframe.to_html


