#!/usr/bin/python
import json
import sys
import os
import re
import simplejson
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
from datasets import loaddataset, loaddataset_fromurl, loadgeocoder, treemap, selectint, buildgeocoder, load_geocodes, datasetfilter, dataset_analyzer
from data2excel import create_excel_dataset
from sys import argv
from historical_data import save_historical_dataset
from random import randint
import openpyxl
from openpyxl.cell import get_column_letter
import numpy as np

def dataframe_compiler(config, fullpath, handle, switch, datafilter):
    handles = []
    remote = 'on'

    # Load Geocoder
    handle = config['geocoderhandle']
    if remote:
        (classification, dataset, title, units) = loaddataset_fromurl(config, handle)
    else:
        dataset = loaddataset(handles)

    (geocoder, geolist) = buildgeocoder(dataset, config, '')
    (modern, historical) = loadgeocoder(config, dataset, 'geocoder')
    coderyears = []
    for i in range(1500, 2015):
        coderyears.append(i)

    # Reading dataset
    if remote:
        (class1, dataset, title, units) = loaddataset_fromurl(config, handle)
    else:
        dataset = loaddataset(handles)

    if switch == 'modern':
        activeindex = modern.index
        coder = modern
        class1 = switch
    else:
        activeindex = historical.index
        coder = historical

    (moderndata, historicaldata) = loadgeocoder(config, dataset, '')
    if switch == 'modern':
        maindata = moderndata
    else:
        maindata = historicaldata

    (cfilter, notint) = selectint(maindata.columns)
    
    codes = selectint(maindata.index)
    geo = load_geocodes(config, switch, codes, maindata, geolist)
    for colname in notint:
        maindata = maindata.drop(colname, axis=1)

    # Apply filters
    datasubset = datasetfilter(maindata, datafilter)

    # Create Excel file out from dataframe
    (yearscolumns, notyears) = selectint(maindata.columns)
    (countryinfo, notcountry) = selectint(maindata.index)

    (finalsubset, icoder, isyear, ctrfilter, nodata) = dataset_analyzer(datasubset, coder, yearscolumns)
    datafile = create_excel_dataset(fullpath, icoder, metadata, icoder.columns, coderyears, finalsubset, isyear, ctrfilter)
    return (fullpath, finalsubset)
