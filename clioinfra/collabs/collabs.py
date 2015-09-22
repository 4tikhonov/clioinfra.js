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

from flask import Flask, render_template
from flask import g
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
import psycopg2
import psycopg2.extras
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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from boundaries import getboundaries
from statistics import createdata
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from locations import load_locations
from topics import load_alltopics
from locations import load_locations
from historical import load_historical
from tabulardata import loadcodes, load_api_data, countryset, json_dict, createframe, combinedata, data2panel

Provinces = ["Groningen","Friesland","Drenthe","Overijssel","Flevoland","Gelderland","Utrecht","Noord-Holland","Zuid-Holland","Zeeland","Noord-Brabant","Limburg"]
pagelist = ["Home", "Global labor conflicts", "Local labor conflicts", "User Guide", "About"]
urls = ["/", "/worldmap", "/site?year=1927&code=NLSTR&custom=on", "/developers", "/about"]
cpath = "/etc/apache2/strikes.config"
database = 'world_data'

def connect():
        cparser = ConfigParser.RawConfigParser()
        cparser.read(cpath)

        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (cparser.get('config', 'dbhost'), cparser.get('config', 'dbname'), cparser.get('config', 'dblogin'), cparser.get('config', 'dbpassword'))

        # get a connection, if a connect cannot be made an exception will be raised here
        conn = psycopg2.connect(conn_string)

        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        cursor = conn.cursor()

        #(row_count, dataset) = load_regions(cursor, year, datatype, region, debug)
        return cursor

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

def load_api_data(apiurl, code, year, custom, scales, catnum):
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

def loadyears(api_years_url, code, year, custom):
    years = []
    data = load_api_data(api_years_url, code, '', custom, '', '')
    apiyears = []
    indicators = {}
    for item in data['years']:
       apiyears.append(item['year'])
       indicators[item['year']] = item['count']

    if apiyears:
       apiyears = apiyears
    else:
       years.append(year);

    return (apiyears, indicators)

def loadcodes(api_topics_url, code, year, custom):
    codes = []
    data = load_api_data(api_topics_url, '', year, custom, '', '')
    apicodes = []
    indicators = {}
    for item in data['codes']:
       apicodes.append(item['code'])
       indicators[item['code']] = item['topic_name']

    if apicodes:
       codes = apicodes
    else:
       codes.append(code);
    return (codes, indicators)

def load_topics(cursor):
        data = {}
        sql = "select distinct code, indicator from datasets.data";
        #sql = sqlfilter(sql)

        # execute
        cursor.execute(sql)

        # retrieve the records from the database
        data = cursor.fetchall()
        jsondata = json_generator(cursor, 'data', data)

        return jsondata


app = Flask(__name__)

@app.route('/info')
def test():
    description = 'nlgis2 API Service v.0.1<br>/api/maps (map polygons)<br>/api/data (data services)<br>/demo web demo<br>'
    return description

@app.route('/slider')
def slider():
    #return 'slider'
    return render_template('slider.html')

@app.route('/members')
def members():
    return render_template('members.html')

@app.route('/mapslider')
def mapslider():
    (title, steps, customcountrycodes, fromyear, toyear, customyear) = ('', 0, '', '1500', '2012', '') 
    handles = []
    datahub = {}
    dataset = ''
    warning = ''
    hist = {}

    if request.args.get('dataset'): 
        dataset = request.args.get('dataset')
	handles.append(dataset)

    historical = 0

    try:
        (header, panelcells, codes, datahub, data, handle2ind, unit2ind) = data2panel(handles, customcountrycodes, fromyear, toyear, customyear, hist)
	for dataitem in handle2ind:
	    title = handle2ind[dataitem]
    except:
	datahub = {}
	#warning = logging.exception()

    validyears = []
    for year in sorted(datahub):
	validyears.append(year)
	steps = steps + 1
    #validyears = ['1880', '1902', '1934', '1955', '1987', '2012']

    return make_response(render_template('mapslider.html', years=validyears, warning=warning, steps=steps, title=title))

