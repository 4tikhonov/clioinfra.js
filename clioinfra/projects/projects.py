# Copyright (C) 2015 International Institute of Social History.
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

from flask import Flask, render_template, session, url_for, redirect
from flask import g
from flask import Response, request, make_response, request, send_from_directory
from twisted.web import http
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, HiddenField, ValidationError, RadioField,\
    BooleanField, SubmitField, IntegerField, FormField, validators
from wtforms.validators import Required
from werkzeug import secure_filename
import json
import os
import urllib2
import glob
import csv
import sys
import uuid
import re
import string
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../modules')))
from storage import data2store, readdata
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from cliocore.projects import Project
from cliocore.configutils import Configuration, OpenLDAP, Utils

app = Flask(__name__)
UPLOAD_FOLDER = '/home/dpe/tmp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'lnk'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
   return '.' in filename and \
       filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['files']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	    return redirect("%spics/%s" % (request.url_root, filename))
    return 'Upload form'

@app.route('/pics/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

clioinfra = Configuration()
app.secret_key = clioinfra.config['secretkey']

@app.route('/')
def browse(settings=''):
    session['name'] = ''
    return make_response(render_template('iish/projects.html'))

@app.route('/logout', methods=['GET'])
def logout(settings=''):
    session['name'] = ''
    try:
        if session['project']:
            sandboxflag = re.search("sandbox", request.url)
            if sandboxflag:
                projecturl = "%s/%s" % (clioinfra.config['apiroot'], session['project'])
            else:
                projecturl = "%s/%s" % (clioinfra.config['proxy'], session['project'])
	    session['project'] = ''
            return redirect(projecturl, code=302)
	else:
	    return make_response(render_template('iish/login.html'))
    except:
        return make_response(render_template('iish/login.html'))

@app.route('/login', methods=['POST', 'GET'])
def login(settings=''):
    clioinfra = Configuration()
    opensession = {}
    openldap = OpenLDAP()
    if request.args.get('project'):
	opensession['project'] = request.args.get('project')
    else:
	opensession['project'] = ''

    try:
        thisuser = openldap.authentificate(request.form.get('login'), request.form.get('password'))
	if thisuser[0][1]['uid'][0]:
	    session['name'] = thisuser[0][1]['displayName'][0]
	    session['uid'] = thisuser[0][1]['uid'][0]
	    if opensession['project']:
		session['project'] = opensession['project']
	name = str(thisuser[0][1]['displayName'][0])
	if session['project']:
	    sandboxflag = re.search("sandbox", request.url)
	    if sandboxflag:
		projecturl = "%s/%s" % (clioinfra.config['apiroot'], session['project'])
	    else:
	        projecturl = "%s/%s" % (clioinfra.config['proxy'], session['project'])
	    return redirect(projecturl, code=302)
	else:
	    return make_response(render_template('iish/login.html', username=name))
    except:
        return make_response(render_template('iish/login.html'))

@app.errorhandler(404)
def projectpage(e):
    uri = str(request.path)
    branch = ''
    dataverse = 'global'
    project = re.sub('/', '', uri)

    remove = ["date", "_id", "passwd"]
    (projectdata, error) = ('','')
    projectinfo = {}  
    data = {}
    try:
        data = readdata('projects', 'uri', project)
	# Remove data
        for item in data:
            for r in remove:
                if item[r]:
                    item[r] = '' 
	    for var in item:
		value = item[var]
		try:
		    value = re.sub('\n', '<br>', value)
		    if len(value) > 0:
		        projectinfo[var] = value
		except:
		    error = 'no settings'
            projectdata = json.dumps(item, encoding="utf-8", sort_keys=True, indent=4)
    except:
	data = readdata('projects', 'uri', project)
	for item in data:
	    return str(item)
	return 'something went wrong...'

    if not projectdata:
	return project
    else:
	dataverseurl = ''
	try:
	    dataverseurl = projectinfo['dataverse']
	except:
	    dataverse = project

	if dataverseurl:
	    ids = re.search(r'dataverse\/(\w+)', dataverseurl, re.M|re.I)
	    try:
	        branch = ids.group(1)
	        if branch:
		    dataverse = branch
	    except:
	        branch = dataverse

	try:
	    username = session['name']
	except:
	    username = ''

	# Check if browse block should be enabled
	options = ["searchmetadata", "browsedata", "fulltextsearch", "iishdataverses", "harvarddataverse", "workingpapers"
]
	# Check public and closed section parameters
	for item in options:
	    (value, closedvalue) = ('', '')
	    closeditem = "closed%s" % item
	    if item in projectinfo:
	        value = projectinfo[item]
	    if closeditem in projectinfo:
		closedvalue = projectinfo[closeditem]

	    if value:
	        projectinfo['explore'] = 'active'
	    if closedvalue:
		projectinfo['closedexplore'] = 'active'

	return make_response(render_template('iish/content.html', projectdata=projectinfo, dataverse=dataverse, username=username)) 

if __name__ == '__main__':
    app.run()
