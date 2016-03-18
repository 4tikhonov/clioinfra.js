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

from flask import Flask, render_template, redirect
from flask import g, session
from flask import Response, make_response, request, send_from_directory
from twisted.web import http
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required
import json
import urllib2
import glob
import csv
import sys
import string
import pprint
import getopt
import ConfigParser
import HTMLParser
from subprocess import Popen, PIPE, STDOUT
import simplejson
import re
import os
import pandas as pd
from werkzeug import secure_filename
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from pandas.io.json import json_normalize
from math import log10, floor

# Clio Infra modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from chartprint import chartonprint
from advancedstatistics import loadpanel, statistics2table, handle2statistics, data2statistics, read_measure, statistics_tojson, advpanel2dict
from boundaries import getboundaries
from statistics import createdata
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, get_citation, pidfrompanel, graphlinks
from locations import load_locations
from topics import load_alltopics
from locations import load_locations
from historical import load_historical
from tabulardata import loadcodes, moderncodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel
from storage import data2store, readdata, removedata, readdatasets, formdatasetquery
from datasets import *
from searchapi import search_by_keyword, search_by_handles, get_datasets_from_html
from dataverse import Connection
from cliocore.configutils import Configuration, Utils
from cliocore.searchapi import ExtrasearchAPI

def readglobalvars():
    cparser = ConfigParser.RawConfigParser()
    cparser.read(cpath)
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')
    website = cparser.get('config', 'website')
    server =  cparser.get('config', 'serverip')
    api_topics_url = server + '/api/topics?'

    # Default year from configuration
    configyear = cparser.get('config', 'year')
    # or year from cookies
    cookieyear = request.cookies.get('year')
    configcode = cparser.get('config', 'code')
    cookiecode = request.cookies.get('code')
    cookiedatarange = request.cookies.get('datarange')
    viewerpath = cparser.get('config', 'viewerpath')
    imagepathloc = cparser.get('config', 'imagepathloc')
    imagepathweb = cparser.get('config', 'imagepathweb')
    viewerpath = cparser.get('config', 'viewerpath')
    path = cparser.get('config', 'path')
    geojson = cparser.get('config', 'geojson')
    configdatarange = cparser.get('config', 'range')

    cmdgeo = ''
    custom = ''

    # get year from API call
    paramyear = request.args.get('year')
    # format for polygons: geojson, topojson, kml
    paramcode = request.args.get('code')
    paramdatarange = request.args.get('datarange')
    year = configyear
    code = configcode
    datarange = configdatarange
    if request.args.get('custom'):
       custom = request.args.get('custom')
    if cookieyear:
       year = cookieyear
    if cookiecode:
       code = cookiecode
    if cookiedatarange:
       datarange = cookiedatarange
    if paramyear:
       year = paramyear
    if paramcode:
       code = paramcode
    if paramdatarange:
       datarange = paramdatarange

    try:
	if int(year) > 2997:
	    year = '1997'
    except:
	donothing = 1

    return (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom)

def load_remote_data(apiurl, code, year):
    amscode = str(code)
    jsondataurl = apiurl + '&year=' + year 
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def first_digit(pop_data):
    return int(str(pop_data)[0])

def load_api_data1(apiurl, code, year, custom, scales, catnum):
    pyear = ''
    amscode = ''
    if code:
	try:
            amscode = str(code)
	except:
	    amscode = code
    if year:
	try:
	    pyear = str(year)
	except:
	    pyear = year
    jsondataurl = apiurl 
    if code:
        jsondataurl = jsondataurl + "&code=" + code
    if year:
        jsondataurl = jsondataurl + '&year=' + pyear
    if custom:
	jsondataurl = jsondataurl + '&custom=' + custom
    if scales:
        jsondataurl = jsondataurl + '&scales=' + scales
    if catnum:
	jsondataurl = jsondataurl + '&categories=' + str(catnum)
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    if scales:
        dataframe = urllib2.urlopen(req).read()
    else:
        dataframe = simplejson.load(f)
    return dataframe

app = Flask(__name__)
clioinfra = Configuration()
app.secret_key = clioinfra.config['secretkey']

@app.route('/graphslider')
def graphslider():
    params = "handle=Panel['hdl%3A10622/4X6NCK'%2C 'hdl%3A10622/I0YK5M']&ctrlist=840%2C804%2C40%2C56%2C276%2C528%2C36&yearmin=1500&yearmax=2013"
    years = [1950, 1970, 1990, 2000, 2010]
    title = 'Graph slider'
    lastyear = 2010
    steps = lastyear
    return make_response(render_template('graphslider.html', params=params, years=years, title=title, lastyear=lastyear, steps=steps))

