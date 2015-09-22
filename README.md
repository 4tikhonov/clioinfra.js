# Clio Infra visualization framework 
## Clioinfra.js
=====
Copyright (C) 2015 International Institute of Social History.
http://www.socialhistory.org

## Major features
- Visualization of research datasets on charts and graphs
- Historical maps
- Descriptive statistics 
- Datasets search and browse functionality

## Project team
Project leader: Bas van Leeuwen <bas.van.leeuwen@iisg.nl> 
Information analyst: Jerry de Vries <jvr@iisg.nl>
Architecture and development: Vyacheslav Tykhonov <vty@iisg.nl>

## Demo
[GDP per capita visualization](http://clearance.sandbox.socialhistoryservices.org/collabs/dashboard?action=visualize&yearmin=1500&yearmax=2012&loc=250&loc=276&loc=528&loc=380&loc=724&dataset=hdl%3A10622%2F4X6NCK%3A114%3A115)

## Installing prerequisites
```
sudo apt-get install build-essential
```
## Installation instructions
```
apt-get install postgresql-8.4
apt-get install postgresql-server-dev-8.4
apt-get install mongodb
apt-get install apache2
apt-get install libapache2-mod-wsgi
apt-get install git
apt-get install python-pip
apt-get install gdal-bin
sudo apt-get update
sudo apt-get install python-software-properties python python-dev python-gdal g++ make
apt-get install inkscape
sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
sudo npm install -g topojson
To verify the two installations, try
which ogr2ogr
which topojson
```
This should print /usr/local/bin/ogr2ogr and /usr/local/bin/topojson

## Python packages
```
pip install flask
pip install twisted
pip install flask_bootstrap
pip install flask_appconfig
pip install flask_wtf
pip install psycopg2
pip install simplejson
pip install xlwt
pip install numpy --upgrade
pip install pandas
pip install pymongo
pip install brewer2mpl
```

### Change default encoding:
```
sudo vi /usr/lib/python2.7/site.py
Change
encoding = "ascii"
to
encoding = "utf8"

