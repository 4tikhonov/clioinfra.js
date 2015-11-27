#!/usr/bin/python
import random, string
import os
import sys
import errno
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration
from search import dataset_search, getindicators, loadjson
from historical_data import get_info, dataframe_filter, match_geocoders, save_historical_dataset, datasetreader, produce_historicaldata 

config = configuration()
handle = "hdl:10622/MRPFJ0"
dataset = datasetreader(handle, config)
clioframe = pd.DataFrame(dataset)

codes = ['1498', '871', '1501']
codes = ['1']
maincode = 'Webmapper numeric code'
limityear = '2012'
fullpath = "historicaltemplate_random.xlsx"
excel = produce_historicaldata(config, fullpath, clioframe, codes, maincode, limityear)
