#!/usr/bin/python

import pandas as pd
import random
from random import randint
import numpy as np
import brewer2mpl
from config import webmapper_geocoder

def getcolors(catnum, pallete, newcolormap):
    nodatacolor = '#ffffff'
    colors = []
    allcolors = []
    defaultcolormap = 'Paired'
    if newcolormap:
	colormap = newcolormap
    else:
	colormap = defaultcolormap
	
    greycolors = ['#f0f0f0', '#d9d9d9', '#bdbdbd', '#969696', '#737373', '#525252', '#303030', '#101010']
    greycolors_advanced = ['#F8F8F8', '#F0F0F0', '#E8E8E8', '#E0E0E0', '#D8D8D8', '#D0D0D0', '#C8C8C8', '#C0C0C0', '#B8B8B8', '#B0B0B0', '#A8A8A8', '#A0A0A0', '#989898', '#909090', '#888888', '#808080', '#787878', '#707070', '#686868', '#606060', '#585858', '#505050', '#484848', '#404040', '#383838', '#303030', '#282828', '#202020', '#181818', '#101010', '#080808', '#000000']
    
    # If more than 8 categories we should use advanced colors scheme for greyscale
    if catnum > 8:
	greycolors = greycolors_advanced

    if not pallete:
        bmap = brewer2mpl.get_map(colormap, 'Qualitative', catnum+1)
        bmapcolors = bmap.hex_colors    
	#bmapcolors.reverse()
        for i in range(0,catnum):
            allcolors.append(bmapcolors[i])
	#allcolors.reverse()
    elif pallete == 'greyscale':
	#allcolors.append(nodatacolor)
	for c in greycolors:
            allcolors.append(c)
    
    try:
        for i in range(0,catnum):
            colors.append(allcolors[i])        
    except:
        showwarning('no colors')
    
    return (nodatacolor, colors)

def webscales(showrange, colors, defaultcolor):
    webranges = []
    webcolors = []
    webscale = {}
    jsonscale = ''
    
    if showrange:
        rangeitem = {}    
        for i in range(0,len(showrange)):        
            irange = showrange[i]
            icolor = colors[i]
            webranges.append(irange)
            webcolors.append(icolor)
    
	webcolors.reverse()
        webranges.append("no data")
        webcolors.append(defaultcolor)
        webscale['scale'] = webranges
        webscale['colors'] = webcolors
        
    return webscale

def showwarning(tip):
    return tip

def buildcategories(num):
    step = 100 / float(num)
    p = []
    for i in range(num+1):
        if i:
            p.append(i * step)
        else:
            p.append(i)
    return p
    
def getscales(data, colors, catnum, geocoder, original):
    values = []
    finalcatnum = 0   
    dataset = {}
    webmapper = {}
    if geocoder:
        webmapper = webmapper_geocoder()
    
    try:
        # Fill values for dataframe
        for row in data:          
            value = row[2]
            if value != 'NA':
                values.append(value)

        # Calculate ranges based on percentile
        qwranges = []        
        try:
            if values:                
                df = pd.DataFrame(values)
                colormap = []
                p = buildcategories(catnum)                
                result = percentile(df, p)
                
                # Trying to find right categories: 8, 7, ... 1
                for thiscat in reversed(range(catnum+1)):
                    if finalcatnum == 0:
                        if thiscat > 0:
                            p = buildcategories(thiscat)
                            finalcatnum = percentile(df, p)
        except:
            showwarning('no data in dataset')
            
        # Calculate ranges based on percentile
        qwranges = []
        if values:
            df = pd.DataFrame(values)
            pval = 0
            colormap = []
            known = []
            p = buildcategories(catnum)
            for i in p:
                val = round(np.percentile(df, i), 2)
                qwranges.append(val)
                
        # Put data in different colors and ranges
        for row in data:
            value = row[2]
            dataitem = {}
            try:
                if value != 'NA':
                    dataitem['value'] = value                    
                    colorID = 0
                    dataitem['color'] = colors[colorID]
                    dataitem['range'] = 0
                    for validx in qwranges:
                        if dataitem['value'] > validx:
                            dataitem['range'] = validx
                            dataitem['color'] = colors[colorID]
			    if geocoder:
			        dataitem['country'] = row[0]
                        colorID = colorID + 1        

		    # Check if round required
		    rlen = len(str(value))
		    if rlen > 10:
		        rvalue = "%.5f" % value
			try:
			    uvalue = original[str(rvalue)]
			except:
			    uvalue = ''
		        dataitem['value'] = uvalue
		mainindex = row[0]
		if geocoder:
		    try:
		        webmapperindex = webmapper[row[3]]
		    except:
		        webmapperindex = mainindex

		    if webmapperindex:
		        mainindex = webmapperindex

		dataset[mainindex] = dataitem
            except:
                showwarning("can't calculate scales")
    except:
        # No scales
        showwarning('not possible to calculate scales')
        
    if finalcatnum == 0:
        finalcatnum = catnum
        
    return (finalcatnum, qwranges, dataset)

def floattodec(s):
    try:
        c = float(s)
        if int(c) == c:
            return int(c)
        else:
            if c > 10:
                return int(round(c))
            else:
                return s
    except ValueError:
        return s

# Combine all ranges to show on map    
def combinerange(map):
    rangestr = ''
    rangearr = []
    for i in reversed(range(len(map))):
        if i > 0:
            id = i - 1
            min = map[id]
            max = map[i]
            rangestr = rangestr + str(min) + ' - ' + str(max) + ', '
            rangearr.append(str(floattodec(min)) + ' - ' + str(floattodec(max)))
    rangestr = rangestr[:-2]
    return (rangearr, rangestr)