@app.route('/d3map')
def d3map(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    (codes, indicators) = loadcodes(api_topics_url, code, year, custom)
    resp = make_response(render_template('d3colored.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code, indicators=indicators))
    return resp

ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(upload_folder, path):
    upload_folder = upload_folder + '/custom'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
	    datafile = upload_folder + '/' + filename
	    perlbin = "/usr/bin/perl "
	    cmd = perlbin + path + "/scripts/etl/custom_import.pl " + datafile
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            result = p.communicate()[0]
            return datafile 
    return

@app.route('/site', methods=['GET', 'POST'])
def d3site(settings=''):
    selectedcode = {}
    custom_selectedcode = {}
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    #custom = ''
    province = ''
    provinces = Provinces[:]
    apiurl = '/api/maps?' #year=' + year
    dataurl = '/api/data?'
    scaleurl = '/api/scales?'
    mapscale = 6050
    dataapiurl = dataurl + 'code=' + code
    api_topics_url = server + '/api/topics?'
    upload_file(imagepathloc, path)
    thiscustom = custom
    thiscode = code
    if not custom:
        thiscustom = ''
        #thiscode = ''

    (codes, indicators) = loadcodes(api_topics_url, thiscode, year, thiscustom)
    if thiscode:
        selectedcode[thiscode] = indicators[thiscode]
        indicators.pop(thiscode, "none");
    api_years_url = server + '/api/years?'
    (years, yearsinfo) = loadyears(api_years_url, code, '', thiscustom)

    # for custom datasets
    intcustom = 'on'
    if custom:
        intcustom = ''
	#code = ''
    (custom_codes, custom_indicators) = loadcodes(api_topics_url, code, year, intcustom)
#    custom_selectedcode[code] = custom_indicators[code]
    custom_indicators.pop(code, "none");
    (custom_years, custom_yearsinfo) = loadyears(api_years_url, code, '', intcustom)

    showlegend='true';
    if request.args.get('nolegend'):
	showlegend = ''
    if int(year) < 1812:
        mapscale = mapscale * 1.5
	showlegend = ''
    
    template = 'site_tabs.html'
    if custom:
        template = 'site_tabs_custom.html'

    legendscales = ["100-200","50-99", "10-49", "1-9", "0-1"]
    # DATAAPI
    scale = 'calculate'
    catnum = 8 
    # Error
    apiweburl = server + scaleurl
    thisscale = load_api_data(apiweburl, code, year, thiscustom, scale, catnum)
    ranges = []
    if thisscale:
        ranges = json.loads(thisscale)
    colors = []
    legendcolors = []
    scales = []
    legendscales = []
    out = ''
    for sector in sorted(ranges):
        dataitem = ranges[sector]
        colors.append(dataitem['color'])
        scales.append(dataitem['range'])
	out = out + ' ' + dataitem['color']

    urlvar = '' #api_years_url + code
    if thisscale:
        ranges = thisscale.split(', ')
    if colors:
	legendscales = scales
	legendcolors = colors

    if request.args.get('province'):
	province = request.args.get('province')
	provinces.remove(province)
	mapscale = mapscale * 2

    activepage = 'Map'
    pages = getindex(activepage)
    resp = make_response(render_template(template, pages=pages, topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, indicators=indicators, datarange=datarange, selectedcode=selectedcode, thiscode=code, showlegend=showlegend, allyears=years, custom=custom, custom_indicators=custom_indicators, custom_allyears=custom_years, legendscales=legendscales, legendcolors=legendcolors, urlvar=urlvar, categories=catnum, province=province, provinces=provinces, mapscale=mapscale))
    return resp

@app.route('/download')
def download(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
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
        cmd = path + "/node_modules/phantomjs/lib/phantom/bin/phantomjs " + path + "/web/demo/static/renderHTML.js '" + website + page + year + "&code=" + code + "&province=" + province + "&custom=" + custom + "'"
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

@app.route('/thisworld')
def thisworld(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?world=on' #year=' + year
    # /api/maps?&year=1982&world=on
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    if request.args.get('year'):
        year = request.args.get('year')
    #codes = loadcodes(api_topics_url, code, year, custom)
    resp = make_response(render_template('world/world.html', topojsonurl=apiurl, datayear=year))
    #, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code))
    
    return resp

@app.route('/worldmap')
def worldmap(settings=''):
    selectedcode = {}
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    code = 'LCI04'
    showlegend = 'yes'
    thiscustom = ''
    scale = '120'
    catnum = 8
    scaleurl = '/api/scales?'
    apiurl = '/api/maps?world=on' #year=' + year
    # /api/maps?&year=1982&world=on
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    if request.args.get('year'):
        year = request.args.get('year')
    if request.args.get('code'):
        code = request.args.get('code')
    #codes = loadcodes(api_topics_url, code, year, custom)
    # Error
    thiscode = code
    apiweburl = server + scaleurl
    apiweburl = apiweburl + '&db=' + database
    api_topics_url = api_topics_url + '&db=' + database
    api_years_url = server + '/api/years?' + '&db=' + database
    thisscale = ''
    try:
        thisscale = load_api_data(apiweburl, code, year, thiscustom, scale, catnum)
        (codes, indicators) = loadcodes(api_topics_url, thiscode, year, thiscustom)
        (years, yearsinfo) = loadyears(api_years_url, code, '', '')

        if thiscode:
            selectedcode[thiscode] = indicators[thiscode]
            indicators.pop(thiscode, "none");
	#return thisscale
    except:
	#return 'Error ' + apiweburl
	donothing = 1
    ranges = []
    if thisscale:
        ranges = json.loads(thisscale)
    colors = []
    legendcolors = []
    scales = []
    legendscales = []
    out = ''
    for sector in sorted(ranges):
        dataitem = ranges[sector]
        colors.append(dataitem['color'])
        scales.append(dataitem['range'])
        out = out + ' ' + dataitem['color']

    #urlvar = '' #api_years_url + code
    if thisscale:
        ranges = thisscale.split(', ')
    if colors:
        legendscales = scales
        legendcolors = colors
    if request.args.get('nolegend'):
        showlegend = ''

    activepage = 'Map'
    pages = getindex(activepage)
    resp = make_response(render_template('world/worldmap.html', pages=pages, topojsonurl=apiurl, datayear=year, showlegend=showlegend, legendscales=legendscales, legendcolors=legendcolors, indicators=indicators, selectedcode=selectedcode, code=thiscode, allyears=years, database=database))
    return resp

@app.route('/history')
def history(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    codes = loadcodes(api_topics_url, code, year, custom)
    resp = make_response(render_template('menu_history.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code))
    return resp

@app.route('/tabs')
def tabs(settings=''):
    selectedcode = {}
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    #custom = ''
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    upload_file(imagepathloc, path)
    (codes, indicators) = loadcodes(api_topics_url, code, year, custom)
    selectedcode[code] = indicators[code]
    indicators.pop(code, "none");
    api_years_url = server + '/api/years?'
    (years, yearsinfo) = loadyears(api_years_url, code, '', custom)

    showlegend='true';
    if request.args.get('nolegend'):
        showlegend = ''

    resp = make_response(render_template('tabs.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, indicators=indicators, datarange=datarange, selectedcode=selectedcode, thiscode=code, showlegend=showlegend, allyears=years, custom=custom))
    return resp

@app.route('/developers')
def developers(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    api_topics_url = server + '/api/topics?'
    #codes = loadcodes(api_topics_url, code, year, custom)
    codes = []
    activepage = 'User Guide'
    pages = getindex(activepage)
    resp = make_response(render_template('menu_developers.html', active=activepage, pages=pages, topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year, codes=codes, datarange=datarange, selectedcode=code, website=website))
    return resp

@app.route('/presentation')
def presentation(settings=''):
    resp = make_response(render_template('menu_presentation.html'))
    return resp

@app.route('/datasetspace')
def datasetspace(settings=''):
    config = configuration()
    root = config['apiroot']
    jsonapi = root + "/cgi-bin/citations.cgi?dataverse=lb"
    req = urllib2.Request(jsonapi)
    opener = urllib2.build_opener()
    f = opener.open(req)
    citations = simplejson.load(f, "utf-8")
    result = ''
    datasets = []
    for line in citations:
        cite = json.loads(line)
	dataset  = {}
        for item in cite:
            #result = str(result) + '<b>' + str(item) + '</b>' + ' ' + str(cite[item]) + '<br>'
	    result = str(result) + "<b>" + str(item) + "</b>" + " " + str(cite[item]) + "<br>\n"
	    dataset[item] = cite[item]

	try:
	    if cite['Subject']:
	        datasets.append(dataset)
	except:
	    nothing = 1

    #datasets = result
    activepage = 'Dashboard'
    pages = getindex(activepage)

    template = 'citations.html'
    resp = make_response(render_template(template, active=activepage, pages=pages, datasets=datasets))
    return resp

@app.route('/')
def start(settings=''):
    activepage = 'Home'
    path = "/home/strikes/sik/web/collabs/"
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
    apiroot = config['apiroot']
    dataverseroot = config['dataverseroot']
    key = config['key']

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

    pages = getindex(activepage)
    valtitle = ''
    if validate:
	# VALIDATION
	cmd = path + "/../../bin/run-demo.py -d '" + dataverseroot + "' -H '" + dataset + "' -k '" + key + "'"
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        maincontent = p.communicate()[0]
	valtitle = maincontent

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

    resp = make_response(render_template(template, active=activepage, pages=pages, title=title, datasetfile=datasetfile, dataset=dataset, stats=stats, topic=topic, citation=citation, cliopid=cliopid, indicatorlist=indicatorlist, locations=locations, fromyear=fromyear, toyear=toyear, customcountrycodes=customcountrycodes, handle=handle, selectedcountries=selectedcountries, selectedindicators=selectedindicators, cliopids=cliopids))
    return resp

@app.route('/export')
def export(settings=''):
    activepage = 'Dashboard'
    config = configuration()
    perlbin = "/usr/bin/perl "
    path = config['datapath']
    varproject = request.args.get('project')
    varbase = request.args.get('base')
    dataset = request.args.get('dataset')
    fileID = request.args.get('fileID')
    cmd = "/bin/cat " + path + fileID + '.csv'
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    maincontent = p.communicate()[0]
    return maincontent

@app.route('/browse')
def browse(settings=''):
    activepage = 'Dashboard'
    config = configuration()
    pages = getindex(activepage)
    dataverse = config['dataverseroot']
    resp = make_response(render_template('dataverse.html', active=activepage, pages=pages, dataverse=dataverse))
    return resp

@app.route('/about')
def about(settings=''):
    activepage = 'About'
    pages = getindex(activepage)
    resp = make_response(render_template('world/about.html', active=activepage, pages=pages))
    return resp

@app.route('/signup')
def signup(settings=''):
    resp = make_response(render_template('signup.html'))
    return resp

@app.route('/boundaries')
def boundaries(settings=''):
    config = configuration()
    root = config['apiroot']
    dataset = 'dataframe66_'
    jsondataset = getboundaries(root, dataset)
    return Response(json.dumps(jsondataset), mimetype='application/json')

@app.route('/colors')
def colors(settings=''):
    activepage = 'Home'
    pages = getindex(activepage)
    resp = make_response(render_template('world/colorbrewer.html', active=activepage, pages=pages))
    return resp

@app.route('/googlemaps')
def googlemaps(settings=''):
    activepage = 'About'
    pages = getindex(activepage)
    if request.args.get('year'):
        year = request.args.get('year')

    resp = make_response(render_template('world/googlemaps.html', active=activepage, pages=pages, datayear=year))
    return resp


@app.route('/get')
def get(settings=''):
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

def getindex(thispage):
    fulllist = []
    for i, page in enumerate(pagelist):
        pages = {}
        pages['name'] = page
        pages['url'] = urls[i]
        if page == thispage:
            pages['active'] = " class=current"
        else:
            pages['active'] = ''
        fulllist.append(pages)

    return fulllist

@app.route('/index')
def d3index(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    topicapiurl = website + "/api/topicslist"
    topicstats = load_api_data(topicapiurl, '', '', '', '', '')
    topiclist = []
    thisletter = ''
    letters = []
    if topicstats:
        for code in sorted(topicstats):
	    topiclist.append(topicstats[code])
            dataset = topicstats[code]
	    letter = dataset['letter']
            url = "/site?code=" + dataset['topic_code'] + "&year=" + str(dataset['startyear'])
	    topicstats[code]['url'] = url
	    if thisletter == letter:
		topicstats[code]['letter'] = ''
	    else:
	        thisletter = letter
		letters.append(letter)

    activepage = 'Index'
    pages = getindex(activepage)
    resp = make_response(render_template('datasetlist.html', active=activepage, letters=letters, topiclist=topiclist, pages=pages))
    return resp

@app.route('/d3movie')
def d3movie(settings=''):
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    apiurl = '/api/maps?' #year=' + year
    dataapiurl = '/api/data?code=' + code
    resp = make_response(render_template('d3movie.html', topojsonurl=apiurl, datajsonurl=dataapiurl, datayear=year))
    return resp

@app.route('/advanced')
def advanced(settings=''):
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

@app.route('/old', methods=['GET', 'POST'])
def index(year=None,code=None):
    cmdgeo = ''
    (year, code, website, server, imagepathloc, imagepathweb, viewerpath, path, geojson, datarange, custom) = readglobalvars()
    api_topics_url = server + '/api/topics?'

    str = 'Website will be developed to render maps'
    html_code = '<select name=code>' + '<option value\=' + code + '>' + code + '</option>' '</select>'
    year_code = '&nbsp;<input type=text name=year value=' + year + '>&nbsp;<input type=submit name="Submit">';
    #  /home/slava/nlgis2/maps/usecases/maprender.py '10426' 1997 /etc/apache2/htdocs/images/1111

    cmd = viewerpath + ' ' + '""' + ' ' + year + ' ' + imagepathloc + '/' + year + '.png'  
    #cmd = '/bin/echo test'

    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    #response = json.dumps(p.stdout.read()
    result = p.communicate()[0]
    #return cmd
    html = result + '<form>' + html_code + year_code + '<br>' + '<img width=1024 src=\"' + imagepathweb + '/' + year + '.png\">' + '</form>'
    image = imagepathweb + '/' + year + '.png';
    codes = loadcodes(api_topics_url, code, year, custom)

    resp = make_response(render_template('demo.html', codes=codes, year=year, image=image))
    for name in request.args:
       resp.set_cookie(name, request.args[name])

    resp.set_cookie('year', year)
    resp.set_cookie('code', code)
    return resp

if __name__ == '__main__':
    app.run()
