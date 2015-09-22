#!/usr/bin/python
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from boundaries import getboundaries

root = 'http://clearance.sandbox.socialhistoryservices.org'
dataset = 'dataframe66_'
jsondataset = getboundaries(root, dataset)
print jsondataset
