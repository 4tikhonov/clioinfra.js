# Copyright (C) 2015 International Institute of Social History.
# @author Vyacheslav Tykhonov <vty@iisg.nl>
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception, the copyright holders give permission to link the
# code of portions of this program with the OpenSSL library under certain
# conditions as described in each individual source file and distribute
# linked combinations including the program with the OpenSSL library. You
# must comply with the GNU Affero General Public License in all respects
# for all of the code used other than as permitted herein. If you modify
# file(s) with this exception, you may extend this exception to your
# version of the file(s), but you are not obligated to do so. If you do not
# wish to do so, delete this exception statement from your version. If you
# delete this exception statement from all source files in the program,
# then also delete it in the license file.

from flask import Flask, redirect, make_response, Response, render_template, request, send_from_directory
from twisted.web import http
import webbrowser
import json
import simplejson
import urllib2
import glob
import csv
import xlwt
import os
import sys
import psycopg2
import psycopg2.extras
import pprint
import collections
import ast
import getopt
import numpy as np
import stat
import pandas as pd
import random
import ConfigParser
from subprocess import Popen, PIPE, STDOUT
from random import randint
import brewer2mpl
import string
import pylab as plt
import re
from urllib import urlopen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from advancedstatistics import loadpanel, statistics2table, handle2statistics, data2statistics, read_measure, statistics_tojson, advpanel2dict
from search import dataset_search, getindicators, dataverse_search, loadjson
import random, string
from download import get_papers, dataset2zip, compile2zip
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel, moderncodes, data2json
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata, pidfrompanel
import matplotlib as mpl
from palettable.colorbrewer.sequential import Greys_8
from data2excel import panel2excel, individual_dataset
from historical import load_historical, histo
from scales import getcolors, showwarning, buildcategories, getscales, floattodec, combinerange, webscales
from storage import data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery
#from statistics import load_api_data
from paneldata import paneldatafilter, panel2dict, panel2csv

cpath = "/etc/apache2/strikes.config"

def connect(custom):
        cparser = ConfigParser.RawConfigParser()
	global datasettable;
	datasettable = "datasets.data"
        cparser.read(cpath)
        options = {}
        dataoptions = cparser.items( "dataoptions" )
        for key, value in dataoptions:
            options[key] = value

 	database = cparser.get('config', 'dbname')
  	if request.args.get('custom'):
	    database = cparser.get('config', 'customdbname')
	if custom:
	    database = cparser.get('config', 'customdbname')
        if request.args.get('db'):
            database = request.args.get('db')
	if request.args.get('handle'):
	    dataverse = request.args.get('handle')
	    datasettable = "datasets.data_" + dataverse

	conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (cparser.get('config', 'dbhost'), database, cparser.get('config', 'dblogin'), cparser.get('config', 'dbpassword'))

    	# get a connection, if a connect cannot be made an exception will be raised here
    	conn = psycopg2.connect(conn_string)

    	# conn.cursor will return a cursor object, you can use this cursor to perform queries
    	cursor = conn.cursor()

	if custom:
	    options = conn_string
	return (cursor, options)

def json_generator(c, jsondataname, data):
	sqlnames = [desc[0] for desc in c.description]
        jsonlist = []
        jsonhash = {}
        
        for valuestr in data:    
            datakeys = {}
            for i in range(len(valuestr)):
               name = sqlnames[i]
               value = valuestr[i]
               datakeys[name] = value
               #print "%s %s", (name, value)
            jsonlist.append(datakeys)
        
        jsonhash[jsondataname] = jsonlist;
        json_string = json.dumps(jsonhash, encoding="utf-8", sort_keys=True, indent=4)

        return json_string

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def is_location(param):
    flag = re.match(r"c\[\d+\]", param)
    try:
        true = flag.group(0)
    except:
        true = 0
        
    return true

# Download ZIP archive
def downloadzip(pid):
    DEBUG = 0
    (fullpath) = ('')
    fullmetadata = {}
    logscale = 0

    config = configuration() 
    API_TOKEN = config['key']
    HOSTNAME = config['dataverseroot']
    cmd = "--insecure -u " + API_TOKEN + ": " + HOSTNAME + "/dvn/api/data-deposit/v1.1/swordv2/statement/study/"
    tmpdir = config['tmpdir']
    filerandom = randomword(10)
    #filerandom = '12345'
    arc = "data" + filerandom + ".zip"
    filename = filerandom  
    finaldir = config['path'] + '/static/tmp'
    # ToDO
    if filename:
        finaldir = str(finaldir) + '/' + str(filename)
        tmpdir = str(tmpdir) + '/' + str(filename)

    try:
        os.mkdir(tmpdir)
        os.mkdir(finaldir)
    except: 
	donothing = 'ok'

    customyear = ''
    fromyear = request.args.get('y[min]')
    toyear = request.args.get('y[max]')
    historical = request.args.get('type[0]')
    (handles, pidslist) = pidfrompanel(pid)
    try:
        if pidslist:
	    fullmetadata = load_fullmetadata(pidslist)
    except:
	showwarning = 1	

    # Log scales switch
    if request.args.get('logscale'):
	logscale = 1

    # Select countries
    customcountrycodes = ''
    f = request.args
    for key in f.keys():
        if is_location(key):
            for value in sorted(f.getlist(key)):
                customcountrycodes = str(customcountrycodes) + str(value) + ','
    if customcountrycodes:
        customcountrycodes = customcountrycodes[:-1]
    
    if handles:
	if historical:
            api = config['apiroot'] + "/collabs/static/data/historical.json"
            (regions, countries, ctr2reg, webmapper, geocoder) = histo(api)
            hist = countries
	else:
	    hist = ''

        (header, panelcells, codes, datahub, data, handle2ind, unit2ind) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logscale)
	filename = filename + '.xls'
        fullpath = panel2excel(finaldir, filename, header, panelcells, fullmetadata)
    else:
	# Clio format download
	zipfile = get_papers(HOSTNAME, API_TOKEN, cmd, pid, tmpdir, arc, finaldir)
	(alonepid, revid, cliohandle, clearpid) = findpid(pid)
	if alonepid:
	    handles = [ clearpid ]

	for pid in handles:
            #api = config['apiroot'] + "/collabs/static/data/historical.json"
            #(regions, countries, ctr2reg, webmapper) = histo(api)
            #hist = countries
	    hist = ''
	    filename = filename + '.xls'
	    # 2DEBUG
	    (header, panelcells, codes, datahub, data, handle2ind, unit2ind) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logscale)
	    #codes = hist
	    #return str(fullmetadata)
	    metadata = fullmetadata
	    result = individual_dataset(finaldir, filename, handle2ind[pid], unit2ind[pid], datahub, data[pid], codes, metadata)

    try:
        for everypid in handles:
	    # Download papers
            zipfile = get_papers(HOSTNAME, API_TOKEN, cmd, everypid, tmpdir, arc, finaldir)
    except:
	nopapers = 1

    compile2zip(finaldir, arc)
    filename = arc
    return filename

