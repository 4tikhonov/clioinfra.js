#!/usr/bin/python

import pandas as pd
import random
from random import randint
import numpy as np
import brewer2mpl

def getcolors(catnum, pallete):
    colors = []
    allcolors = []
    colormap = 'Paired'
    greycolors = ['#ffffff', '#f0f0f0', '#d9d9d9', '#bdbdbd', '#969696', '#737373', '#525252', '#252525']
    
    if not pallete:
        bmap = brewer2mpl.get_map(colormap, 'Qualitative', catnum+1)
        allcolors = bmap.hex_colors    
    elif pallete == 'greyscale':
        allcolors = greycolors
    
    try:
        nodatacolor = allcolors[0]
        for i in range(1,catnum+1):
            colors.append(allcolors[i])        
    except:
        showwarning('no colors')
    
    return (nodatacolor, colors)

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
    
def getscales(data, colors, catnum):
    values = []
    finalcatnum = 0   
    dataset = {}
    
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
                        colorID = colorID + 1        
                dataset[row[0]] = dataitem
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

