#!/usr/bin/python
import getopt
import urllib2 
import pandas as pd
import re
import json
import simplejson
import ConfigParser
import getopt
from subprocess import Popen, PIPE, STDOUT

def load_api_data(apiurl, fileID):
    jsondataurl = apiurl
    
    req = urllib2.Request(jsondataurl)
    opener = urllib2.build_opener()
    f = opener.open(req)
    dataframe = simplejson.load(f)
    return dataframe

def getfiles(root, dv, key):
    files = []
    if dv:
        newapi = root + "/api/datasets/" + str(dv) + "?key=" + key
        newdata = load_api_data(newapi, '')
        rdata = newdata['data']
	for items in rdata['latestVersion']['files']:
            for fileID in items['datafile']:
                try:
		    known = set(files) 
		    if items['datafile']['id'] in known:
		        donothing = 'ok'
		    else:
                        files.append(items['datafile']['id'])
                except:
                    donothing = 'ok'
    return files

def columns2sql(table, columns):
    sql = "CREATE TABLE " + table + ' (\n'
    for column in columns:
        sqlcolumn = str(column)
        sqlcolumn = re.sub(r'[\[\]\;\,\:\%\/]', '', sqlcolumn)
        sqlcolumn = re.sub(r'\s', '_', sqlcolumn)
        sql = sql + ' ' + sqlcolumn + ' character varying(255) DEFAULT \'\'::character varying,\n'
    sql = re.sub(r'\,$', '', sql)
    sql = sql + ');\n'
    return sql

def parsehandle(handle):
    match = re.search('\:(\S+)\:(\d+)\:(\d+)', handle)
    if match:
        return (match.group(1), match.group(2), match.group(3))
    else:
        return ('', '', '')

def downloadfile(root, path, fileID, key):
    fullpath = path + str(fileID)
    if key:
        cmd = "/usr/bin/wget -q \"" + root + "/api/access/datafile/" + str(fileID) + "?key=" + str(key) + "&show_entity_ids=true&q=authorName:*&format=original\" -O " + fullpath + " --no-check-certificate"
	cmd = "/usr/bin/wget -q \"" + root + "/api/access/datafile/" + str(fileID) + "?key=" + str(key) + "&show_entity_ids=true&q=authorName:*\" -O " + fullpath + " --no-check-certificate"
	print cmd
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        response = p.stdout.read()
    return fullpath

def excelvalidator(path, filename, resultfile, tmpdir):
    # Convert to CSV
    cmd = path + "/../modules/xlsx2csv.py " + filename + " > " + resultfile + ".tmp" 
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    response = p.stdout.read()

    # Read as dataframe
    file = open(resultfile + ".tmp", 'r')
    contents = file.read()
    strings = contents.split("\n")
    columnlen = 0
    for item in strings:
        data = item.split('|')
        if len(data) > columnlen:
            columnlen = len(data)
    matrix = []
    for item in strings:
        data = item.split('|')
        dataset = []
        thislen = len(data)
        for i in range(0, columnlen):
            try:
                dataitem = data[i]
                dataitem = dataitem.replace("\r", "")
                dataset.append(dataitem)
            except:
                dataset.append('')
        matrix.append(dataset)
    df = pd.DataFrame(matrix)
    df = df.fillna('')
    info = df.head()
    #df.convert_objects(convert_numeric=True)
    data = df
    # Columns, title and units
    col = data.ix[2]
    title = data.ix[0][0]
    units = data.ix[1][0]
    csvfile = resultfile + '.csv'
    try:
	df.columns = col
        df.to_csv(csvfile, cols=col, sep='\t', encoding='utf-8')
    except:
	skip = 1

    # Save json
    if col.any():
        d = [
        dict([
        (colname, row[i])
        for i,colname in enumerate(df.columns)
        ])
        for row in df.values
        ]

        jsondatafile = resultfile + '.json'
	contents = json.dumps(d)
	contents = ''
        #with open(jsondatafile, 'w') as filej:
            #filej.write(contents)

    return (jsondatafile, csvfile, title, units)

def dataextractor(fullpath, path, handle, fileID):
    dataset = {}
    (title, units) = ('', '')
    DEBUG = ''
    xl = pd.ExcelFile(fullpath)
    sheetid = 0
    sheets = xl.sheet_names
    fileID = handle

    for sheetname in sheets:
	pd.options.display.float_format = '{:,.0f}'.format
        df = xl.parse(sheetname) #, dtype=int)
	df = df.fillna('')
	if df.columns[0]:
            title = df.columns[0]
            units = df.ix[0][0]

        info = df.head()
        data = df
    
        # Columns first
        col = data.columns
        if DEBUG:
            print '=== ' + sheetname
        tablename = 'dataframe' + str(fileID) + '_' + str(sheetid)
        sql = columns2sql(tablename, col)

        if DEBUG:
            print sql
	csvfile = str(path) + str(tablename) + '.csv'
	#backupcol = df.columns
	#df.columns = data.ix[1]
        df.to_csv(csvfile, cols=col, sep='\t', encoding='utf-8')
	#df.columns = backupcol
        dataset[sheetname] = data

	godata = {}
    	for i,colname in enumerate(df.columns):
            colname = col[i]
	    try:
		noname = re.match("Unnamed", colname)
		noname = re.match("date", colname)
                if noname:
                    skip = i
	    except:
                godata[str(colname)] = i
    
        # Data insert
	#df = df.drop('start date', 1)
	#df = df.drop('end date', 1)
        d = [
        dict([
        (colname, row[i])
        for i,colname in enumerate(df.columns)
        ])
        for row in df.values
        ] 
    
	jsondatafile = path + tablename + '.json'
        with open(path + tablename + '.json', 'w') as filej:
            filej.write(json.dumps(d))
        sheetid = sheetid + 1
	print jsondatafile
	print csvfile
	return (jsondatafile, csvfile, title, units)

    if DEBUG:
        for sheet in dataset:
            print sheet
            print dataset[sheet]
    #print info
