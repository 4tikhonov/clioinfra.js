#!/usr/bin/python

import sys
sys.path.append('/home/strikes/clioinfra/modules')
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata

def tableapi():
    # years in filter
    #host = "http://clearance.sandbox.socialhistoryservices.org"
    config = configuration()
    customyear = ''
    fromyear = '1800'
    toyear = '2000'
    customcountrycodes = '380,250,276,804'
    handle = "F16UDU"
    DEBUG = 0

    apifile = str(handle) + ".json"
    jsonapi = config['apiroot'] + "/collabs/static/data/" + apifile
    dataframe = load_api_data(jsonapi, '')
    loccodes = loadcodes(dataframe)
    (ctr, header) = countryset(customcountrycodes, loccodes)
    indicator = ''
    (frame, years, values, dates) = createframe(indicator, loccodes, dataframe, customyear, fromyear, toyear, ctr, DEBUG)
    names = ['indicator', 'm', 'ctrcode', 'country', 'year', 'intcode', 'value', 'id']

    (csvdata, aggrdata) = combinedata(ctr, frame, loccodes)

    return (csvdata, aggrdata)

(csvdata, aggrdata) = tableapi()
print csvdata
print aggrdata

