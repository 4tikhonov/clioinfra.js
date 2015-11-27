#!/usr/bin/python

import sys
import os
import pandas as pd
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata, pidfrompanel
from statistics import load_api_data
from paneldata import paneldatafilter, panel2dict, panel2csv
from tabulardata import moderncodes

config = configuration()
jsonapi = config['apiroot'] + "/api/datasets?handle=Panel[%27hdl%3A10622/4X6NCK%27%2C%20%27hdl%3A10622/F16UDU%27%2C%20%27hdl%3A10622/ZWRBOY]"
#hdl%3A10622/GDAO0N]"
yearmin = '1500'
yearmax = '2015'
x = ''
ctrlist = '380,250,52,850'
ctrlist = ''
result = ''
thisyear = 2010
ctrlimit = 10

modern = moderncodes(config['modernnames'], config['apiroot'])
dataframe = load_api_data(jsonapi, '')

if dataframe:
    allcodes = {}
    panel = []

    for dataitem in dataframe: 
        handle = dataitem['handle']        
        (dataset, codes) = paneldatafilter(dataitem['data'], int(yearmin), int(yearmax), ctrlist, handle)    
        if not dataset.empty:                
            panel.append(dataset)
        
    if panel:
        totalpanel = pd.concat(panel)
        cleanedpanel = totalpanel.dropna(axis=1, how='any')
        cleanedpanel = totalpanel

        (header, data, countries, handles, vhandles) = panel2dict(cleanedpanel)           
	print data
        result = panel2csv(header, data, thisyear, countries, handles, vhandles, ctrlimit, modern)
        print result
