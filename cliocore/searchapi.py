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
import os
import urllib2

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

import requests
import re

class ExtrasearchAPI:
    def __init__(self, root, dataversename):
        self.config = {}
	self.dataverseroot = root
	self.dataversename = dataversename
	self.handle = 'hdl'
	self.org = '10622'
	self.query = ''

    # read all handles from HTML page
    def read_dataverse_html_page(self, page):
        query = ''
        url = self.dataverseroot + "/dataverse/" + self.dataversename + "?types=datasets"
        if int(page) > 1:
            url+="&page=" + str(page)

        response = urllib2.urlopen(url)
        html = response.read()
        pattern = re.compile(r'>http\:\/\/hdl.handle.net\/\d+\/(\S+)<', re.IGNORECASE)
        match = pattern.findall(html)
        for q in match:
            query+=q + ' '
        
        total = re.search(r'of\s+(\d+)\s+Result', html)            
	if total:
	    results = total.group(1)
	else:
	    results = 1
        return (query, results)

    def load_dataset_page(self, page, pID):
        query = ''
	# full handle check
	if len(pID) < 10:
	   pIDhandle = "%s:%s/%s" % (self.handle, self.org, pID) 
	else:
	   pIDhandle = pID 

        url = "%s/%s=%s" % (self.dataverseroot, page, pIDhandle)    
        response = urllib2.urlopen(url)
        html = response.read()
        return html

    def read_all_datasets(self):
        condition = True
        start = 0
        page = 1
        per_page = 10
        tq = ''
        while (condition):
            (query, total) = self.read_dataverse_html_page(page)    
            results = page * per_page    
            tq+= query
            page+=1
            if results > int(total):
                condition = False
	self.query = tq
        return tq

    # Check if there is restricted dataset
    def has_restricted_data(self, pID):
	html = self.load_dataset_page("dataset.xhtml?persistentId", pID)
        restricted = ''
        pattern = re.compile(r'\/primepush\/ingest(\d+).*class\=\"file\-icon\-restricted\-block\"', re.DOTALL)
        match = pattern.findall(html)
        if match:
            restricted = match[0]
        
        return restricted

    def get_datasets_from_html(root, dataversename):
        query = ''
        url = root + "/dataverse/" + dataversename + "?types=datasets"
        response = urllib2.urlopen(url)

        html = response.read()
        pattern = re.compile(r'>http\:\/\/hdl.handle.net\/\d+\/(\S+)<', re.IGNORECASE)
        match = pattern.findall(html)
        for q in match:
            query+=q + ' '
        return query

    def search_by_handles(self, searchquery):
        (searchhandles, metadata, pids) = ('', [], [])
        if ' ' in searchquery['q']:
    	    pids = searchquery['q'].split()
        if ',' in searchquery['q']:
            pids = searchquery['q'].split(",")

        if not pids:
            return metadata

        for handle in pids:
            ids = re.search(r'hdl\:\d+\/(\w+)', handle, re.M|re.I)
            if ids:
    	        identificator = ids.group(1)
    	        searchhandles = searchhandles + identificator + ' '

        if searchhandles:
     	    searchquery['q'] = searchhandles
    	    metadata = search_by_keyword(self, searchquery)

        return metadata

    def search_by_keyword(self, searchquery):
        if searchquery:
            url = '{0}/search'.format(
                self.native_base_url
            )

     	options = ['q', 'type', 'subtree', 'sort', 'order', 'per_page', 'start', 'show_relevance', 'show_facets', 'fq']

    	# Form parameters URI
      	params = {'key': self.token}
    	for opt in options:
    	    if opt in searchquery:
    		params[opt] = searchquery[opt]

    	resp = requests.get(url, params)

        if resp.status_code == 404:
            raise self.VersionJsonNotFoundError(
                'JSON metadata could not be found for this version.'
            )
        elif resp.status_code != 200:
                raise self.ConnectionError('JSON metadata could not be retrieved.')

        metadata = resp.json()['data']

        return metadata

