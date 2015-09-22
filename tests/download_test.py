#!/usr/bin/python
import random, string
import os
import sys
import errno
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))

from download import get_papers
def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def testdownload():
    DEBUG = 0
    API_TOKEN="73883b6f-ca99-41b9-953a-b9f8be42723d"
    HOSTNAME="dv.sandbox.socialhistoryservices.org"
    cmd = "--insecure -u " + API_TOKEN + ": https://" + HOSTNAME + "/dvn/api/data-deposit/v1.1/swordv2/statement/study/"
    tmpdir = "/tmp/test"
    filename = randomword(10)
    arc = "data" + filename + ".zip"
    finaldir = "/home/strikes/sik/web/collabs/static/tmp"
    if filename:
	finaldir = str(finaldir) + '/' + str(filename)
	tmpdir = str(tmpdir) + '/' + str(filename)

    pid = "hdl:10622/73BBBI"
    pid = "hdl:10622/4X6NCK"
    try:
	os.mkdir(tmpdir)
        os.mkdir(finaldir)

    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        pass

    zipfile = get_papers(HOSTNAME, API_TOKEN, cmd, pid, tmpdir, arc, finaldir)
    print zipfile
    return

testdownload()
