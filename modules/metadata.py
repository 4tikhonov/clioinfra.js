#!/usr/bin/python

import re
import sys
sys.path.append('/home/strikes/clioinfra/modules')
from config import configuration, load_dataverse, findpid

def metadata(dataset):
    #return ('xxx', '', '')
    config = configuration()
    (pid, fileid) = findpid(dataset)
    #return ('xxx', '', '')
    data = {}
    if pid:
        query = pid
        apiurl = config['dataverseroot'] + "/api/search?q=" + query + '&key=' + config['key'] + '&type=dataset'
        data = load_dataverse(apiurl)
    return (data, pid, fileid)
