#!/usr/bin/python

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from years import years_per_dataset
url = "http://clearance.sandbox.socialhistoryservices.org/api/years?handle=4X6NCK114_115&db=strikes_test"
years = years_per_dataset(url)
print years
