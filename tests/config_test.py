#!/usr/bin/python

import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../modules')))
from config import configuration, dataverse2indicators, load_dataverse, findpid, load_metadata, load_fullmetadata, pidfrompanel

class TestConfiguration(unittest.TestCase):
    config = configuration()

    def testconf(self):
	dataset = 'hdl:10622/XUH7BG:65:66'
	dataset = "hdl:10622/I0YK5M:111:112"
	dataset = "hdl:10622/4X6NCK"

	if dataset:
    	    (handle, revid, cliopid, clearpid) = findpid(dataset)
    	    print handle

	(metadata, pid, fileid, clio) = load_metadata(dataset)
	print pid
	for item in metadata:
    	    print item['name']

	branch = 'clio1clio'
	#datasets = dataverse2indicators(branch)
	#print datasets

	pid = "Panel['hdl:10622/4X6NCK','hdl:10622/4X6NCG']"
	(pids, pidstr) = pidfrompanel(pid)
	print '\n' + pidstr
	self.assertEqual(str(pids), "['4X6NCK', '4X6NCG']")

	dataset = "4X6NCK,I0YK5M"
        if dataset:
	    metadata = load_fullmetadata(dataset)
	    for item in metadata:
	        print str(item['name']) + ' ' + str(item['authors'])
	    self.assertEqual(dataset, dataset)

if __name__ == '__main__':
    unittest.main()
