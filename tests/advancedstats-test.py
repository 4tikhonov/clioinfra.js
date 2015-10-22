#!/usr/bin/python

import urllib2 
import simplejson
import json
import pandas as pd
import re
import numpy as np
import ast
import sys
import os
#from pandas.io.json import json_normalize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from advancedstatistics import loadpanel, data2statistics, read_measure, statistics_tojson, advpanel2dict
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel,  moderncodes
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata
from historical import load_historical, histo
from paneldata import panel2dict, paneldatafilter, panel2csv

def test_stats():
    thisyear = 2010
    jsonapi = "http://dpe.sandbox.socialhistoryservices.org/api/datasets?handle=Panel[%27hdl%3A10622/4X6NCK%27%2C%20%27hdl%3A10622/I0YK5M%27%2C%20%27hdl%3A10622/ZWRBOY%27]"
    yearmin = '1990'
    yearmax = '2010'
    ctrlist = ''
    config = configuration()
    modern = moderncodes(config['modernnames'], config['apiroot'])

    (panel, cleanedpanel) = loadpanel(jsonapi, yearmin, yearmax, ctrlist)
    (header, data, countries, handles, vhandles) = advpanel2dict(cleanedpanel)           
    
    ctrlimit = 200
    #result = panel2csv(header, data, thisyear, countries, handles, vhandles, ctrlimit, modern)
    maindataframe = data2statistics(handles, cleanedpanel)
    showhtml = statistics_tojson(maindataframe, modern)
    return showhtml

showhtml = test_stats()
print showhtml