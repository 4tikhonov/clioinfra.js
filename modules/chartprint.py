#!/usr/bin/python

import re
from config import configuration
from subprocess import Popen, PIPE, STDOUT

def chartonprint(webpage, fileformat, year, code): 
    # Print function
    (cmd, size, fileonweb) = ('', '1024', '')

    # Configuration
    config = configuration()
    path = config['path']
    phantompath = config['phantompath']
    imagepathloc = config['imagepath'] 
    filesvg = config['tmpdir'] + '/' + year + '_' + code + '.svg'  

    if fileformat == 'shapefile':
        year = year
    else:
        cmd = phantompath + "/phantomjs/lib/phantom/bin/phantomjs " + path + "/static/renderHTML.js '" + webpage + "'"

        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        html = p.communicate()[0]
        result = re.findall(r'<svg.+?</svg>', html, re.DOTALL)
        if year:
            svgfile = open(filesvg, "w")
            svgfile.write(result[0])
            svgfile.close()

    if fileformat == 'SVG':
        svgfileout = '/get?svg=' + year + '_' + code + '_' + "map.svg"
        return "<a href=\"" + svgfileout + "\">Download SVG file</a>"
        fileonweb = ''

    if fileformat == 'png':
        outfile = year + '_' + code + '_' + 'map.png'
        outdirfile = imagepathloc + '/' + outfile
        cmd = "/usr/bin/inkscape " + filesvg + " -e " + outdirfile + " -h " + size + " -D -b '#ffffff'"
        fileonweb = '/get?image=' + outfile

    if cmd:
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        result = p.communicate()[0]
        image = outfile

    return fileonweb
