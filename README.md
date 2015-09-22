# Clio Infra visualization framework 
## Clioinfra.js
```
Copyright (C) 2015 International Institute of Social History.
http://www.socialhistory.org
```

## Major features
- Integration with Dataverse (https://github.com/IQSS/dataverse)
- Visualization of research datasets on charts and graphs
- Historical maps
- Descriptive statistics and histograms 
- Datasets search, browse and download functionality
- Customized scales

## Project team
```
Project leader: Bas van Leeuwen <bas.van.leeuwen@iisg.nl> 
Information analyst: Jerry de Vries <jvr@iisg.nl>
Frontend development: Gaele Strootman <gaele@guruburu.com>
Architecture, development and integration: Vyacheslav Tykhonov <vty@iisg.nl>
```

## Demo
[Search and browse Clio Infra datasets](http://cliov4.sandbox.socialhistoryservices.org/datasets/search)

[Interactive dashboard](http://clearance.sandbox.socialhistoryservices.org/collabs/dashboard?action=visualize&yearmin=1500&yearmax=2012&loc=250&loc=276&loc=528&loc=380&loc=724&dataset=hdl%3A10622%2F4X6NCK%3A114%3A115)

[Data visualization on historical maps](http://clearance.sandbox.socialhistoryservices.org/collabs/mapslider?action=map&year=1981&dataset=4X6NCK&colors=greyscale)

## Reports and papers
[OECD: How Was Life? Global Well-being since 1820] (http://adapt.it/englishbulletin/wp/wp-content/uploads/2014/10/oecd_2_10_2014.pdf)

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

