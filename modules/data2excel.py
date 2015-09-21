#!/usr/bin/python

import xlsxwriter
import xlwt
import sys

def panel2excel(datadir, filename, header, panelcells):
    wb = xlwt.Workbook(encoding='utf')

    f_short_name = "Data"
    ws = wb.add_sheet(str(f_short_name))
    style_string = "font: bold on; borders: bottom medium"
    style = xlwt.easyxf(style_string)

    i = 0
    col_width = 256 * 20
    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font
    for row in header:
        ws.col(i).width = col_width
        ws.write(0, i, row, style=style)
        i = i+1

    f_copyrights_name = "Copyrights"
    copyrights = "Clio Infra (2015) http://www.clio-infra.eu"

    wscop = wb.add_sheet(str(f_copyrights_name))
    wscop.write(0,0,copyrights)

    i = 0
    for dataitem in panelcells:
        i = i + 1
        for j in range(0, len(dataitem)):
            value = dataitem[j]
            if value == 'NaN':
                value = ''
            ws.write(i, j, value)

    fullpath = datadir + "/" + filename
    wb.save(fullpath)

    return fullpath 

def individual_dataset(datadir, filename, indicator, units, inputdatahub, data, codes):
    wb = xlwt.Workbook(encoding='utf')

    f_short_name = "Data"
    ws = wb.add_sheet(str(f_short_name))
    style_string = "font: bold on; borders: bottom medium"
    style = xlwt.easyxf(style_string)
    simplestyle = xlwt.easyxf(style_string)

    i = 0
    col_width = 256 * 20
    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font
    font = xlwt.Font()
    font.bold = False
    simplestyle.font = font

    (x,y) = (0,0)
    startX = 2
    startY = 2
    x = startX    
    ws.col(0).width = col_width
    ws.col(1).width = col_width + 256 * 40
    ws.write(0, 0, indicator, style=style)
    ws.write(1, 0, units, style=style)
    ws.write(2, 0, 'Code', style=style)
    ws.write(2, 1, 'Continent, Region, Country', style=style)

    datahub = {}
    limit = 224
    limy = 0
    for year in sorted(inputdatahub):
        try:
            dataitem = data[year]
        except:
            dataitem = []

        for item in dataitem:
            datacode = item[1]
            datavalue = item[6]
	    if datavalue == 'NaN':
		datavalue = ''

	    if datavalue:
	        datahub[year] = inputdatahub[year]
	  	#print str(year) + ' ' + str(datavalue)
	    limy = limy + 1
    
    codeID = startX 
    for code in sorted(codes):
        codeID = codeID + 1
        country = codes[code]
        ws.write(codeID, 0, code)
        ws.write(codeID, 1, country)
    
    y = startY 
    for year in sorted(datahub):        
        ws.write(2, y, year, style=style)
        y = y + 1
    
    y = startY
    for year in sorted(datahub):
        codes = datahub[year]
	dataitem = []
	try:
            dataitem = data[year]
	except:
	    dataitem = []
        #print str(year) + str(codes)
        print dataitem
        dataindex = {}
        for item in dataitem:
            datacode = item[1]
            datavalue = item[6]                        
            if datavalue == 'NaN':
                datavalue = ''
            dataindex[str(datacode)] = datavalue                
        
        # Filling columns
        for code in sorted(codes):
            country = codes[code]               
            x = x + 1
	    try:
                value = dataindex[str(code)]
	    except:
		value = ''
            print str(x) + ',' + str(y) + ':' + str(value)
            ws.write(x, y, value)
        
        # New row
        x = startX 
        y = y + 1
    
    fullpath = datadir + "/" + filename
    wb.save(fullpath)    
    return fullpath