def analyze_data(cursor, catnum):
        data = {}
        debug = ''
        query = "select value from " + datasettable + " WHERE 1 = 1 ";
        query = sqlfilter(query)
        if debug:
            print "DEBUG " + query + " <br>\n"
        query += ' order by id asc'
        if debug:
            return query

        # execute
        cursor.execute(query)
        i = 0
        values = []
        # retrieve the records from the database
        records = cursor.fetchall()
        for row in records:
                i = i + 1
                values.append(row[0])
                data[i] = row

        # Calculate ranges based on percentile
        qwranges = []
        finalcatnum = 0
        try:
            if values:
                df = pd.DataFrame(values)
                colormap = []
                p = buildcategories(catnum)
                result = percentile(df, p)
                # Trying to find right categories: 8, 7, ... 1
                for thiscat in reversed(range(catnum+1)):
                    if finalcatnum == 0:
                        if thiscat > 0:
                            p = buildcategories(thiscat)
                            finalcatnum = percentile(df, p)
        except:
            return 3

        return finalcatnum

def load_years(cursor):
        data = {}
        sql = "select * from datasets.years where 1=1";
	sql = "select year, count(*) as count  from " + datasettable + " where 1=1"
	sql = sqlfilter(sql)
	sql = sql + ' group by year order by year asc';
        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
	jsondata = json_generator(cursor, 'years', data)

        return jsondata

def sqlfilter(sql):
        items = ''
        sqlparams = ''

	for key, value in request.args.items():
	    #sql = sql + '  ' +key + '=' + value + '<br>'
            items = request.args.get(key, '')
            itemlist = items.split(",")
	    itemparams = ''
            for item in itemlist:
		#sql = sql + ' ' + item + ' = ' + '<br>' 
                sqlparams = "\'%s\'" % item
            #sqlparams = sqlparams[:-1]
	    if key != 'datarange':
		if key != 'output':
		    if key != 'custom':
		        if key != 'scales':
			    if key != 'categories':
			        if key != 'csv':
				    if key != 'db':
					if key != 'handle':
					    if key != 'colors':
                                                sql += " AND %s in (%s)" % (key, sqlparams)
	return sql

def tableapi():
    # years in filter
    config = configuration()
    customyear = ''
    fromyear = '1500'
    toyear = '2012'
    customcountrycodes = ''
    (aggr, logscale, dataset) = ('',0,'')

    # Select countries
    f = request.args
    for key in f.keys():
	if key == 'loc':
            for value in sorted(f.getlist(key)):
		if value:
		    customcountrycodes = str(customcountrycodes) + str(value) + ','
    if customcountrycodes:
        customcountrycodes = customcountrycodes[:-1]

    handle = "F16UDU"
    # HANDLE
    if request.args.get('handle'):
        handle = request.args.get('handle')
	(dataset, revid, cliohandle, clearpid) = findpid(handle)
    if request.args.get('dataset'):
        dataset = request.args.get('dataset')
    if request.args.get('ctrlist'):
	customcountrycodes = ''
        tmpcustomcountrycodes = request.args.get('ctrlist')
	c = tmpcustomcountrycodes.split(',')
	for ids in sorted(c):
	   if ids:
	       customcountrycodes = str(customcountrycodes) + str(ids) + ','
	customcountrycodes = customcountrycodes[:-1]

    if not customcountrycodes:
	customcountrycodes = '528'
    if request.args.get('yearmin'):
	fromyear = request.args.get('yearmin')
    if request.args.get('yearmax'):
	toyear = request.args.get('yearmax')
    if request.args.get('aggr'):
        aggr = request.args.get('aggr')
    # Log scales switch
    if request.args.get('logscale'):
        logscale = 1
    DEBUG = 0

    apifile = str(dataset) + ".json"
    jsonapi = config['apiroot'] + "/collabs/static/data/" + apifile
    dataframe = load_api_data(jsonapi, '')
    loccodes = loadcodes(dataframe)
    (ctr, header) = countryset(customcountrycodes, loccodes)
    indicator = ''
    (frame, years, values, dates) = createframe(indicator, loccodes, dataframe, customyear, fromyear, toyear, ctr, logscale, DEBUG)
    names = ['indicator', 'm', 'ctrcode', 'country', 'year', 'intcode', 'value', 'id']

    (csvdata, aggrdata) = combinedata(ctr, frame, loccodes)
    if aggr:
        csvdata = aggrdata

    return (csvdata, aggrdata)

def load_locations(cursor, year, indicator):
        data = {}

	sql = "select naam, amsterdam_code, year, count(*) from " + datasettable + " where 1=1 "
        limit = 0
	sql = sqlfilter(sql)
        sql = sql + ' group by naam, year, amsterdam_code'

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'locations', data)

        return jsondata

