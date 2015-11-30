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
handles = ["hdl:10622/GDAO0N"]
logflag = 0
config = configuration()

if fromyear:
    historical = 0
    if historical:
        api = config['clearance'] + "/collabs/static/data/historical.json"
        (regions, countries, ctr2reg, webmapper, geo) = histo(api, '')
        hist = countries

    (header, panelcells, codes, datahub, data, handle2ind, unit2ind, original) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logflag)
    f = "panel.xlsx"
    #(handles, pidslist) = pidfrompanel(pid)
    pidslist = handles
    try:
        if pidslist:
            fullmetadata = load_fullmetadata(pidslist)
    except:
	fullmetadata = ''
    # Create panel
    panel2excel(config['tmpdir'], f, header, panelcells, fullmetadata)

# Create individual files 
for pid in handles:
    testfile = 'test1.xls'    
    print data[pid]
    individual_dataset(config['tmpdir'], testfile, handle2ind[pid], unit2ind[pid], datahub, data[pid], codes, fullmetadata)

