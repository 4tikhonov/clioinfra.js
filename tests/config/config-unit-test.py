#!/usr/bin/python

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
	# check if passwd can be recognized in uri
	self.assertTrue(self.clioinfra.not_valid_uri('passwd'), 'passwd recogntion problem')
	# wget instance in uri
	self.assertTrue(self.clioinfra.not_valid_uri('wget`'), 'wget recognition problem')
	# other characters are allowed
	self.assertFalse(self.clioinfra.not_valid_uri("some_clear_url"), 'False recognition of characters in url')

class ToolsTestClass(ConfigTestClass):
   def test_jsonurl(self):
	tools = Utils()
	#geocoder = tools.webmapper_geocoder()	
	#self.assertTrue(geocoder)

	links = tools.graphlinks('handle')
	self.assertTrue(links)

if __name__ == '__main__':
    unittest.main()
