Clio Infra visualization framework (clioinfra.js)
=====
Copyright (C) 2015 International Institute of Social History.

@author Vyacheslav Tykhonov <vty@iisg.nl>

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

