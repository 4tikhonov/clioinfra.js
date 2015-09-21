#!/usr/bin/python

import subprocess
import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as etree

def download(HOSTNAME, API_TOKEN, tmpdir, fileID, original):
    original = re.sub('\(|\)', '', original)
    url = HOSTNAME + "/api/access/datafile/" + str(fileID) + "?key=" 
    cmd = "/usr/bin/wget -q https://%s%s --no-check-certificate -O %s/%s" % (url, API_TOKEN, tmpdir, original)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
        
    return out

def compile2zip(finaldir, arc):
    cmd = "cd %s;/usr/bin/zip -9 -y -r -q %s *;/bin/mv %s ../" % (finaldir, arc, arc);
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    return finaldir + '/' + arc

def dataset2zip(tmpdir, arc, finaldir):
    #proc = subprocess.Popen("cd %s;/bin/rm *;/usr/bin/zip -9 -y -r -q %s *;/bin/mv %s/%s %s/" % (tmpdir, arc, tmpdir, arc, finaldir), shell=True, stdout=subprocess.PIPE)
    cmd = "mv %s/*.pdf %s/;mv %s/*.doc %s;mv %s/*.docx %s" % (tmpdir, finaldir, tmpdir, finaldir, tmpdir, finaldir);
    #/usr/bin/zip -9 -y -r -q %s *;/bin/mv %s %s/../" % (tmpdir, finaldir, finaldir, arc, arc, finaldir)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()

    return finaldir + '/' + arc

def get_papers(HOSTNAME, API_TOKEN, cmd, pid, tmpdir, arc, finaldir):
    DEBUG = 0
    files = []
    proc = subprocess.Popen("/usr/bin/curl -s %s%s" % (cmd, pid), shell=True, stdout=subprocess.PIPE)
    (xml, err) = proc.communicate()

    y=BeautifulSoup(xml)
    try:
        files = y.html.body.feed.findAll("id")
    except:
	files = []

    for filename in files:
        isfile = re.search(r'file\/(\d+)\/(\S+)', str(filename.string), re.M|re.I)
        if isfile:
            fileID = isfile.group(1)
            fileoriginal = isfile.group(2)
            download(HOSTNAME, API_TOKEN, tmpdir, fileID, fileoriginal)
            if DEBUG:
                print filename.string
                print fileoriginal
    
    zipfile = dataset2zip(tmpdir, arc, finaldir)

    return finaldir

