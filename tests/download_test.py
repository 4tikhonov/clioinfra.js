#!/usr/bin/python
import random, string
import os
import sys
import errno
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata

from download import get_papers
def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def testdownload():
    config = configuration()
    DEBUG = 0
    API_TOKEN=config['key']
    cmd = "--insecure -u " + API_TOKEN + ": " + config['dataverseroot'] + "/dvn/api/data-deposit/v1.1/swordv2/statement/study/"
    tmpdir = "/tmp/test"
    filename = randomword(10)
    arc = "data" + filename + ".zip"
    finaldir = "/home/dpe/tmp"
    if filename:
	finaldir = str(finaldir) + '/' + str(filename)
	tmpdir = str(tmpdir) + '/' + str(filename)

    pid = "hdl:10622/73BBBI"
    pid = "hdl:10622/4X6NCK"
    pid = "hdl:10622/JPIRSD"
    try:
	os.mkdir(tmpdir)
        os.mkdir(finaldir)

    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        pass

    zipfile = get_papers(config['dataverseroot'], config['key'], cmd, pid, tmpdir, arc, finaldir)
    print zipfile
    return

testdownload()
