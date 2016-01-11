#!/usr/bin/python
import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata, pidfrompanel
from paneldata import build_panel
from data2excel import panel2excel

config = configuration()
if config:
    handles = ['hdl:10622/2XMLW5', 'hdl:10622/SMIOST']
    handles = ['hdl:10622/4X6NCK', 'hdl:10622/CSNW0F'] #, 'hdl:10622/6FCHEF', 'hdl:10622/ZWRBOY']
    if handles[0]:
	ctrlist = '1523,1525'
 	ctrlist = '528'
	startyear = '1950'
	endyear = '1955'
	datafilter = {}
	datafilter['startyear'] = startyear
	datafilter['endyear'] = endyear
	datafilter['ctrlist'] = ctrlist
	switch = 'modern'
	(header, panelcells, metadata, totalpanel) = build_panel(config, switch, handles, datafilter)
	datadir = "/home/dpe/tmp"
	filename = "paneltest.xlsx"
	metadata = []
	outfile = panel2excel(datadir, filename, header, panelcells, metadata)
	print outfile
	print str(panelcells)
