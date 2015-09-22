#!/usr/bin/python

import xlsxwriter
import xlwt
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from historical import load_historical, histo
from data2excel import panel2excel, individual_dataset

hist = {}
handles = ["4X6NCK", "F16UDU","ZWRBOY"]
customyear = ''
fromyear = '1500'
toyear = '2000'
customcountrycodes = '380,250,276,804,174,108,232,528,756'
#customcountrycodes = '528,756'
handles = ["GDAO0N"]
handles = ["4X6NCK"]
years = 0

config = configuration()
if fromyear:
    historical = 0
    if historical:
        api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/historical.json"
        (regions, countries, ctr2reg) = histo(api)
        hist = countries

    (header, panelcells, codes, datahub, data, handle2ind, unit2ind) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist)
    for year in sorted(datahub):
	print year
