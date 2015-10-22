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

def advanced_statistics():
    handle = 'Panel[%27hdl%3A10622/4X6NCK%27%2C%20%27hdl%3A10622/I0YK5M%27%2C%20%27hdl%3A10622/ZWRBOY%27]'
    handle = "Panel['hdl:10622/4X6NCK', 'hdl:10622/F16UDU', 'hdl:10622/I0YK5M']"
    handle = handle.replace(" ", '')
    print handle
    yearmin = '1990'
    yearmax = '2010'
    ctrlist = ''
    ctrlist = '250,276'
    config = configuration()
    modern = moderncodes(config['modernnames'], config['apiroot'])
    jsonapi = config['apiroot'] + '/api/datasets?handle=' + str(handle)

    (panel, cleanedpanel) = loadpanel(jsonapi, yearmin, yearmax, ctrlist)
    (header, data, countries, handles, vhandles) = advpanel2dict(cleanedpanel)           
    
    ctrlimit = 200
    #result = panel2csv(header, data, thisyear, countries, handles, vhandles, ctrlimit, modern)
    maindataframe = data2statistics(handles, cleanedpanel)
    showhtml = statistics_tojson(maindataframe, modern)
    return showhtml

showhtml = advanced_statistics()
print showhtml
