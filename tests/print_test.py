#!/usr/bin/python

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from chartprint import chartonprint
from config import configuration

def print_map(config):
    colors = ''# 'greyscale'
    webpage = "http://localhost/collabs/static/v/worldmap.html?start=on&action=map&handle=hdl:10622/8FCYOX&catmax=6&ctrlist=&year=1981&lasty=2010&colors=" + colors
    fileformat = 'png'
    year = '1981'
    code = '4X6NCK'
    imagefile = chartonprint(webpage, fileformat, year, code, config['proxy'])
    return imagefile

config = configuration()
imagefile = print_map(config)
print imagefile
