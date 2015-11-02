#!/usr/bin/python

import ConfigParser
import getopt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from excel2data import excelvalidator, parsehandle, dataextractor, downloadfile, load_api_data, getfiles
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata
from storage import removedata, data2store, readdata, readdataset, readdatasets, datasetadd, formdatasetquery

def main():
    handle = ''
    dataverse = ''
    customkey = ''
    config = configuration()

    try:
        myopts, args = getopt.getopt(sys.argv[1:],"H:r:d:k:D:")
    except getopt.GetoptError as e:
        print (str(e))
        print("Usage: %s -y year -d datatype -r region -f filename -DDEBUG -o output" % sys.argv[0])
        sys.exit(2)

    (handle, rhandle, customdv) = ('', '', '')
    for o, a in myopts:
        if o == '-H':
            handle=a
	if o == '-r':
	    rhandle=a 
	if o == '-d':
	    dataverse=a
	if o == '-k':
	    customkey=a
	if o == '-D':
	    customdv=a

    dataset = {}
    DEBUG = ''
    path = config['path']
    # Default dataverse
    root = config['dataverseroot']
    key = config['key']
    dvname = config['branch']
    title = 'Title'
    units = 'Units'

    if dataverse:
	root = dataverse
    if customkey:
	key = customkey
    if customdv:
	dvname = customdv

    files = []
    if rhandle:
	contentsapi = root + "/api/dataverses/" + dvname +"/contents?key=" + key
	print contentsapi
	newdata = load_api_data(contentsapi, '')
	metadata = newdata['data']
	for item in metadata:
	    dv = item['id']
	    files = getfiles(root, dv, key)

    if handle:
         print handle
         (datahandle, datasetID, fileID) = parsehandle(handle)
	 files.append(fileID)

    for fileID in files: 
	 fullpath = downloadfile(root, path, fileID, key)
	 print fullpath
	 (pid, revid, cliohandle, clearpid) = findpid(handle)
	 jsonfile = ''
	 #try:
	 if pid:
	     handle = pid
	     try:
	        (jsonfile, tmptitle, tmpunits) = dataextractor(fullpath, path, pid, fileID)
	     except:
		resultfile = config['tmpdir'] + "/" + fileID
		(jsonfile, tmptitle, tmpunits) = excelvalidator(config['phantompath'], fullpath, resultfile, config['tmpdir'])
	
	     if jsonfile:
		remove = removedata('datasets', 'handle', clearpid)
		try:
		    title = str(tmptitle)
		    units = str(tmpunits)
		except:
		    donothing = 1
        	datasetadd(jsonfile, clearpid, handle, title, units)
                print handle
        	print clearpid
	 #except:
	     #print "Dataset " + fullpath + " not extracted..."
	 #print fullpath

if __name__ == "__main__":
    main()
