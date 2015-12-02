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
from datacompiler import dataframe_compiler

config = configuration()
datafilter = {}
datafilter['startyear'] = '1500'
datafilter['endyear'] = '2010'
datafilter['ctrlist'] = ''
datafilter['ctrlist'] = '528,14,18,67'
handle = "hdl:10622/WNGZ4A"
switch = 'historical'
fullpath = ''

a = datetime.now()
(outfile, finalsubset) = dataframe_compiler(config, fullpath, handle, switch, datafilter)
b = datetime.now()
d = b - a
print "Time: " + str(d.seconds) + " seconds"
print finalsubset.ix[67][1831]

