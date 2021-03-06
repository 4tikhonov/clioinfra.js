# Clio Infra visualization framework 
Clio Infra is a research project to document and analyse the various dimensions of global inequality
between 1500 and the present. Scholars from the International Institute of Social History (IISH) and the
universities of Utrecht, Groningen and Tuebingen supported by National Science Foundation (NWO) and
Royal Academy of Sciences (KNAW) are organizing collaboratories aimed at collecting and standardizing
economic-historical datasets to that purpose. 

An example of the Maddison project, which aims at continuing
the international comparative work on historical national accounting organized by Angus Maddison in the
past, resulting in his well-known global dataset. Similar networks of scholars working on measures of
economic performance (real wages, heights, life expectancy) and their determinants (human capital,
institutions, gender inequality) are producing high quality global datasets on these topics, covering the world
in the past 500 years. 

Recently also indices of sustainability have been integrated into the Clio Infra
framework. 
```
Copyright (C) 2015 International Institute of Social History.
http://www.socialhistory.org
```

## Major features of Clioinfra.js
- Integration with Dataverse (https://github.com/IQSS/dataverse)
- Panel data download of all available indicators
- Visualization of research datasets on charts and graphs
- Historical maps
- Descriptive statistics and histograms 
- Datasets search, browse and download functionality
- Customized scales

## Project team
```
Project coordinator: Bas van Leeuwen <bas.van.leeuwen@iisg.nl> 
Information analyst: Jerry de Vries <jvr@iisg.nl>
Frontend development: Gaele Strootman <gaele@guruburu.com>
Architecture, development and integration: Vyacheslav Tykhonov <vty@iisg.nl>
```

## Demo
[Search and browse Clio Infra datasets](http://cliov4.sandbox.socialhistoryservices.org/datasets/search)

[Interactive dashboard](http://dpe.sandbox.socialhistoryservices.org/collabs/dashboard?action=visualize&yearmin=1500&yearmax=2012&loc=250&loc=276&loc=528&loc=380&loc=724&dataset=hdl%3A10622%2F4X6NCK%3A114%3A115)

[Data visualization on historical maps](http://dpe.sandbox.socialhistoryservices.org/collabs/mapslider?action=map&year=1981&handle=hdl:10622/4X6NCK)

[Panel data visualization](http://dpe.sandbox.socialhistoryservices.org/collabs/panel?start=on&aggr=on&hist=&handle=Panel[%27hdl%3A10622/4X6NCK%27%2C%20%27hdl%3A10622/F16UDU%27]&ctrlist=276%2C528&yearmin=1900&yearmax=2013)

[Descriptive statistics](http://dpe.sandbox.socialhistoryservices.org/collabs/statistics?start=on&aggr=on&hist=&handle=Panel[%27hdl%3A10622/4X6NCK%27%2C%20%27hdl%3A10622/F16UDU%27]&ctrlist=&yearmin=1900&yearmax=2013)

## Reports and papers
[OECD: How Was Life? Global Well-being since 1820] (http://adapt.it/englishbulletin/wp/wp-content/uploads/2014/10/oecd_2_10_2014.pdf)

## Presentations
[Data analysis in Dataverse & visualization of datasets on historical maps](http://projects.iq.harvard.edu/dataverse-community-meeting/people/vyacheslav-tykhonov)
Dataverse Community Meeting 2015, IQSS, Harvard University, June 2015

## Installing prerequisites
```
sudo apt-get install build-essential
```
## Installation instructions
```
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
sudo apt-get install python-pandas
sudo apt-get install python-matplotlib
sudo apt-get install python-bs4
sudo apt-get install zip
apt-get install python-pymongo
sudo apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev
apt-get install catdoc
sudo a2enmod headers
sudo npm install -g topojson
To verify the two installations, try
which ogr2ogr
which topojson
```
This should print /usr/local/bin/ogr2ogr and /usr/local/bin/topojson

## Python packages
```
pip install flask
pip install requests
pip install twisted
pip install flask_bootstrap
pip install flask_appconfig
pip install flask_wtf
pip install psycopg2
pip install simplejson
pip install xlwt
pip install numpy --upgrade
pip install pymongo
pip install brewer2mpl
pip install vincent
pip install palettable
pip install xlsxwriter
pip install lxml 
```

### Change default encoding:
```
sudo vi /usr/lib/python2.7/site.py
Change
encoding = "ascii"
to
encoding = "utf8"
```

### Configuration
The example of configuration file clioinfra.config
```
[config]
path = /home/somepath/clioinfra.js/clioinfra/collabs
dataverseroot = http://dv.sandbox.socialhistoryservices.org
key = 73883b6f-somekey-11111
apiroot = http://dpe.sandbox.socialhistoryservices.org
branch = clio1clio
datapath = /home/somepath/data/
perl = /usr/bin/perl
modernnames = F16UDU
tmpdir = /tmp/test
imagepath = /home/somepath/clioinfra.js/clioinfra/collabs/static
phantompath = /home/somepath/clioinfra.js/node_modules
defaulthandle = hdl:10622/4X6NCK
ctrlist = 380,528,276,250,724,56,756
geocoderapi = http://geo-proxy.sandbox.socialhistoryservices.org/iisg/new/ids
# Standard codes
moderncode = Code
webmapperoecd = ccode
webmappercode = Webmapper numeric code
webmapperstartyear = 1500
webmappercountry = country name
moderncountry = Continent, Region, Country
# Copyrights
geacron_copyright = Map Polygons Source: Provided by <a href=\"http://www.geacron.com\">Geacron</a>
gecron_shortcopyright = Shapes (C) Geacron
cshapes_copyright = Map Polygons Source: Weidmann, Nils B., Doreen Kuse, and Kristian Skrede Gleditsch. 2010.<br> The Geography of the International System: <a href=\"http://nils.weidmann.ws/projects/cshapes.html\">The CShapes Dataset. International Interactions 36 (1)</a>
cshapes_shortcopyright = Shapes (C) CShapes
```