@app.route('/mapslider')
def mapslider():
    (title, steps, customcountrycodes, fromyear, toyear, customyear, catmax, histo) = ('', 0, '', '1500', '2012', '', 6, '') 
    config = configuration()
    datafilter = {}
    datafilter['ctrlist'] = ''
    datafilter['startyear'] = fromyear
    datafilter['endyear'] = toyear
    if config['error']:
	return config['error']
    handleface = ''
    urlmatch = re.search(r'(.+)\&face', request.url)
    try:
        if urlmatch.group(0):
            thismapurl = urlmatch.group(1)
    except:
	thismapurl = request.url
    thismapurl = thismapurl.replace('http://', 'https://')

    geocoder = ''
    pids = []
    handledataset = ''
    logscale = 0
    handles = []
    datahub = {}
    dataset = ''
    warning = ''
    hist = {}
    if request.args.get('ctrlist'):
        customcountrycodes = ''
        tmpcustomcountrycodes = request.args.get('ctrlist')
        c = tmpcustomcountrycodes.split(',')
        for ids in sorted(c):
           if ids:
               customcountrycodes = str(customcountrycodes) + str(ids) + ','
        customcountrycodes = customcountrycodes[:-1]
	datafilter['ctrlist'] = customcountrycodes

    if request.args.get('dataset'): 
        dataset = request.args.get('dataset')
	handles.append(dataset)

    if request.args.get('handle'):
        handledataset = request.args.get('handle')
	try:
  	    (pids, pidslist) = pidfrompanel(handledataset)
	except:
	    nopanel = 'yes'

        handlestring = request.args.get('handle')
        ishandle = re.search(r'(hdl:\d+\/\w+)', handlestring)
        if ishandle:
            handle = ishandle.group(1)
            handle = handle.replace("'", "")
        else:
            handle = handlestring

	(dataset, revid, cliopid, clearpid) = findpid(handle)
        #handles.append(dataset)
	handles.append(handle)
	handleface = handle

    if request.args.get('logscale'):
	logscale = 1
    if request.args.get('catmax'):
	catmax = request.args.get('catmax')
    if request.args.get('yearmin'):
        fromyear = request.args.get('yearmin')
	datafilter['startyear'] = fromyear
    if request.args.get('yearmax'):
        toyear = request.args.get('yearmax')
	datafilter['endyear'] = toyear
    if request.args.get('geocoder'):
        geocoder = request.args.get('geocoder')
    if request.args.get('hist'):
        geocoder = request.args.get('hist') 
	histo = 'on'
    if request.args.get('face'):
        handleface = request.args.get('face')
    if handleface:
	handles = []
	handle = handleface
	handles.append(handleface)
	try:
	    pids.remove(handleface)
	except:
	    nothing = 1

    historical = 0

    hubyears = []
    if config:
	switch = 'modern'
	if histo:
	    switch = 'historical'
        (geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, '')
        (origdata, maindata, metadata) = request_datasets(config, switch, modern, historical, handles, geolist)
	(hubyears, notyears) = selectint(origdata.columns)
	title = metadata[handles[0]]['title'] 

    for handle in handles:
        (datasubset, ctrlist) = datasetfilter(maindata[handle], datafilter)
        datasubset['handle'] = handle
        if not datasubset.empty:
            datasubset = datasubset.dropna(how='all')
	    (allyears, notyears) = selectint(datasubset.columns)
	    for year in datasubset:
		if datasubset[year].count() == 0:
		    datasubset = datasubset.drop(year, axis=1)
	    (hubyears, notyears) = selectint(datasubset.columns)

    validyears = []
    lastyear = ''
    for year in sorted(hubyears):
	validyears.append(year)
	lastyear = year
	steps = steps + 1

    handledict = {}
    if pids:
	hquery = formdatasetquery(pids,'')
	d = readdatasets('datasets', json.loads(hquery))
	for x in d:
	    thishandle = x['handle']
	    handledict[thishandle] = x['title']

    #validyears.reverse()
    return make_response(render_template('mapslider.html', handle=handle, years=validyears, warning=warning, steps=steps, title=title, geocoder=histo, dataset=dataset, customcountrycodes=customcountrycodes, catmax=catmax, lastyear=lastyear, indicators=pids, thismapurl=thismapurl, handledict=handledict))

ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/download')
def download(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    config = configuration()
    year = str(year)
    format = 'png'
    svgfileout = ''
    province = ''
    pdffile = ''
    shapefile = ''
    size = str(1524);
    paramformat = request.args.get('format')
    if paramformat:
        format = paramformat
    if request.args.get('province'):
        province = request.args.get('province')

    filesvg = imagepathloc + '/' + year + '_' + code + '_' + "map.svg"
    page = '/site?nolegend=yes&year='
    if request.args.get('worldmap'):
	page = '/worldmap?nolegend=yes&year='
	#size = str(1024);

    if format == 'shapefile':
	year = year
    else:
        cmd = path + "/node_modules/phantomjs/lib/phantom/bin/phantomjs " + path + "/collabs/static/renderHTML.js '" + website + page + year + "&code=" + code + "&province=" + province + "&custom=" + custom + "'"
        #cmd = '/bin/echo test'

        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        html = p.communicate()[0]
        result = re.findall(r'<svg.+?</svg>', html, re.DOTALL)
        if year:
            svgfile = open(filesvg, "w")
            svgfile.write(result[0])
            svgfile.close()

    if format == 'SVG':
        svgfileout = '/get?svg=' + year + '_' + code + '_' + "map.svg"
        return "<a href=\"" + svgfileout + "\">Download SVG file</a>"
        fileonweb = ''

    if format == 'png':
        outfile = year + '_' + code + '_' + 'map.png'
        outdirfile = imagepathloc + '/' + outfile
        cmd = "/usr/bin/inkscape " + filesvg + " -e " + outdirfile + " -h " + size + " -D -b '#ffffff'"
	fileonweb = '/get?image=' + outfile

    if format == 'shapefile':
	thisfilter = year + '_' + code + '_'
	infile = year + '_' + code + '_' + 'tmp.json'
        outfile = year + '_' + code + '_' + 'tmp.shp'
	indirfile = imagepathloc + '/' + infile
        outdirfile = imagepathloc + '/' + outfile
	webapicmd = website + "/api/maps?format=geojson&year=" + year 
	if province:
	    webapicmd = webapicmd + "&province=" + province
	
	cmd = "/usr/bin/wget \"" + webapicmd +"\" -O " + indirfile
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
	cmd = "/usr/bin/ogr2ogr -f \"ESRI Shapefile\" " + outdirfile + " " + indirfile
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
	if outdirfile:
	   cmd = "cd " + imagepathloc + ";tar -cf " + thisfilter + ".tar *" + thisfilter + "*;gzip " + thisfilter + ".tar;rm -rf *" + thisfilter + "*tmp*" 
	   shapefile = '/get?nlgis=' + thisfilter + ".tar.gz"

    if format == 'pdf':
        outfile = year + '_' + code + '_' + 'map.PDF'
        outdirfile = imagepathloc + '/' + outfile	
	cmd = "/usr/bin/inkscape " + filesvg + " --export-pdf=" + outdirfile + " -D -b '#ffffff'"
	fileonweb = ''
	pdffile = '/get?pdf=' + outfile

    if cmd:
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
        image = outfile

    if shapefile:
        return "<a href=\"" + shapefile + "\">Download ShapeFile</a>"
    resp = make_response(render_template('download.html', image=fileonweb, svgfile=svgfileout, pdffile=pdffile))
    return resp

@app.route('/treemap')
def treemap(settings=''):
    (years, ctrlist) = ([], '')
    showpanel = 'yes'
    config = configuration()
    if config['error']:
        return config['error'] 

    (historical, handle, handles, thisyear) = ('', '', [], '')
    if request.args.get('face'):
        facehandle = request.args.get('face')
        if facehandle not in handles:
            handles.append(facehandle)
	    handle = facehandle

    if request.args.get('handle'):
        handledataset = request.args.get('handle')
        try:
            (pids, pidslist) = pidfrompanel(handledataset)
	    handle = pids[0]
            handles.append(handle)
        except:
            handles.append(handledataset)
	    handle = handledataset
            nopanel = 'yes'
    if request.args.get('historical'):
        historical = request.args.get('historical')
    if request.args.get('year'):
        thisyear = request.args.get('year')
    if request.args.get('hist'):
        historical = request.args.get('hist')
    if request.args.get('ctrlist'):
	ctrlist = request.args.get('ctrlist')
        if ctrlist == config['ctrlist']:
	    ctrlist = ''

    mainlink = '&handle=' + str(handle)
    try:
        (title, units, years) = dpemetadata(config, handle)
    except:
        (title, units, years) = ('Panel Data', '', [])

    if historical:
	mainlink = str(mainlink) + '&historical=on'
    if thisyear:
	mainlink = str(mainlink) + '&year=' + str(thisyear)
    if ctrlist:
	mainlink = str(mainlink) + '&ctrlist=' + str(ctrlist)

    links = graphlinks(mainlink)
    apitreemap = config['apiroot'] + "/api/treemap?action=showyears&handle=" + str(handles[0]) + "&ctrlist=" + str(ctrlist)
    years = load_api_data(apitreemap, 1)
    total = len(years)
    lastyear = years[-1]

    resp = make_response(render_template('treemap.html', handle=handle, chartlib=links['chartlib'], barlib=links['barlib'], panellib=links['panellib'], treemaplib=links['treemaplib'], q=handle, showpanel=showpanel, historical=historical, title=title, thisyear=thisyear, years=years, total=total, lastyear=lastyear, ctrlist=ctrlist))
    return resp

# Visualize
@app.route('/visualize')
def visualize():
    config = configuration()
    resp = 'visualize'
    view = 'panel'
    if request.args.get('view'):
	view = request.args.get('view')

    if config['error']:
        return config['error']

    if view == 'panel':
        resp = panel()
    elif view == 'time-series':
	resp = chartlib()
    elif view == 'treemap':
	resp = treemap()
    return resp

@app.route('/panel')
def panel(settings=''):
    showpanel = ''
    handle = ''
    handler = ''
    config = configuration()
    if config['error']:
        return config['error']

    f = request.args
    for q in f:
	value = f[q]
	if value:
	    handle = str(handle) + '&' + str(q) + '=' + str(f[q])
    # Default countris
    try:
        if not f['yearmin']:
	    handle = str(handle) + '&yearmin=1500&yearmax=2013'
    except:
	handle = str(handle) + '&yearmin=1500&yearmax=2013'
    try:
        if not f['ctrlist']:
	    handle = str(handle) + '&ctrlist=' + config['ctrlist'] 
    except:
	handle = str(handle) + '&ctrlist=' + config['ctrlist']
    try:
	if f['print']:
	    showpanel = ''
    except:
	showpanel = 'yes'

    try:
        (title, units, years) = dpemetadata(config, handle)
    except:
	(title, units, years) = ('Panel Data', '', [])
    links = graphlinks(handle)

    resp = make_response(render_template('panel.html', handle=handle, chartlib=links['chartlib'], barlib=links['barlib'], panellib=links['panellib'], treemaplib=links['treemaplib'], q=handle, showpanel=showpanel, title=title))
    return resp

@app.route('/chartlib')
def chartlib():
    (thismapurl, apilink, ctrlist, title, units, switch, hist) = ('', '', '', 'Title', 'Units', 'modern', '')
    handleface = []
    config = configuration()
    ctrlist = config['ctrlist']
    if config['error']:
        return config['error']

    urlmatch = re.search(r'(.+)\&face', request.url)
    try:
        if urlmatch.group(0):
            thismapurl = urlmatch.group(1)
    except:
        thismapurl = request.url
    if 'sandbox' not in thismapurl:
        thismapurl = thismapurl.replace('http://', 'https://')

    handles = []
    showpanel = 'yes'
    try:
        if request.args.get('print'):
            showpanel = ''
    except:
        showpanel = 'yes'
    f = request.args
    handle = ''
    for q in f:
        value = f[q]
        if value:
            handle = str(handle) + '&' + str(q) + '=' + str(f[q])

    if request.args.get('ctrlist'):
        ctrlist = request.args.get('ctrlist')
    if request.args.get('hist'):
	switch = 'historical'
	hist = request.args.get('hist')
    if request.args.get('handle'):
        handledataset = request.args.get('handle')
        try:
            (pids, pidslist) = pidfrompanel(handledataset)
	    handles.append(pids[0])
        except:
	    handles.append(handledataset)
            nopanel = 'yes'
	if pids[0]:
	    apilink = "/api/tabledata?handle=" + str(pids[0])
	    if ctrlist:
	        apilink = apilink + '&ctrlist=' + ctrlist
	    if request.args.get('hist'):
		apilink = apilink + '&hist=' + hist

    if request.args.get('face'):
        handles = []
        handleface = request.args.get('face')
        handles.append(handleface)
        if handleface:
	    apilink = "/api/tabledata?handle=" + str(handleface)
            if ctrlist:
                apilink = apilink + '&ctrlist=' + ctrlist
            if request.args.get('hist'):
                apilink = apilink + '&hist=' + hist
	    
        try:
            pids.remove(handleface)
        except:
            nothing = 1

    if set(pids) == set(handles):
	pids[:] = []
    links = graphlinks('&face=' + str(handles[0]) + '&hist=' + hist)
    (geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, '')
    # vty hist
    (origdata, maindata, metadata) = request_datasets(config, switch, modern, historical, handles, geolist)
    try:
	title = metadata[handles[0]]['title']
	units = metadata[handles[0]]['units']
    except:
	skip = 0

    handledict = {}
    if handles:
        handle = handles[0]

    if pids:
	try:
	    if handles[1]:
	        pids.remove(handles[0])
	except:
	    skip = 1
        hquery = formdatasetquery(pids,'')
        d = readdatasets('datasets', json.loads(hquery))
        for x in d:
            thishandle = x['handle']
	    if thishandle != handle:
                handledict[thishandle] = x['title']

    resp = make_response(render_template('chartlib.html', thismapurl=thismapurl, indicators=handledict, apilink=apilink, title=title, units=units, showpanel=showpanel, handle=handle, chartlib=links['chartlib'], barlib=links['barlib'], panellib=links['panellib'], treemaplib=links['treemaplib']))
    return resp

@app.route('/graphlib')
def graphlib(settings=''):
    showpanel = 'yes'
    try:
        if request.args.get('print'):
            showpanel = ''
    except:
        showpanel = 'yes'
    f = request.args
    handle = ''
    for q in f:
        value = f[q]
        if value:
            handle = str(handle) + '&' + str(q) + '=' + str(f[q])

    links = graphlinks(handle)

    resp = make_response(render_template('graphlib.html', handle=handle, chartlib=links['chartlib'], barlib=links['barlib'], panellib=links['panellib'], treemaplib=links['treemaplib'], q=handle, showpanel=showpanel))
    return resp

@app.route('/datasetspace')
def datasetspace(settings=''):
    (where, query, datasets, metadata, s, permissions) = ({}, '', [], [], {}, 'yes')
    where = {'collab': '', 'iish': '', 'harvard': ''}
    pagetitle = "Public datasets"
    config = configuration()
    if config['error']:
        return config['error']

    root = config['apiroot']
    dataversename = 'global'
    if request.args.get('dv'):
	dataversename = request.args.get('dv')
    if request.args.get('q'):
        query = request.args.get('q')
    if request.args.get('permissions'):
        permissions = request.args.get('permissions')
    if request.args.get('where'):
	where[request.args.get('where')] = 'checked="checked"' 

    settings = Configuration()
    sconnection = ExtrasearchAPI(settings.config['dataverseroot'], dataversename)
    if where['harvard']:
        # Extract host for Dataverse connection
        findhost = re.search('(http\:\/\/|https\:\/\/)(.+)', settings.config['harvarddataverse'])
        if findhost:
            settings.config['dataversehostname'] = findhost.group(2)
        connection = Connection(settings.config['dataversehostname'], settings.config['harvardkey'])
    else:
       try:
           connection = Connection(config['hostname'], settings.config['key'])
       except:
           return 'Error: no connection to Dataverse. Please try later...'

    handlestr = ''
    if query:
	s['q'] = query
	metadata = search_by_keyword(connection, s)
    else:
	try:
	    dataverse = connection.get_dataverse(dataversename)
	    item = dataverse.get_contents()
	    active = 'yes'	
	except:
	    active = None
	if active:
	    try:
                for item in dataverse.get_contents():
                    handlestr+= item['identifier'] + ' '
		    active = 'yes'
	    except:
	 	active = None

	if not active:
	    handlestr = sconnection.read_all_datasets()

        if handlestr:
	    s['q'] = handlestr	
	    s['per_page'] = 100
	    metadata = search_by_keyword(connection, s)

    #return str(metadata['items'])
    for dataset in metadata['items']:
	active = ''
	# Private datasets
	if permissions == 'closed':
	    pagetitle = "Restricted datasets"
	    try:
	        if (sconnection.has_restricted_data(dataset['global_id'])):
		    active = 'yes'
	    except:
		active = ''
	# Public data
	else:
	    try:
                if not (sconnection.has_restricted_data(dataset['global_id'])):
                    active = 'yes'
	    except:
		active = ''
	
	if active:
	    try:
	        for author in dataset['authors']:
	            dataset['author'] = str(author) + ', '
	            dataset['author'] = dataset['author'][:-2]
	    except:
	        dataset['author'] = str(dataset['description'])
	
            datasets.append(dataset)
	if where['harvard']:
	    datasets.append(dataset)

    (username, projectname) = ('','')    
    fields = {}
    resp = make_response(render_template('search.html', projectname=projectname, username=username, datasets=datasets, searchq=query, pagetitle=pagetitle, where=where, fields=fields))
    return resp

@app.route('/')
def start(settings=''):
    activepage = 'Home'
    config = configuration()
    if config['error']:
        return config['error']

    path = config['path']
    pages = getindex(activepage)
    perlbin = "/usr/bin/perl "
    project = "frontpage"
    base = ''
    varproject = request.args.get('project')
    varbase = request.args.get('base')
    if varproject:
	project = varproject
    if varbase:
	base = varbase
    cmd = perlbin + path + "/../../bin/collab2api.pl " + project + " '' " + " " + base
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    maincontent = p.communicate()[0]

    resp = make_response(render_template('clioinfra.html', maincontent=maincontent))
    return resp

@app.route('/benford')
def benford(cmddataset='', cmdyear='', settings=''):
    varbase = request.args.get('base')
    dataset = request.args.get('dataset')
    if cmddataset:
        dataset = cmddataset
    if cmdyear:
        year = cmdyear
    m = re.search(r'(\S+)\/(\S+)\:(\d+)\:(\d+)', dataset)
    handle = m.group(2) + m.group(3) + '_' + m.group(4)
    if not handle:
        return 'no dataset'

    year = request.args.get('year')
    action = request.args.get('action')
    apiurl = "http://localhost/api/data?db=strikes_test&handle=" + handle + "&categories=8&datarange=calculate"
    if year:
	varyear = year
    else:
        varyear = '1890'

    # Dataframe
    yeardf, countrydf, unitdf, valuedf = [],[],[],[]
    data = load_remote_data(apiurl, handle, varyear)
    for country in data:
        values = data[country]
        yeardf.append(data[country]['year'])
        valuedf.append(data[country]['value'])
        unitdf.append(data[country]['units'])
        countrydf.append(country)
    
    df = pd.DataFrame([yeardf,countrydf,unitdf,valuedf]).T
    df.columns = ['year', 'country', 'units', 'value']
    #newframe = df[['year', 'country', 'units', 'value']]
 
    # count how many constants have each leading digit
    count = [0]*10
    benford = {}
    #[0]*10
    d = valuedf
    for value in d:
        x = abs(value)
        dig = first_digit(x)
        if dig > 0:
            count[ dig ] += 1
        total = sum(count)
 
    try:
        for i in range(10):
            if i:
                benford[i] = count[i]
    except:
	return 'no data'

    result = 'digit\tfrequency\n'
    for dig in benford:
        value = benford[dig]
	if result:
	    result = result + str(dig) + '\t' + str(value) + '\n'
	else:
	    result = str(dig) + '\t' + str(value) + '\n'

    return Response(result, mimetype='text/csv')

def is_location(param):
    flag = re.match(r"c\[\d+\]", param)
    try:
        true = flag.group(0)
    except:
        true = 0

    return true

@app.route('/dashboard')
def dashboard(settings=''):
    activepage = 'Dashboard'
    config = configuration()
    if config['error']:
        return config['error']

    apiroot = config['apiroot']
    dataverseroot = config['dataverseroot']
    key = config['key']
    tabnum = '' 
    ctrnum = 0
    if not tabnum:
	tabnum = 3 # tabs with maps is default
    logscale = ''

    if config['perl']:
	perlbin = config['perl'] + ' '
    else:
        perlbin = "/usr/bin/perl "
    path = config['path']

    # Default parameters
    (datatitle, validate, topic, citation, cliopid, stats, fileid, clearpid) = ('', '', '', '', '', '', '', '')
    (handle, fromyear, toyear) = ('', 1500, 2012)
    (selectedcountries, selectedindicators) = ('', '')

    # Variables from dashboard
    varproject = request.args.get('project')
    varbase = request.args.get('base')
    dataset = request.args.get('dataset')
    # Log scales switch
    if request.args.get('logscale'):
        logscale = 1

    if request.args.get('pid'):
	dataset = request.args.get('pid')
    if dataset:
	(handle, revid, cliopid, clearpid) = findpid(dataset)

    action = request.args.get('action')
    year = request.args.get('year')
    hist = request.args.get('hist')
    if request.args.get('yearmin'):
        fromyear = request.args.get('yearmin')
    if request.args.get('yearmax'):
        toyear = request.args.get('yearmax')
    if request.args.get('y[min]'):
        fromyear = request.args.get('y[min]')
    if request.args.get('y[max]'):
        toyear = request.args.get('y[max]')
    # Select countries
    customcountrycodes = ''
    f = request.args
    for key in f.keys():
        if key == 'loc':
            for value in sorted(f.getlist(key)):
                customcountrycodes = str(customcountrycodes) + str(value) + ','
		ctrnum = ctrnum + 1
    if customcountrycodes:
        customcountrycodes = customcountrycodes[:-1]

    # Requests from Drupal
    fromdrupal = 0
    for key in f.keys():
        if is_location(key):
            for value in sorted(f.getlist(key)):
                customcountrycodes = str(customcountrycodes) + str(value) + ','
		fromdrupal = 1

    if fromdrupal:
        if customcountrycodes:
            customcountrycodes = customcountrycodes[:-1]

    template = "dashboard.html"

    # Load topics and locations
     
    api1 = apiroot + "/collabs/static/data/dataframe100_0.json"
    branch = config['branch']
    indicatorlist = load_alltopics(api1, branch)
    api2 = apiroot + "/collabs/static/data/dataframe94_0.json"
    locations = load_locations(api2)
    api3 = apiroot + "/collabs/static/data/historical.json"
    historical = load_historical(api3)
    if hist:
	locations = historical

    try:
        (dataversemeta, pid, fileid, cliopid) = load_metadata(dataset)
        for item in dataversemeta:
            citation = 'Suggested citation: ' + str(item['citation'])
            datatitle = str(item['name'])
            topic = item['topic']
    except:
        title = dataset

    if action == 'chart':
	template = 'chart.html'
    if action == 'map':
	template = 'worldmap.html'
    if action == 'validate':
	validate = 'yes'
	template = 'validate.html'
	template = 'simplechart.html'
    if action == 'geocoder':
	template = 'geocoder.html'
    if action == 'visualize':
	template = 'navigation.html'
	# DEB
 	jsonapi = apiroot + "/collabs/static/data/" + str(pid) + ".json"
	data = createdata(jsonapi)
	d = data.describe()
	show = d.transpose()
	stats = show.to_html()

    benforddata = ''
    datasetfile = ''
 
    try:
        benforddata = benford(dataset, year, '') 
    except:
	donothing = 1

    valtitle = ''
    if validate:
	# VALIDATION
	return 'Dataset not updated'
	cmd = path + "/../../bin/import.py -d '" + dataverseroot + "' -H '" + dataset + "'"
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        maincontent = p.communicate()[0]
	valtitle = maincontent
	return 'Dataset updated'

    if benforddata:
	title = benforddata
	datasetfile = benforddata
    else:
	# Clio dataset
	try:
            cmd = perlbin + path + "/../../bin/api2data.pl " + dataset
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            maincontent = p.communicate()[0]
            title = "World Data Strikes, 1927-2009"
            datasetfile = maincontent
	except:
	    donothing = 1

    datasetfile = valtitle
    if datatitle:
	title = datatitle
    if customcountrycodes:
	selectedcountries = customcountrycodes
    if dataset:
	selectedindicators = "\"" + dataset + "\""
    cliopids = cliopid

    # Choose tab
    if ctrnum <= 10:
	if ctrnum > 0:
	    tabnum = 0

    resp = make_response(render_template(template, active=activepage, pages=pages, title=title, datasetfile=datasetfile, dataset=dataset, stats=stats, topic=topic, citation=citation, cliopid=cliopid, indicatorlist=indicatorlist, locations=locations, fromyear=fromyear, toyear=toyear, customcountrycodes=customcountrycodes, handle=handle, selectedcountries=selectedcountries, selectedindicators=selectedindicators, cliopids=cliopids, logscale=logscale, tabnum=tabnum))
    return resp

@app.route('/statistics')
def statistics(settings=''):
    datafilter = {}
    (yearmin, yearmax, ctrlist, histo) = ('1500', '2020', '', '')
    datafilter['startyear'] = yearmin
    datafilter['endyear'] = yearmax
    datafilter['ctrlist'] = ''
    config = configuration()
    if config['error']:
        return config['error']

    handles = []

    if request.args.get('handle'):
        handledataset = request.args.get('handle')
        handledataset = handledataset.replace(" ", '')
	panelcheck = re.search(r'Panel', handledataset)
	if not panelcheck:
	    handles.append(handledataset)
            handledataset = "Panel[" + handledataset + "]"
	else:
	    (handles, pidslist) = pidfrompanel(handledataset)

    if request.args.get('dataset'):
        dataset = request.args.get('dataset')
        handles.append(dataset)

    if request.args.get('hist'):
	histo = 'on'
    if request.args.get('yearmin'):
        yearmin = request.args.get('yearmin')
	datafilter['startyear'] = yearmin
    if request.args.get('yearmax'):
        yearmax = request.args.get('yearmax')
	datafilter['endyear'] = yearmax
    if request.args.get('ctrlist'):
        ctrlist = request.args.get('ctrlist')
	datafilter['ctrlist'] = ctrlist	

    old = ''
    (names, cleanedpanel) = ({}, [])
    for handle in handles:
        names[handle] = str(handle)

    if old:
        modern = moderncodes(config['modernnames'], config['apiroot'])
        jsonapi = config['apiroot'] + '/api/datasets?handle=' + str(handledataset)

        (panel, cleanedpanel, names) = loadpanel(jsonapi, yearmin, yearmax, ctrlist)
    else:
	if histo:
	    switch = 'historical'
	    loadgeo = 'geocoder'
	else:
            switch = 'modern'
	    loadgeo = ''

	geolist = {}
	(geocoder, geolist, oecd2webmapper, modern, historical) = request_geocoder(config, loadgeo)
        (origdata, maindata, metadata) = request_datasets(config, switch, modern, historical, handles, geolist)
        (subsets, panel) = ({}, [])
	for handle in handles:
            (datasubset, ctrlist) = datasetfilter(maindata[handle], datafilter)
            #datasubset['handle'] = handle
	    meta = metadata[handle]
	    names[handle] = meta['title'] 
	    # Try to remove years columns
	    try:
	        if np.nan in datasubset.index:
	            datasubset = datasubset.drop(np.nan, axis=0)
                if str(np.nan) in datasubset.columns:
                    datasubset = datasubset.drop(np.nan, axis=1)
	    except:
		skip = 'yes'
	    # Try to remove index columns
	    try:
                if config['webmapperoecd'] in datasubset.index:
                    datasubset = datasubset.drop(config['webmapperoecd'], axis=0)
	    except:
		skip = 'yes'

            if not datasubset.empty:
		datasubset['handle'] = handle
                panel.append(datasubset)
    
            subsets[handle] = datasubset
	cleanedpanel = pd.concat(panel)

    #(header, data, countries, handles, vhandles) = advpanel2dict(cleanedpanel)
    #data = advpanel2dict(cleanedpanel)
    #return data.to_html()

    ctrlimit = 200
    data = handle2statistics(handles, cleanedpanel, names)
    showhtml = statistics2table(data)
    return showhtml

@app.route('/totalstatistics')
def totalstatistics(settings=''):
    config = configuration()
    if config['error']:
        return config['error']

    handles = []

    if request.args.get('handle'):
        handledataset = request.args.get('handle')
        (dataset, revid, cliopid, clearpid) = findpid(handledataset)
        handles.append(dataset)

    if request.args.get('dataset'):
        dataset = request.args.get('dataset')
	handles.append(dataset)

    if request.args.get('yearmin'):
        fromyear = request.args.get('yearmin')
    if request.args.get('yearmax'):
        toyear = request.args.get('yearmax')

    html = ''
    for dataset in handles:
        jsonapi = config['apiroot'] + "/collabs/static/data/" + str(dataset) + ".json"
        data = createdata(jsonapi)
        d = data.describe()
        show = d.transpose()
        stats = show.to_html()
        html = html = stats + '<br>'

    return html

@app.route('/export')
def export(settings=''):
    config = configuration()
    if config['error']:
        return config['error']

    activepage = 'Dashboard'
    config = configuration()
    perlbin = "/usr/bin/perl "
    path = config['datapath']
    varproject = request.args.get('project')
    varbase = request.args.get('base')
    dataset = request.args.get('dataset')
    fileID = request.args.get('fileID')
    maincontent = config['error']
    cmd = "/bin/cat " + path + fileID + '.csv'
    docheck = re.match(r'.*[;|\/\:\(\)]', cmd)
    if not docheck:
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        maincontent = p.communicate()[0]
    else:
	maincontent = 'Something went wrong..'
    return maincontent

@app.route('/browse')
def browse(settings=''):
    activepage = 'Dashboard'
    config = configuration()
    if config['error']:
        return config['error']

    pages = getindex(activepage)
    dataverse = config['dataverseroot']
    resp = make_response(render_template('dataverse.html', active=activepage, pages=pages, dataverse=dataverse))
    return resp

@app.route('/settings', methods=['GET', 'POST'])
def signup(settings=''):
    user = ''
    config = configuration()
    if config['error']:
        return config['error']

    (admin, user, tabnum, createnews, editnews) = ('','',0,'','')
    fields = {}
    checkboxes = {}
    fieldslist = ["dataverse", "apitoken", "email", "passwd", "uri", "title", "logo", "description", "summary", "about", "contact", "partners", "news", "newstitle", "newssummary", "newstext"]
    if request.args.get("user"):
	user = request.args.get("user")
	if user == 'admin':
	    admin = 'user'
    try:
        if session['name']:
	    user = session['name']
    except:
	donothing = 0	

    for field in fieldslist:
	cfield = "%s%s" % ("closed", field)
	fields[field] = ''
	fields[cfield] = ''
	if request.args.get(field):
	     fields[field] = request.args.get(field)
	elif request.form.getlist(field):
	    fields[field] = str(request.form.getlist(field)[0])	
        if request.args.get(cfield):
             fields[cfield] = request.args.get(cfield)
        elif request.form.getlist(cfield):
            fields[cfield] = str(request.form.getlist(cfield)[0])

    uriparams = {}
    if request.args:
	for key in request.args.keys():
	    uriparams[key] = str(request.args.getlist(key))
    elif request.form:
	for key in request.form.keys():
	    uriparams[key] = str(request.form.getlist(key))

    for key in uriparams:
	value = uriparams[key]
	#if key == 'datasets':
	if value == "[u'on']":
	    value = 'checked'
	    fields[key] = value
	    checkboxes[key] = value

    if request.args.get('project'):
	fieldsall = readdata('projects', 'uri', request.args.get('project'))
	for f in fieldsall:
	    fields = f
	if request.args.get('view') == 'newseditor':
	    tabnum = 2
 	if request.args.get('action') == 'create':
	    createnews = 'yes'
        if request.args.get('action') == 'edit':
            editnews = 'yes'

	return make_response(render_template('closedprojectdetails.html', fields=fields, checkboxes=str(checkboxes), admin=admin, username=user, tabnum=tabnum, createnews=createnews, editnews=editnews))
    else:
	# Clean settings first
	if len(fields['uri']):
            remove = removedata('projects', 'uri', fields['uri'])
            result = data2store('projects', fields)
	    return redirect(config['apiroot'] + '/' + fields['uri'], code=301)
	else:
	    return make_response(render_template('projectdetails.html', fields=fields, checkboxes=str(checkboxes), admin=admin, username=user))

@app.route('/boundaries')
def boundaries(settings=''):
    config = configuration()
    if config['error']:
        return config['error']

    root = config['apiroot']
    dataset = 'dataframe66_'
    jsondataset = getboundaries(root, dataset)
    return Response(json.dumps(jsondataset), mimetype='application/json')

@app.route('/get')
def get(settings=''):
    config = configuration()
    if config['error']:
        return config['error']

    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    image = request.args.get('image')
    gzip = request.args.get('nlgis')
    svg = request.args.get('svg')
    pdf = request.args.get('pdf')
    outfile = ''

    thismimetype='image'
    if image:
	outfile = image
    if gzip:
	thismimetype = 'application/x-gzip'
	outfile = gzip
    if svg:
	thismimetype = 'text/plain'
	outfile = svg
    if pdf:
	thismimetype = 'application/pdf'
	outfile = pdf
  	
    if image:
        return send_from_directory(imagepathloc, outfile, mimetype=thismimetype)
    else:
	return send_from_directory(imagepathloc, outfile, as_attachment=True)
 	#return outfile + ' not found'

@app.route('/datasets')
def datasets(settings=''):
    config = configuration()
    if config['error']:
        return config['error']

    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    topicapiurl = website + "/api/topicslist"
    topicstats = load_api_data(topicapiurl, '', '', '', '', '')
    localfile = 'index.csv'
    filename = imagepathloc + '/' + localfile
    f = csv.writer(open(filename, "wb+"))

    varlist = []
    firstline = 0
    for code in sorted(topicstats):
        dataset = topicstats[code]
        mapurl = website + "/site?code=" + dataset['topic_code'] + "&year=" + str(dataset['startyear'])
        dataurl = website + '/api/data?code=' + dataset['topic_code']
        topicstats[code]['urlmap'] = mapurl
        topicstats[code]['urldata'] = dataurl
        datarow = []    
        if firstline == 0:
            for row in sorted(dataset):
                varlist.append(row)    
            f.writerow(varlist)
            firstline = 1
        
        for row in sorted(dataset):        
            datarow.append(dataset[row])
        f.writerow(datarow) 
    return send_from_directory(imagepathloc, localfile, as_attachment=True)

@app.route('/print')
def printme():
    config = configuration()
    if config['error']:
        return config['error']

    year = request.args.get("year")
    handle = request.args.get("handle")
    handles = []
    handles.append(handle)

    hquery = formdatasetquery(handles,'')
    datainfo = readdatasets('datasets', json.loads(hquery))
    try:
	for item in datainfo:
	    datasetID = item['datasetID']
    except:
	datasetID = 228
    root = config['dataverseroot'] + "/api/datasets/" + str(datasetID) + "/versions/?key=" + config['key'] + "&show_entity_ids=true&q=authorName:*"
    data = load_api_data(root, 1)
    (title, citation) = get_citation(data['data'])
    uhandle = handle
    uhandle = uhandle.replace('hdl:', '')
    mapcopyright = config['cshapes_copyright']
    if int(year) < 1946:
	mapcopyright = config['geacron_copyright']
    # "Note: Map polygons provided by Geacron <a href=\"geacron.com\">http://www.geacron.com</a>"
    resp = make_response(render_template('printall.html', title=title, citation=citation, mapcopyright=mapcopyright, year=year, handle=handle, uhandle=uhandle))
    return resp

@app.route('/printall')
def printall():
    config = configuration()
    if config['error']:
        return config['error']

    colors = ''# 'greyscale'
    root = request.url
    urigroup = re.search('\?(.+)', root)
    try:
        uri = urigroup.group(1)
    except:
        uri = root
    #webpage = config['apiroot'] + "/collabs/static/v/worldmap.html?start=on&action=map&dataset=4X6NCK&catmax=6&ctrlist=&year=1981&lasty=2010&colors=" + colors
    webpage = config['apiroot'] + "/collabs/static/v/worldmap.html?start=on&action=map&" + str(uri)  
    fileformat = 'png'
    year = '1982'
    code = '4X6NCK'
    imagefile = chartonprint(webpage, fileformat, year, code, config['proxy'])
    return redirect(imagefile, code=301)

@app.route('/advanced')
def advanced(settings=''):
    config = configuration()
    if config['error']:
        return config['error']

    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()

    for name in request.cookies:
	settings = settings + ' ' + name + '=' + request.cookies[name]	
    #return settings

    image = imagepathweb + '/' + year + '.png';

    settings = ''
    resp = make_response(render_template('advanced.html', image=image, settings=settings, r=request.cookies))
  
    # Cookie revision
    for name in request.cookies:
	on = request.cookies[name]
        try: 
	    if request.args[name]: 
	        i = 1
	except:
	    if on == 'on':
		erase[name] = on
	        resp.set_cookie(name, '')

    for name in request.args:
        resp.set_cookie(name, request.args[name])

    return resp

if __name__ == '__main__':
    app.run()
