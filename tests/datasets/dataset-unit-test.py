#!/usr/bin/python

from __future__ import absolute_import
import os
import sys
import unittest
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("__file__"), '../../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("__file__"), '../../modules')))
from cliocore.configutils import Configuration
from cliocore.datasets import Dataset

class ConfigTestClass(unittest.TestCase):
    def test_settings(self):
        self.clioinfra = Dataset()
	clioindex = self.clioinfra.clioindex()
	self.assertTrue(clioindex.to_html())
	uids = '11007,11002'
	self.assertTrue(self.clioinfra.findhandles(uids))
        self.assertTrue(self.clioinfra.config['dataverseroot'])
        self.assertTrue(self.clioinfra.config['apiroot'])
        self.assertTrue(self.clioinfra.config['key'])

if __name__ == '__main__':
    unittest.main()
