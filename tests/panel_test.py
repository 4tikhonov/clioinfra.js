#!/usr/bin/python

import xlsxwriter
import xlwt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from historical import load_historical, histo
from data2excel import panel2excel

hist = {}
handles = ["4X6NCK", "F16UDU","ZWRBOY"]
customyear = ''
fromyear = '1500'
toyear = '2000'
customcountrycodes = '380,250,276,804,174,108,232,528,756'
#customcountrycodes = '528,756'

if fromyear:
    historical = 1
    if historical:
        api = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/historical.json"
        (regions, countries, ctr2reg) = histo(api)
        hist = countries

    (header, panelcells, codes) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist)
    f = "panel.xlsx"
    panel2excel(f, header, panelcells)
