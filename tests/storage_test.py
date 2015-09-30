#!/usr/bin/python

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from storage import data2store, readdata
x = readdata('projects', "author", "Mike")
for item in x:
    for i in item:
        print i
