#!/usr/bin/python

import xlsxwriter
import xlwt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata
from historical import load_historical, histo
from data2excel import panel2excel

hist = {}
handles = ["4X6NCK", "F16UDU","ZWRBOY"]
customyear = ''
fromyear = '1990'
toyear = '2000'
customcountrycodes = '380,250,276,804,174,108,232,528,756'
logflag = 0
thisdir = '.'
fullmetadata = {}
pidslist = "4X6NCK,ZWRBOY"
finaldir = '.'
filename = 'test.xls'

config = configuration()
if fromyear:
    historical = 0
    if historical:
        api = config['apiroot'] + "/collabs/static/data/historical.json"
        (regions, countries, ctr2reg) = histo(api)
        hist = countries

    (header, panelcells, codes, x1, x2, x3, x4) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logflag)
    f = "panel.xlsx"
    if pidslist:
        fullmetadata = load_fullmetadata(pidslist)
    fullpath = panel2excel(finaldir, filename, header, panelcells, fullmetadata)
    for year in panelcells:
	print year
    print x4
