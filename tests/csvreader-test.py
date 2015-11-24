#!/usr/bin/python

import urllib2 
import simplejson
import json
import sys
import pandas as pd
import numpy as np
import random
import vincent
from vincent import Axis, AxisProperties, PropertySet, ValueRef
from pandas.io.json import json_normalize
import re
import openpyxl
from openpyxl.cell import get_column_letter
import requests
from StringIO import StringIO

url = "http://dpe.sandbox.socialhistoryservices.org/api/datasets?handle=Panel[%27hdl:10622/MRPFJ0:243:244%27]&format=csv"
res = requests.get(url)
csvio = StringIO(res.content)
dataframe = pd.read_csv(csvio, sep='\t', dtype='unicode')
print dataframe.to_html
