#!/usr/bin/python
import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from boundaries import getboundaries
from config import configuration

class TestBoundaries(unittest.TestCase):

  def test_boundaries(self):
	config = configuration()
	root = config['apiroot']
	dataset = 'dataframe66_'
	countries = getboundaries(root, dataset)
	self.assertEqual(countries[1879][0], 'Austria-Hungary')

if __name__ == '__main__':
    unittest.main()