def list_topics(cursor):
	data = {}

	# Before the list of topics will be available a few sql statements should be run
	# update datasets.topics set count=subquery.as_count from (select code as as_code, count(*) as as_count from " + datasettable + " group by as_code) as subquery where topic_code=subquery.as_code;
  	#update datasets.topics set startyear=subquery.startyear from (select code as as_code, min(year) as startyear from " + datasettable + " group by as_code) as subquery where topic_code=subquery.as_code;
	# update datasets.topics set totalyears=subquery.total from (select count(DISTINCT year) as total, code as as_code from " + datasettable + " group by as_code) as subquery where topic_code=subquery.as_code;
	sql = "select topic_name, topic_code, count, startyear, totalyears from datasets.topics where startyear > 0 and active='yes' order by count desc"
        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        
        topics = {}
	maxvalue = -1
        for topic in data:
            topicdata = {}
            letter = 'A'
            for i, field in enumerate(columns):
                topicdata[field] = topic[i]
                if field == 'topic_code':
                    mletter = re.match("^(\w)", topicdata[field])
                    letter = mletter.group(0)
		if maxvalue == -1:
		    if field == 'count':
		 	findindex = columns.index('totalyears')
		        if topic[findindex] < 10:
			    maxvalue = topicdata[field] 
		            topicdata['max'] = maxvalue
            topicdata['letter'] = letter
	    topicdata['max'] = maxvalue
            topics[topicdata['topic_code']] = topicdata
            
        #jsondata = json_generator(cursor, 'topics', topics)
        jsondata = json.dumps(topics, encoding="utf-8", sort_keys=True, indent=4)

        return jsondata

def load_topics(cursor, year, indicator):
        data = {}

	sql = "select code, indicator, topic_name, count(*) as count from " + datasettable + " as d, datasets.topics as t where d.code=t.topic_code and t.active='yes' "
	limit = 0

	sql = sqlfilter(sql) 
	try:
            if limit:
                sql = sql + ' limit ' + str(limit)
	except:
	    limit = 0
	sql = sql + ' group by code, indicator, t.topic_name'

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'codes', data)
        
        return jsondata

def load_lonlat(cursor):
        data = {}
        sql = "select * from datasets.locations where 1=1"
        for key, value in request.args.items():
            #sql = sql + '  ' +key + '=' + value + '<br>'
            items = request.args.get(key, '')
            itemlist = items.split(",")
            itemparams = ''
	    locstr = ''
            for item in itemlist:
	 	locstr = locstr + "'" + item + "',"
	        #sql += " AND %s in (%s)" % (key, item)
	    locstr = locstr[:-1]
	    sql += " AND %s in (%s)" % (key, locstr)

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'locations', data)

        return jsondata

# Search API
def simplesearch(root, qurl, apiroot):
    # Load topics
    #topicurl = apiroot + "/collabs/static/data/dataframe100_0.json"
    topicurl = apiroot + "/api/datasets?handle=Panel[%27hdl:10622/0PCZX5%27]"
    topicsframe = loadjson(topicurl)
    for item in topicsframe:
	topics = item['data']

    # Input
    IDS = getindicators(qurl)

    datasets = dataset_search(root, IDS, topics)
    return datasets

def load_oecd(cursor):
        data = {}
        sql = "select * from datasets.oecd where 1=1"
        for key, value in request.args.items():
            #sql = sql + '  ' +key + '=' + value + '<br>'
            items = request.args.get(key, '')
            itemlist = items.split(",")
            itemparams = ''
            locstr = ''
            for item in itemlist:
                locstr = locstr + "'" + item + "',"
                #sql += " AND %s in (%s)" % (key, item)
            locstr = locstr[:-1]
            sql += " AND %s in (%s)" % (key, locstr)

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'oecd', data)

        return jsondata

def load_oecdregions(cursor):
        data = {}
        sql = "select * from datasets.oecdregionsVer1 where 1=1"
	groupby = ''
        for key, value in request.args.items():
            #sql = sql + '  ' +key + '=' + value + '<br>'
            items = request.args.get(key, '')
	    if key == 'groupby':
		groupby = items
            itemlist = items.split(",")
            itemparams = ''
            locstr = ''
            for item in itemlist:
                locstr = locstr + "'" + item + "',"
                #sql += " AND %s in (%s)" % (key, item)
            locstr = locstr[:-1]
            sql += " AND %s in (%s)" % (key, locstr)

        # execute
	if groupby == 'parent_name1':
	    sql = "select distinct " + groupby + ", parent_code1 from datasets.oecdregionsVer1";
	elif groupby == 'parent_name':
	    sql = "select distinct " + groupby + ", parent_code from datasets.oecdregionsVer1";
	elif groupby:
	    sql = "select distinct " + groupby + ", parent_code1 from datasets.oecdregionsVer1";
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'oecdregions', data)

        return jsondata

def load_indicators(filename):
    csvfile = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/data/" + filename
    ufile = urlopen(csvfile)
    data = pd.read_csv(ufile, delimiter='\t')
    df = data
    if csvfile:
        d = [
        dict([
        (colname, row[i])
        for i,colname in enumerate(df.columns)
        ])
        for row in df.values
        ] 
    
    return json.dumps(d)

def load_api_data1(apiurl, fileID):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f, "utf-8")
    return dataframe

def searchdata(query):
    searchapi = "http://dv.sandbox.socialhistoryservices.org/api/search?q=" + query + "&key=73883b6f-ca99-41b9-953a-b9f8be42723d"
    dataframe = load_api_data(searchapi, '')
    return json.dumps(dataframe)

def load_classes(cursor):
        data = {}
	sql = "select topic_code, topic_name from datasets.topics where 1=1"
        sql = sqlfilter(sql)

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'indicators', data)

        return jsondata

def load_regions(cursor):
        data = {}
        sql = "select * from datasets.regions where 1=1";
	sql = sqlfilter(sql)
	sql = sql + ';'
        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
	jsondata = json_generator(cursor, 'regions', data)

        return jsondata

