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
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("__file__"), '../../')))
from cliocore.configutils import Configuration, Utils

class ConfigTestClass(unittest.TestCase):
    def test_settings(self):
	self.clioinfra = Configuration()
        self.assertTrue(self.clioinfra.config['dataverseroot'])
	self.assertTrue(self.clioinfra.config['apiroot'])
	self.assertTrue(self.clioinfra.config['key'])

class URITestClass(ConfigTestClass):
    def test_validate_uri(self):
	self.clioinfra = Configuration()
	self.assertFalse(self.clioinfra.is_valid_uri('http://cliodomain.com/xcxc;`some code'))
	# check if passwd can be recognized in uri
	self.assertFalse(self.clioinfra.are_parameters_valid('passwd'), 'passwd recognition problem')
	# wget instance in uri
	self.assertFalse(self.clioinfra.are_parameters_valid('wget` '), 'wget recognition problem')
	self.assertFalse(self.clioinfra.are_parameters_valid('curl '), 'curl recognition problem')
	# other characters are allowed
	self.assertTrue(self.clioinfra.are_parameters_valid("http://data.cliodomain.org/collabs/data/static/"), 'False recognition of characters in url')
	# shell injection check
	self.assertFalse(self.clioinfra.are_parameters_valid("http://data.cliodomain.org/?export?fileId=12;%cat%20/etc/passw1d%20"), 'False recognition of characters in url')

class ToolsTestClass(ConfigTestClass):
   def test_jsonurl(self):
	tools = Utils()
	#geocoder = tools.webmapper_geocoder()	
	#self.assertTrue(geocoder)

	links = tools.graphlinks('handle')
	self.assertTrue(links)

if __name__ == '__main__':
    unittest.main()
