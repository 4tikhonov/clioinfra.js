#!/usr/bin/python
# Copyright (C) 2016 International Institute of Social History.
# @author Vyacheslav Tykhonov <vty@iisg.nl>
#
# This program is free software: you can redistribute it and/or  modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# As a special exception, the copyright holders give permission to link the
# code of portions of this program with the OpenSSL library under certain
# conditions as described in each individual source file and distribute
# linked combinations including the program with the OpenSSL library. You
# must comply with the GNU Affero General Public License in all respects
# for all of the code used other than as permitted herein. If you modify
# file(s) with this exception, you may extend this exception to your
# version of the file(s), but you are not obligated to do so. If you do not
# wish to do so, delete this exception statement from your version. If you
# delete this exception statement from all source files in the program,
# then also delete it in the license file.


from __future__ import absolute_import
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname("__file__"), '../../')))
from cliocore.configutils import Configuration, Utils
from cliocore.searchapi import ExtrasearchAPI

class SearchAPITestClass(unittest.TestCase):
   def testsearch(self):
	settings = Configuration()
	sconnection = ExtrasearchAPI(settings.config['dataverseroot'], "labourconflicts")
	self.assertTrue(bool(sconnection.read_all_datasets()))

if __name__ == '__main__':
    unittest.main()