def medianlimits(dataframe):
    scale = []
    frame1 = []
    frame2 = []
    avg = dataframe.median()
    for value in dataframe:
        if value <= avg:
            frame1.append(value)
        else:
            frame2.append(value)
    avg1 = pd.DataFrame(frame1).median()
    avg2 = pd.DataFrame(frame2).median()
    
    return (dataframe.min(), int(avg1), int(avg), int(avg2), dataframe.max())

def meanlimits(dataframe):
    scale = []
    frame1 = []
    frame2 = []
    avg = dataframe.mean()
    for value in dataframe:
        if value <= avg:
            frame1.append(value)
        else:
            frame2.append(value)
    avg1 = pd.DataFrame(frame1).mean()
    avg2 = pd.DataFrame(frame2).mean()

    return (dataframe.min(), int(avg1), int(avg), int(avg2), dataframe.max())

def round_it(x):
    g = round(x)
    if request.args.get('code'):
        m = r'LCI'
        isindex = re.match(m, request.args.get('code'))
        if isindex:
            g = float("{0:.5f}".format(x))
    return g



def grayify_cmap(cmap):
    """Return a grayscale version of the colormap"""
    cmap = plt.cm.get_cmap(cmap)
    colors = cmap(np.arange(cmap.N))
    
    # convert RGBA to perceived greyscale luminance
    # cf. http://alienryderflex.com/hsp.html
    RGB_weight = [0.299, 0.587, 0.114]
    luminance = np.sqrt(np.dot(colors[:, :3] ** 2, RGB_weight))
    colors[:, :3] = luminance[:, np.newaxis]
    
    return cmap.from_list(cmap.name + "_grayscale", colors, cmap.N)

def load_data(cursor, year, datatype, region, datarange, output, debug, dataframe, catnum, options, csvexport):
        data = {}
	colors = ['red', 'green', 'orange', 'brown', 'purple', 'blue', 'cyan']
	gcolors = ['#ffffff', '#f0f0f0', '#d9d9d9', '#bdbdbd', '#969696', '#737373', '#525252', '#252525']
	colormap = 'Paired'
	# D1
	#return ('test', 'test', 'test') 
 	#colormap = 'Green'
	if not catnum:
	    try:
	        catnumint = int(options['defaultcategories'])
	        if catnumint:
	    	    catnum = catnumint 
	    except:
	        catnum = 8
	bmap = brewer2mpl.get_map(colormap, 'Qualitative', catnum)
	colors = bmap.hex_colors
        if request.args.get('colors') == 'greyscale':
	    colors = gcolors
	#colors = mpl.colors.ListedColormap(palettable.colorbrewer.sequential.Grey8.mpl_colors)
	maxColor = 0

        # execute our Query
	#    for key, value in request.args.iteritems():
	#        extra = "%s<br>%s=%s<br>" % (extra, key, value)

        query = "select * from " + datasettable + " WHERE 1 = 1 ";
	if output:
 	    query = "select amsterdam_code, value from " + datasettable + " WHERE 1 = 1 ";
	
	query = sqlfilter(query)
        if debug:
            print "DEBUG " + query + " <br>\n"
        query += ' order by id asc'
	if debug:
	    return query 

        # execute
        cursor.execute(query)
	columns = [i[0] for i in cursor.description]
	thiscount = 0
	index = 0
	for col in columns:
    	   if col == 'value':
        	index = thiscount
    		thiscount = thiscount + 1

        # retrieve the records from the database
        records = cursor.fetchall()
        if csvexport:
            return (records, columns, '')

 	# Data upload
        i = 0
        values = []
        index = 6 
	if request.args.get('handle'):
	    index = 8
        for row in records:
                i = i + 1
		thisvalue = row[index]
                values.append(thisvalue)
                data[i] = row

	# Calculate ranges based on percentile
        qwranges = []
        if values:
            df = pd.DataFrame(values)
	    pval = 0
            colormap = []
	    known = []
            p = buildcategories(catnum)
            for i in p:
                val = round(np.percentile(df, i), 2)
		if request.args.get('code') == 'NLSTR':
		    val = round(np.percentile(df, i))
                qwranges.append(val)

	if request.args.get('code') == 'LCI04':
	    qwranges = defaultscales
	    colors = defaultcolors
	if request.args.get('code') == 'NLSTR':
	    colors = defaultcolors

	# Calculate real none repeatable ranges
        xranges = []
	realcat = 0
        for val in qwranges:
            if val in xranges:
                skip = 1
            else:
                xranges.append(val)
	 	realcat = realcat + 1

	if realcat < catnum:
            qwranges = xranges
	    catnum = realcat
	    newcolors = []
	    for cID, color in enumerate(colors):
	        if cID < catnum:
		    newcolors.append(color)
	    colors = newcolors
	# DBQ1
	#return ('test', 'test', 'test')

	#return (query, 'test', 'test')
	fulldata = {}
	fulldataarray = []
	#for i in xrange(cursor.rowcount):
	i = 0
	for dataline in records:
	    dataset = {}
	    index = 0
	    amscode = ''

	    LOCCODE = 'amsterdam_code'
	    if request.args.get('db'):
	        LOCCODE = 'location'
	    for item in dataline:
		fieldname = columns[index]
                #dataset[fieldname] = dataline[index]
		#if fieldname == 'value':
		#   value = float(dataline[index])
		if fieldname == LOCCODE:
		   amscode = str(dataline[index])
		elif fieldname == 'value':
		   # Round to 3 digits after dot
		   dataset[fieldname] = round_it(dataline[index])
		else:
		   dataset[fieldname] = dataline[index]
		k = item
		index = index + 1

	    # Select colors
	    #if datarange == 'random':
	        #colorID = randint(0, catnum)
		#dataset['color'] = colors[colorID]
	    #if datarange == 'binary':
		#colorID = 0
	        #dataset['color'] = colors[colorID]

	    if not datarange:
	        datarange = 'calculate'

	    if datarange == 'calculate':
		if dataset['value'] != 'NA':
		    colorID = 0 
		    dataset['color'] = colors[colorID]
		    dataset['r'] = 0
		    for validx in qwranges:
		        if dataset['value'] > validx:
			    dataset['r'] = validx
		            dataset['color'] = colors[colorID]	 
			colorID = colorID + 1

	    #return (json.dumps(colors), 'test')
	    try:
	        if amscode:
	            fulldata[amscode] = []
	            fulldata[amscode] = dataset
	        if dataset:
	            fulldataarray.append(dataset)
	    except:
		donothing = 1
	    i = i + 1
	#return (json.dumps(colors), 'test')
	#return json.dumps(fulldataarray)
	jsondata = json.dumps(fulldata, ensure_ascii=False, sort_keys=True, indent=4)

        row_count = 0
        i = 0
	values = []
	index = 6
	#activecolors = []
	#for i, color in enumerate(colors):
	#    if i < maxColor:
	#        activecolors.append(color)
	#catnum = maxColor
	#if maxColor:
	#    colors = activecolors
	# DBQW
	#return (str(maxColor), 'test')
	#return (json.dumps(qwranges), json.dumps(colors), catnum)

        for row in records:
                i = i + 1
		#row['color'] = 'red'
		values.append(row[index])
                data[i] = row
