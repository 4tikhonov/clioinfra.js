#!/usr/bin/python
import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata, pidfrompanel
from paneldata import build_panel
from data2excel import panel2excel

config = configuration()
handles = ['hdl:10622/2XMLW5', 'hdl:10622/SMIOST']
ctrlist = '1523,1525'
startyear = '1929'
endyear = '1955'
(header, panelcells, metadata, totalpanel) = build_panel(config, handles, startyear, endyear, ctrlist)
datadir = "/home/dpe/tmp"
filename = "paneltest.xlsx"
metadata = []
outfile = panel2excel(datadir, filename, header, panelcells, metadata)
print outfile
panelcells
