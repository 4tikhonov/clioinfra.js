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
    if key:
	fullpath = path + str(fileID)
        cmd = "/usr/bin/wget -q \"" + root + "/api/access/datafile/" + str(fileID) + "?key=" + key + "&show_entity_ids=true&q=authorName:*\" -O " + fullpath + " --no-check-certificate"
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        response = p.stdout.read()
    return fullpath

def dataextractor(fullpath, path, handle, fileID):
    dataset = {}
    DEBUG = ''
    xl = pd.ExcelFile(fullpath)
    sheetid = 0
    sheets = xl.sheet_names
    fileID = handle

    for sheetname in sheets:
        df = xl.parse(sheetname)
	df = df.fillna('')
        info = df.head()
        data = df
	print info
    
        # Columns first
        col = data.columns
        if DEBUG:
            print '=== ' + sheetname
        tablename = 'dataframe' + str(fileID) + '_' + str(sheetid)
        sql = columns2sql(tablename, col)

        if DEBUG:
            print sql
        df.to_csv(path + tablename + '.csv', cols=col, sep='\t', encoding='utf-8')
        dataset[sheetname] = data

	godata = {}
    	for i,colname in enumerate(df.columns):
            colname = col[i]
            noname = re.match("Unnamed", colname)
            if noname:
                skip = i
            else:
                godata[str(colname)] = i
    
        # Data insert
        d = [
        dict([
        (colname, row[i])
        for i,colname in enumerate(df.columns)
        ])
        for row in df.values
        ] 
    
        with open(path + tablename + '.json', 'w') as filej:
            filej.write(json.dumps(d))
        sheetid = sheetid + 1

    if DEBUG:
        for sheet in dataset:
            print sheet
            print dataset[sheet]
    #print info
