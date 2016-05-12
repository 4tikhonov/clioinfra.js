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
from __future__ import absolute_import
import json
import pandas as pd
import re
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../')))
from cliocore.configutils import Configuration, Utils, DataFilter
from cliocore.storagemanager import Storage
from datasets import content2dataframe

# Dataset class definition and implementation
class Geocoder(Configuration):
    def __init__(self):
        Configuration.__init__(self)
        self.geocoderhandle = self.config['geocoderhandle']
	(self.classification, self.geodataset, self.title, self.units) = content2dataframe(self.config, self.geocoderhandle)

    def historical(self):
	return self.geonames

    def modernboundaries(self):
	self.modern.index = self.modern['ccode']
	return self.modern

    def selectint(self, cols):
        (isint, notint) = ([], [])
        for colname in cols:
            tmpvar = ''
            if str(colname) != 'nan':
                colname = re.sub(r'(\d+)\.0', r'\1', str(colname))
                try:
                    tmpvar = int(str(colname))
                    isint.append(tmpvar)
                except:
                    notint.append(colname)
        return (isint, notint)

    def buildgeocoder(self, filtersettings):
        self.geodict = {}
        self.geonames = []
        self.geolist = {}
        self.oecd = {}
        self.geocoder = self.geodataset.convert_objects(convert_numeric=True)
	self.modern = self.geocoder
   	self.modern = self.modern.loc[self.modern[self.config['webmapperoecd']] > 0]
	if filtersettings.datafilter['classification'] == 'modern':
	    self.geocoder = self.modern
	    self.geocoder.index = self.geocoder[self.config['webmapperoecd']]
	else:
            self.geocoder.index = self.geocoder[self.config['webmappercode']]

	# Apply filter
        if filtersettings.minyear():
            self.geocoder = self.geocoder.loc[self.geocoder['start year'] >= filtersettings.minyear()]
        if filtersettings.maxyear():
            self.geocoder = self.geocoder[self.geocoder['start year'] <= filtersettings.maxyear()]
        (self.cfilter, self.notint) = self.selectint(self.geocoder.index)

        i = 0
        for cID in self.cfilter:
            geoitem = {}
            geoitem['id'] = ''
            ignore = 0
            try:
                countryitem = self.geocoder.ix[cID]
                mainID = int(countryitem[self.config['webmappercode']])
                geoitem['id'] = int(countryitem[self.config['webmappercode']])
                geoitem['validfrom'] = int(countryitem['start year'])
                geoitem['validuntil'] = int(countryitem['end year'])
                years = '(' + str(int(countryitem['start year'])) + '-' + str(int(countryitem['end year'])) + ')'
		if filtersettings.datafilter['classification'] == 'modern':
		    geoitem['label'] = str(countryitem[self.config['webmappercountry']])	
		    geoitem['id'] = int(countryitem[self.config['webmapperoecd']])
		else:
                    geoitem['label'] = countryitem[self.config['webmappercountry']] + ' ' + str(years)
                geoitem['year'] = str(countryitem[self.config['webmappercountry']]) + ' ' + years
                geoitem['name'] = str(countryitem[self.config['webmappercountry']])
                self.geolist[int(geoitem['id'])] = geoitem['label']
                try:
                    self.oecd[int(countryitem[self.config['webmapperoecd']])] = int(geoitem['id'])
                except:
                    skipoecd = 'on'
            except:
                ignore = cID

            if ignore == 0:
                if 'name' in filtersettings.datafilter:
		    searchname = filtersettings.datafilter['name']
                    result = re.search(r"^%s" % searchname, geoitem['name'], flags=re.IGNORECASE)
                    if result:
                        if geoitem['name']:
                            self.geodict[geoitem['label']] = geoitem
                else:
                    if geoitem['id']:
                        self.geodict[geoitem['label']] = geoitem
            i = i + 1

        for name in sorted(self.geodict.keys()):
            self.geonames.append(self.geodict[name])

        return (self.geonames, self.geolist, self.oecd)
