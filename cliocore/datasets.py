#!/usr/bin/python
# Copyright (C) 2016 International Institute of Social History.
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
import urllib2
import simplejson
import json
import pandas as pd
import re
import sys
import io
import string
import os
import csv
from StringIO import StringIO
from cliocore.configutils import Configuration, Utils, DataFilter
from cliocore.storage import Storage

# Dataset class definition and implementation
class Dataset(Configuration):
    def __init__(self):
	Configuration.__init__(self)
        self.topicindex = self.config['topicindex']
	self.database = 'datasets'
        self.storedata = []
        self.data = []
        self.links = {}
	
    def getpidfrompanel(self, pid):
        self.pids = []
        (thispid, revpid, cliopid, self.pidslist) = ('', '', '', '')
        pid = pid.replace("]", "")
        self.match = re.match(r'Panel\[(.+)', pid)
        if self.match:
            pidstr = match.group(1)
            # Remove quotes
            clearpids = re.sub('["\']+', '', pidstr)
            ptmpids = clearpids.split(',')
            for fullhandle in ptmpids:
                (thispid, revpid, cliopid, clearpid) = findpid(fullhandle)           
                self.pids.append(clearpid)
                self.pidslist = self.pidslist + thispid + ','
        else:
            self.pids.append(pid)
            self.pidslist = pid

        self.pidslist = self.pidslist[0:-1]
        return (self.pids, self.pidslist)

    def getindexpid(self):
        if self.topicindex:
            (self.handles, self.pidslist) = self.getpidfrompanel(self.topicindex)
	    return self.handles
 	return false

    def retrievedatasets(self, handles):
	self.storeddata = []
	storage = Storage(self.database)
	if handles:
            self.hquery = storage.formdatasetquery(handles,'')
            self.datainfo = storage.readdatasets(json.loads(self.hquery))
	    for self.item in self.datainfo:
                self.csvio = StringIO(str(self.item['csvframe']))
                self.data = pd.read_csv(self.csvio, sep='\t', dtype='unicode',quoting=csv.QUOTE_NONE)
                self.columns = []
                for itemcol in self.data.columns:
                    self.col = re.sub(r"\"", "", itemcol)
                    self.columns.append(self.col)
                self.data.columns = self.columns
		self.storeddata.append(self.data)
	return self.storeddata

    def clioindex(self):
	self.handles = self.getindexpid()
	storage = Storage(self.database)
	if self.handles:
            self.hquery = storage.formdatasetquery(self.handles,'')
            self.datainfo = storage.readdatasets(json.loads(self.hquery))
            self.csvio = StringIO(str(self.datainfo[0]['csvframe']))
            self.data = pd.read_csv(self.csvio, sep='\t', dtype='unicode',quoting=csv.QUOTE_NONE)
            self.columns = []
            for item in self.data.columns:
                self.col = re.sub(r"\"", "", item)
                self.columns.append(self.col)
            self.data.columns = self.columns
            self.storeddata = storage.readdatasets('')

        self.linking = {}
        for item in self.storeddata:
            try:
                self.linking[item['title']] = item['handle']
            except:
                skip = 'yes'
        self.data['handle'] = ''
        for row in self.data.index:
            title = self.data.ix[row]['Name']
	    uid = self.data.ix[row]['ID']
            try:
                self.data.ix[row]['handle'] = self.linking[title]
		self.links[uid] = self.linking[title]
            except:
                self.data.ix[row]['handle'] = ''
	self.data = self.data.drop('ID', axis=1)
        return self.data

    def findhandles(self, uIDs):
	self.thisuids = []
	if uIDs:
	    uids = uIDs.split(',') 
	    for uid in uids:
		if uid in self.links:
		    self.thisuids.append(self.links[uid])	
	    return self.thisuids
	else:
	    return self.links