#               print row[0]
	#jsondata = json_generator(fulldataarray)
	if dataframe:
	    return (qwranges, colors, catnum)
	    df = pd.DataFrame(values)
	    colormap = []
	    p = buildcategories(catnum)
	    qw = []
	    for i in p:
    	   	val = round(np.percentile(df, i), 2)
    		qw.append(val)

	    if dataframe == 'mean':
	        colormap = meanlimits(df[0])
	    else:
		colormap = medianlimits(df[0])
	    #colormap = [0, 1, 2, 3]
	    return qw
	    #return json_generator(cursor, 'ranges', colormap)

	if year:
	    return (jsondata, colors, catnum)
	else:
	    return (json_generator(cursor, 'data', records), colors, catnum)

app = Flask(__name__)

@app.route('/')
def test():
    description = 'nlgis2 API Service v.0.1<br>/api/maps (map polygons)<br>/api/data (data services)<br>'
    return description

@app.route('/demo')
def demo():
    sql = "select * from datasets.topics where 1=1";
    sql = sqlfilter(sql)
    return sql

@app.route('/topicslist')
def topicslist():
    (cursor, options) = connect('')
    data = list_topics(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/lonlat')
def lonlat():
    (cursor, options) = connect('')
    data = load_lonlat(cursor)
    return Response(data,  mimetype='application/json')


@app.route('/progress')
def open():
    root = ''
    resp = make_response(render_template('progress.html', download=root))
    return resp

# Panel data
@app.route('/panel')
def panel():
    (handle, yearmin, yearmax, thisyear, ctrlist, lastyear) = ('', '1500', '2020', 1950, '', 2010)
    config = configuration()
    modern = moderncodes(config['modernnames'], config['apiroot'])
    if request.args.get('handle'):
        handle = str(request.args.get('handle'))
	handle = handle.replace(" ", "")
	handle = handle.replace("'", "")
    if request.args.get('dataset'):
        dataset = request.args.get('dataset')
    if request.args.get('ctrlist'):
        customcountrycodes = ''
        ctrlist = request.args.get('ctrlist')
    if request.args.get('year'):
        thisyear = request.args.get('year')

    jsonapi = config['apiroot'] + "/api/datasets?handle=" + str(handle)
    dataframe = load_api_data(jsonapi, '')
    result = ''
    ctrlimit = 10

    allcodes = {}
    panel = []
    names = {}

    for dataitem in dataframe:
        handle = dataitem['handle']
	names[handle] = dataitem['title']
        (dataset, codes) = paneldatafilter(dataitem['data'], int(yearmin), int(yearmax), ctrlist, handle)
        if not dataset.empty:
            panel.append(dataset)

    if panel:
        totalpanel = pd.concat(panel)
        cleanedpanel = totalpanel.dropna(axis=1, how='any')
        cleanedpanel = totalpanel

        (header, data, countries, handles, vhandles) = panel2dict(cleanedpanel, names)  
	years = []
	for year in sorted(data):
            try:
        	years.append(int(year))
		lastyear = year
    	    except:
        	skip = 1

	# Return only years
	if request.args.get('showyears'):
	    yearsdata = {}
	    yearsdata['years'] = years
	    yearsdata['latestyear'] = lastyear
	    #yearsdata['data'] = data
	    yearsjson = json.dumps(yearsdata, ensure_ascii=False, sort_keys=True, indent=4)
	    return Response(yearsjson,  mimetype='application/json')

	# Show dataframe in CSV
        result = panel2csv(header, data, thisyear, countries, handles, vhandles, ctrlimit, modern)

    return Response(result,  mimetype='text/plain')

# Collabs
@app.route('/collabs')
def collabs():
    remove = ["date", "_id", "passwd"]
    (project, jsondata) = ('', '')
    data = {}
    if request.args.get('project'):
	project = request.args.get('project')
	data = readdata('projects', 'uri', project)
	for item in data:
    	    for r in remove:
		if item[r]:
                    del item[r]
	    jsondata = json.dumps(item, encoding="utf-8", sort_keys=True, indent=4)

    return Response(jsondata,  mimetype='application/json')

# Advanced statistiscs
@app.route('/advancedstats')
def advanced_statistics():
    (yearmin, yearmax, ctrlist) = (1500, 2020, '')
    config = configuration()
    handles = []

    if request.args.get('handle'):
        handledataset = request.args.get('handle')
	handledataset = handledataset.replace(" ", '')

    if request.args.get('dataset'):
        dataset = request.args.get('dataset')
        handles.append(dataset)

    if request.args.get('yearmin'):
        yearmin = request.args.get('yearmin')
    if request.args.get('yearmax'):
        yearmax = request.args.get('yearmax')
    if request.args.get('ctrlist'):
        ctrlist = request.args.get('ctrlist')

    modern = moderncodes(config['modernnames'], config['apiroot'])
    jsonapi = config['apiroot'] + '/api/datasets?handle=' + str(handledataset)

    (panel, cleanedpanel, names) = loadpanel(jsonapi, yearmin, yearmax, ctrlist)
    (header, data, countries, handles, vhandles) = advpanel2dict(cleanedpanel)

    ctrlimit = 200
    #result = panel2csv(header, data, thisyear, countries, handles, vhandles, ctrlimit, modern)
    #maindataframe = data2statistics(handles, cleanedpanel)
    #showhtml = statistics_tojson(maindataframe, modern)
    data = handle2statistics(handles, cleanedpanel)
    showhtml = statistics2table(data)
    return showhtml

# Dataverse API
@app.route('/download')
def download():
    pid = ''
    root = ''
    config = configuration()

    if request.args.get('pid'):
        pid = request.args.get('pid')

    zipfile = downloadzip(pid)
    root = config['apiroot'] + "/collabs/static/tmp/" + zipfile

    # HTML
    #resp = make_response(render_template('progress.html', download=root))
    #return "<a href=\"" + str(root) + "\">Download dataset(s) with all papers (zip archive)</a>"
    #return resp
    return redirect(root, code=301)

@app.route('/webmappercodes')
def webmapper():
    config = configuration()
    api = config['apiroot'] + "/collabs/static/data/historical.json"
    (regions, countries, ctr2reg, webmapper, geocoder) = histo(api)

    data = json.dumps(webmapper, encoding="utf-8", sort_keys=True, indent=4)
    return Response(data,  mimetype='application/json')

@app.route('/geocoder')
def geocoder():
    config = configuration()
    fromyear = 1500
    cfilter = ''
    if request.args.get('name'):
        cfilter = request.args.get('name')

    if fromyear:
        historical = 1
        if historical:
            api = config['apiroot'] + "/collabs/static/data/historical.json"
            (regions, countries, ctr2reg, webmapper, geocoder) = histo(api, cfilter)
    data = json.dumps(geocoder, encoding="utf-8", sort_keys=True, indent=4)
    return Response(data,  mimetype='application/json')

@app.route('/datasets')
def datasets():
    config = configuration()
    (jsondata, pid) = ('', '')
    handles = []
    combineddataset = []
    datainfo = []

    if request.args.get('handle'):
        pid = request.args.get('handle')
    if request.args.get('latest'):
	dataset = config['defaulthandle']
   	return dataset

    if pid:
        (handles, pidslist) = pidfrompanel(pid)

        hquery = formdatasetquery(handles,'')
        datainfo = readdatasets('datasets', json.loads(hquery))
	#if not datainfo:
	    #datainfo.append(pid)

	#return 'test'
        for dataset in datainfo:
	    data = {}
	    handle = dataset['handle']
            jsondata = str(dataset['data'])
	    jsondata = jsondata.replace(".0,", ",")
	    json_dict = ast.literal_eval(jsondata.strip())
	    data['handle'] = handle
	    try:
	        data['title'] = dataset['title']
	        data['units'] = dataset['units']
	    except:
		data['title'] = 'Title'
		data['units'] = 'Units'
	    data['data'] = json_dict
	    combineddataset.append(data)

    if combineddataset:
	
        finaldata = json.dumps(combineddataset, encoding="utf-8", sort_keys=True, indent=4)
        return Response(finaldata,  mimetype='application/json')
    else:
	print "No data"

@app.route('/dialog')
def dialog():
    pid = ''
    root = ''
    if request.args.get('pid'):
        pid = request.args.get('pid')
        zipfile = downloadzip(pid)
        root = "http://clearance.sandbox.socialhistoryservices.org/collabs/static/tmp/" + zipfile

    resp = make_response(render_template('dialog.html', download=root))
    return resp

@app.route('/dataverse')
def dataverse():
    config = configuration()
    root = config['dataverseroot']
    query = ''
    if request.args.get('q'):
        query = request.args.get('q')
    apiurl = root + "/api/search?q=" + str(query) + "&key=" + config['key'] + "&type=dataset"
    url = request.url

    data = ''
    if query:
        rawdata = load_dataverse(apiurl)
    else:
        rawdata = simplesearch(root, url, config['apiroot'])
	#return rawdata

    try:
        data = json.dumps(rawdata, encoding="utf-8", sort_keys=True, indent=4)
	return Response(data,  mimetype='application/json')
    except:
	data = 'no data'
	return 'No data'

@app.route('/oecd')
def oecd():
    (cursor, options) = connect('')
    data = load_oecd(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/oecdregions')
def oecdregions():
    (cursor, options) = connect('')
    data = load_oecdregions(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/indicators')
def indicators():
    data = load_indicators("indicators.csv")
    return Response(data,  mimetype='application/json')

@app.route('/search')
def search():
    q = request.args.get('q')
    data = searchdata(q)
    return Response(data,  mimetype='application/json')

@app.route('/topics')
def topics():
    (cursor, options) = connect('')
    data = load_topics(cursor, 0, 0)
    return Response(data,  mimetype='application/json')

def load_province_data(apiurl, province):
    jsondataurl = apiurl + province
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

@app.route('/clean')
def clean():
    cleanall = ''
    custom = ''
    exceptdb = ''
    (cursor, options) = connect(custom)

    cmd = ''
    if request.args.get('all'):
        cleanall = 'yes'
    if request.args.get('except'):
        exceptdb = request.args.get('except')

    cparser = ConfigParser.RawConfigParser()
    cparser.read(cpath)
    imagepathloc = cparser.get('config', 'imagepathloc')

    ext = ["png", "svg", "PDF", "gz", "csv", "tar", "jpg"]
    for extension in ext:
       thiscmd = "/bin/rm -rf " + imagepathloc + "/*." + extension + ";"
       cmd = cmd + thiscmd
    # clean custom
    customcmd = "/bin/rm -rf " + imagepathloc + "/custom/*";
    cmd = cmd + customcmd
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())

    # Clean custom " + datasettable + "base
    if exceptdb:
	sql = "delete from " + datasettable + " where 1=1"
	sql = sql + ' and indicator<>\'' + exceptdb + '\''
    else:
	sql = "truncate table " + datasettable + ""
    cursor.execute(sql)
    sql = "truncate table datasets.topics"
    cursor.execute(sql)

    return 'All files and custom databases cleaned. ' 

@app.route('/provincies')
def provincies():
    thisprovince = ''
    provinceurl = "http://www.gemeentegeschiedenis.nl/provincie/json/"
    paramprovince = request.args.get('province');
    if paramprovince:
	thisprovince = paramprovince

    provlist = ["Groningen", "Friesland", "Drenthe", "Overijssel", "Flevoland", "Gelderland", "Utrecht", "Noord-Holland", "Zuid-Holland", "Zeeland", "Noord-Brabant", "Limburg"]
    provincies = {}
    if thisprovince:
        provlist = []
        provlist.append(thisprovince)
    
    for province in provlist:
        data = load_province_data(provinceurl, province)
        provincelist = []
        for item in data:
            locations = {}
            #print item['amco'] + ' ' + item['provincie'] + ' ' + item['startjaar'] + ' ' + item['eindjaar'] + ' ' + item['naam']
            locations['amsterdamcode'] = item['amco']
            locations['name'] = item['naam']
            locations['start'] = item['startjaar']
            locations['end'] = item['eindjaar']
            locations['cbscode'] = item['cbscode']
            provincelist.append(locations)
        provincies[province] = provincelist

    jsondata = json.dumps(provincies, ensure_ascii=False, sort_keys=True, indent=4)
    return Response(jsondata,  mimetype='application/json')

@app.route('/dataapi')
def dataapi():
    handles = []
    logscale = ''
    config = configuration()
    customyear = ''
    fromyear = '1500'
    toyear = '2012'
    categoriesMax = 6
    countriesNum = 200
    geocoder = ''
    (getrange, colormap, pallette, customcountrycodes) = ('', '', '', '')

    if request.args.get('logscale'):
        logscale = request.args.get('logscale')
    if request.args.get('year'):
        customyear = request.args.get('year')
    if request.args.get('catmax'):
        categoriesMax = int(request.args.get('catmax'))
    if request.args.get('getrange'):
        getrange = request.args.get('getrange')
    if request.args.get('colors'):
        pallette = request.args.get('colors')
    if request.args.get('colormap'):
        colormap = request.args.get('colormap')
    if request.args.get('geocoder'):
        geocoder = request.args.get('geocoder')
    if request.args.get('handle'):
        handlestring = request.args.get('handle')
	ishandle = re.search(r'(hdl:\d+\/\w+)', handlestring)
	if ishandle:
    	    handle = ishandle.group(1)
	    handle = handle.replace("'", "")
	else:
	    handle = handlestring
        handles.append(handle)

    if request.args.get('ctrlist'):
        customcountrycodes = ''
        tmpcustomcountrycodes = request.args.get('ctrlist')
        c = tmpcustomcountrycodes.split(',')
        for ids in sorted(c):
           if ids:
               customcountrycodes = str(customcountrycodes) + str(ids) + ','
        customcountrycodes = customcountrycodes[:-1]

    hist = {}
    config = configuration()
    try:
	if len(customcountrycodes):
            countriesNum = len(customcountrycodes.split(','))
            if countriesNum < categoriesMax:
	        if countriesNum >= 1:
                    categoriesMax = countriesNum
    except:
	nothing = 1

    (header, panelcells, codes, x1, x2, x3, x4) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist, logscale)

    modern = moderncodes(config['modernnames'], config['apiroot'])
    #jsondata = data2json(modern, codes, panelcells)
    #data = json.dumps(jsondata, ensure_ascii=False, sort_keys=True, indent=4)
    (defaultcolor, colors) = getcolors(categoriesMax, pallette, colormap)
    (catlimit, ranges, dataset) = getscales(panelcells, colors, categoriesMax, geocoder)
 
    if getrange:
	(showrange, tmprange) = combinerange(ranges)
	webscale = webscales(showrange, colors, defaultcolor)
	data = json.dumps(webscale, ensure_ascii=False, sort_keys=True, indent=4)
	return Response(data,  mimetype='application/json')
    else:
        data = json.dumps(dataset, ensure_ascii=False, sort_keys=True, indent=4)
        return Response(data,  mimetype='application/json')

@app.route('/locations')
def locations():
    (cursor, options) = connect('')
    data = load_locations(cursor, 0, 0)
    return Response(data,  mimetype='application/json')

@app.route('/indicators')
def classes():
    (cursor, options) = connect('')
    data = load_classes(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/years')
def years():
    (cursor, options) = connect('')
    data = load_years(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/regions')
def regions():
    (cursor, options) = connect('')
    data = load_regions(cursor)
    return Response(data,  mimetype='application/json')

@app.route('/tabledata')
def tabledata():
    (data, aggrdata) = tableapi()
    return Response(data,  mimetype='text/plain')

@app.route('/scales')
def scales():
    (cursor, options) = connect('')
    year = 0
    datatype = '1.01'
    region = 0
    debug = 0
    datarange = 'random'
    output = ''

    # Read parameters grom GET
    paramrange = request.args.get('datarange');
    paramyear = request.args.get('year')
    paramoutput = request.args.get('output');
    paramscales = request.args.get('scales');
    paramcat = request.args.get('categories');
    catnum = 8
    if paramrange:
        datarange = paramrange
    if paramyear:
        year = paramyear
    if paramoutput:
        output = paramoutput
    if options['defaultcategories']:
        catnumint = int(options['defaultcategories'])
    if paramcat:
        catnumint = paramcat
        try:
            catnum = int(catnumint)
        except:
            catnum = catnumint

    realcatnum = analyze_data(cursor, catnum)
    if realcatnum:
        if realcatnum < catnum:
            catnumX = realcatnum

    paramscales = 'scale'
    try:
        (data, colors, catnum) = load_data(cursor, year, datatype, region, datarange, output, debug, paramscales, catnum, options, '')
    except:
	data = []
	colors = []
    # DEBUGSCALE
    #return json.dumps(data)
    (rangearr, rangestr) = combinerange(data)
    colormap = []
    cID = 0
    # Remove extra colors if less than 8 categories
    if catnum < 8:
	colors.pop()
    for color in reversed(colors):
	if cID >= 0:
	    colormap.append(color)
	    output = output + ' ' + color
	cID = cID + 1
    output = ''
    id = 0 
    #return str(catnum) + ' ' + json.dumps(rangearr) + json.dumps(colormap)
    #return json.dumps(data) + ' ' + json.dumps(colors) + ' ' + str(catnum)
    scales = {}
    for thisrange in rangearr:
	if thisrange != "0.0 - 0.0":
	    output = output + ' ' + thisrange + '=' + str(id) + '<br>'
	    color = colormap[id]
	    savecolor = {}
	    savecolor['color'] = color
	    thisid = catnum - id
	    savecolor['range'] = thisrange
	    #savecolor['max'] = data[thisid]
	    savecolor['sector'] = id
	    scales[id] = savecolor
	id = id + 1

    # Add no data in scale
    if id:
	savecolor = {}
	savecolor['color'] = '#ffffff'
	savecolor['range'] = 'no data'
	scales[id] = savecolor

    jsondata = json.dumps(scales, ensure_ascii=False, sort_keys=True, indent=4)
    return Response(jsondata,  mimetype='application/json')

@app.route('/data')
def data():
    (cursor, options) = connect('')
    year = 0
    datatype = '1.01'
    region = 0
    debug = 0
    datarange = 'random'
    csvexport = ''
    output = ''
    code = ''
    paramrange = request.args.get('datarange');
    paramyear = request.args.get('year')
    paramoutput = request.args.get('output');
    paramscales = request.args.get('scales'); 
    paramcat = request.args.get('categories');
    catnum = 8 
    if paramrange:
        datarange = paramrange
    if paramyear:
	year = paramyear
    if paramoutput:
	output = paramoutput
    if options['defaultcategories']:
        catnumint = int(options['defaultcategories'])
        #catnum = catnumint
    if request.args.get('csv'):
        csvexport = 'yes'
    if request.args.get('code'):
        code = request.args.get('code')
    if paramcat:
        catnumint = paramcat
        try:
            catnum = int(catnumint)
        except:
            catnum = catnumint

    realcatnum = analyze_data(cursor, catnum)
    if realcatnum:
        if realcatnum < catnum:
            catnumX = realcatnum

    (data, colors, catnum) = load_data(cursor, year, datatype, region, datarange, output, debug, paramscales, catnum, options, csvexport)
    # D2
    #return data
    #DEBUG1
    dataset = data
    if csvexport:
        cparser = ConfigParser.RawConfigParser()
        cparser.read(cpath)
        imagepathloc = cparser.get('config', 'imagepathloc')
        # CSV
        localfile = 'dataset_' + code + '.csv'
        fullpath = imagepathloc + '/' + localfile

        f = csv.writer(open(fullpath, "wb+"))
        f.writerow(colors)
        #m = dataset['data']
        for dataset in data:
            f.writerow(dataset)
        return send_from_directory(imagepathloc, localfile, as_attachment=True)

    if paramscales:
	#dataset = paramscales
	(rangearr, rangestr) = combinerange(dataset)
	output = ''
	id = 0
	for i in dataset:
	    if output:
	        output = output + ',' + str(i) #+ colors[id]
	    else:
		output = str(i)
	    id = id + 1

	json_response = rangestr
	return Response(json_response) #, mimetype='application/json')
    else:
	return Response(dataset, mimetype='application/json')

    #json_response = json.loads(data)
    #return Response(data,  mimetype='application/json;charset=utf-8')
    return Response(dataset, mimetype='application/json')

@app.route('/maps')
def maps():
    cparser = ConfigParser.RawConfigParser()
    cparser.read(cpath)
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')

    # Default year 
    year = cparser.get('config', 'year')
    cmdgeo = ''
    provcmd = ''
    wcmdgeo = ''
    thisformat = 'topojson'
    # get year from API call
    paramyear = request.args.get('year');
    world = request.args.get('world');
    # format for polygons: geojson, topojson, kml 
    paramformat = request.args.get('format');
    paramprovince = request.args.get('province');
    if paramyear:
	year = paramyear
    if paramformat == 'geojson':
	cmdgeo = path + "/maps/bin/geojson.py " + str(year) + " " + geojson
	thisformat = paramformat
    if paramprovince:
	provcmd = path + '/maps/bin/topoprovince.py ' + str(year) + " " + paramprovince + " " + thisformat	
    if world:
	wcmdgeo = path + "/maps/bin/topoworld.py " + str(year) 

    pythonpath = '/usr/bin/python '
    cmd = pythonpath + path + "/maps/bin/topojson.py " + str(year)
    if cmdgeo:
	cmd = pythonpath + cmdgeo
    if provcmd:
	cmd = pythonpath + provcmd
    if wcmdgeo:
	cmd = pythonpath + wcmdgeo

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = json.dumps(p.stdout.read())
    #"objects":{"1812
    #new_string = re.sub(r'"{\"1812"', r'{\"NLD', response)
    json_response = json.loads(response)

    return Response(json_response,  mimetype='application/json;charset=utf-8')

if __name__ == '__main__':
    app.run()
