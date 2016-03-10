#!/usr/bin/python

from __future__ import absolute_import
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("__file__"), '../../')))
from cliocore.configutils import Configuration

class ConfigTestClass(unittest.TestCase):
    def test_settings(self):
	self.clioinfra = Configuration()
        self.assertTrue(self.clioinfra.config['dataverseroot'])
	self.assertTrue(self.clioinfra.config['apiroot'])
	self.assertTrue(self.clioinfra.config['key'])

class URITestClass(ConfigTestClass):
    def test_validate_uri(self):
	self.clioinfra = Configuration()
        if self.clioinfra.not_valid_uri('passwd'):
            print self.clioinfra.config['error']
        if self.clioinfra.not_valid_uri('`wget'):
            print self.clioinfra.config['error']
        if self.clioinfra.not_valid_uri('|'):
            print self.clioinfra.config['error']


if __name__ == '__main__':
    unittest.main()
