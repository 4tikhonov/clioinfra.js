#!/usr/bin/python

import math
import pandas as pd
import random
from random import randint
import numpy as np
import brewer2mpl
from config import webmapper_geocoder
import math
import re

def value2scale(value, logscale, original):
    convertedvalue = 0
    if logscale:
        origvalue = value
        rvalue = "%.1f" % value
        if logscale:
            try:
                if logscale == '2':
                    value = math.log(value, int(logscale))
                elif logscale == '10':
                    value = math.log10(value)
                else:
                    value = math.log(value)
                    rvalue = "%.5f" % value
		convertedvalue = value
            except:
                value = 'NaN'
                rvalue = 'NaN'
                original[str(rvalue)] = origvalue
        else:
            original[origvalue] = origvalue
    else:
	convertedvalue = value

    return (convertedvalue, original)

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
    
def get_normal_scale(catmax, valarray):
    (amin, amax) = (valarray.min(), valarray.max())    
    diff = (amax - amin)/catmax
    ranges = []
    for i in range(1,catmax+1):
        imin = amin + (i-1) * diff
        imax = amin + i * diff
        #print str(imin) + ' ' + str(imax)
        ranges.append(imin)
    ranges.append(imax)
    return ranges

def getscales(config, data, colors, catnum, geocoder, original, histclass, logscale):
    values = []
    finalcatnum = 0   
    (webmapper, geoison) = ({}, '')
    dataset = {}
    try: 
        if not geocoder.empty:
            webmapper = geocoder #webmapper_geocoder()
	    geoison = 'on'
    except:
	geoison = ''
    
    try:
    #if data:
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

        valdata = pd.DataFrame(values)
        qwranges = get_normal_scale(catnum, valdata.values.astype('float64'))
                
        # Put data in different colors and ranges
        for row in data:
            value = row[2]
            dataitem = {}
            #try:
	    if value:
                if value != 'NA':
                    dataitem['value'] = value                    
                    colorID = 0
                    dataitem['color'] = colors[colorID]
                    dataitem['range'] = 0
                    for validx in qwranges:
                        if dataitem['value'] > validx:
                            dataitem['range'] = validx
                            dataitem['color'] = colors[colorID]
			    if geoison:
				try:
			            dataitem['country'] = webmapper.ix[row[3]][config['webmappercountry']]
				except:
				    dataitem['country'] = row[0] + ' problem'
				dataitem['id'] = str(row[3])
                        colorID = colorID + 1        

		    # Check if round required
		    rlen = len(str(value))
		    rvalue = value
		    if rlen > 10:
		        rvalue = "%.2f" % value
			#rvalue = value
			try:
			    uvalue = original[str(rvalue)]
			except:
			    uvalue = ''
		    dataitem['value'] = rvalue
		mainindex = str(row[0])
		if geoison:
		    mainindex = str(row[3])
		    if histclass == 'modern':
			try:
			    mainindex = int(webmapper.ix[row[3]][config['webmappercode']])
			except:
			    mainindex = str(row[3])

		dataset[mainindex] = dataitem
            #except:
	    else:
                showwarning("can't calculate scales")
    except:
    #else:
        # No scales
        showwarning('not possible to calculate scales')
        
    if finalcatnum == 0:
        finalcatnum = catnum
        
    realranges = []
    if logscale:
	for val in qwranges:
	    val = math.pow(int(logscale),val) 
	    realranges.append(val)
    	    qwranges = realranges
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

def roundme(thisval):
    toround = 3
    strval = str(thisval)
    dots = re.search(r'\.(.+)', strval)
    afterdots = 0
    if dots:
        afterdots = len(dots.group(1))
    if afterdots > toround:
        thisval = round(thisval, toround)
    return thisval

# Combine all ranges to show on map    
def combinerange(map):
    rangestr = ''
    rangearr = []
    for i in reversed(range(len(map))):
        if i > 0:
            id = i - 1
            imin = str(roundme(floattodec(map[id])))
            imax = str(roundme(floattodec(map[i])))
            rangestr = rangestr + str(imin) + ' - ' + str(imax) + ', '
            rangearr.append(str(imin) + ' - ' + str(imax))
    rangestr = rangestr[:-2]
    return (rangearr, rangestr)

