#!/usr/bin/python

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname("__file__"), '../modules')))
from chartprint import chartonprint

def print_map():
    colors = ''# 'greyscale'
    webpage = "http://dpe.sandbox.socialhistoryservices.org/collabs/static/v/worldmap.html?start=on&action=map&dataset=4X6NCK&catmax=6&ctrlist=&year=1981&lasty=2010&colors=" + colors
    fileformat = 'png'
    year = '1981'
    code = '4X6NCK'
    imagefile = chartonprint(webpage, fileformat, year, code)
    return imagefile

imagefile = print_map()
print imagefile
