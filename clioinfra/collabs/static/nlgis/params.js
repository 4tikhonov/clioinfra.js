var myurl=window.location.toString();
var uri = '';
var year;
var mapyear = 2012;
var catmax = 6;
var ctrlist = '';
var lastyear;
var logscale = '';
myurl = myurl + '&'
var colors = '';
var histo = '';
var copyrights_cshapes = '<a href="http://nils.weidmann.ws/projects/cshapes.html">Borders (C) CShapes</a>';
var copyrights_geacron = '<a href="http://www.geacron.com">Borders (C) Geacron</a>';
var copyrights = copyrights_cshapes;

if (myurl.indexOf("start=") > 0) {
    handle=myurl.substring(myurl.indexOf("start=")+8);
    cindex=myurl.indexOf("&");
    if (cindex > 0) {
      uri=handle.substring(0,cindex);
      uri = handle.substring(2,myurl.length);
    };
};

if (myurl.indexOf("histo=") > 0) {
    histostr=myurl.substring(myurl.indexOf("histo=")+6);
    cindex=histostr.indexOf("&");
    if (cindex > 0) {
      histo=histostr.substring(0,cindex);
    };
};

if (myurl.indexOf("hist=") > 0) {
    histostr=myurl.substring(myurl.indexOf("hist=")+5);
    cindex=histostr.indexOf("&");
    if (cindex > 0) {
      histo=histostr.substring(0,cindex);
    };
};

if (myurl.indexOf("dataset=") > 0) {
    handlestr=myurl.substring(myurl.indexOf("dataset=")+8);
    cindex=handlestr.indexOf("&");
    if (cindex > 0) {
      handle=handlestr.substring(0,cindex);
    };
};

if (myurl.indexOf("handle=") > 0) {
    handlestr=myurl.substring(myurl.indexOf("handle=")+7);
    cindex=handlestr.indexOf("&");
    if (cindex > 0) {
      handle=handlestr.substring(0,cindex);
    };
};

if (myurl.indexOf("ctrlist=") > 0) {
    ctrstr=myurl.substring(myurl.indexOf("ctrlist=")+8);
    cindex=ctrstr.indexOf("&");
    if (cindex > 0) {
      ctrlist=ctrstr.substring(0,cindex);
    };
};

if (myurl.indexOf("&year=") > 0) {
    yearstr=myurl.substring(myurl.indexOf("year=")+5);
    cindex=yearstr.indexOf("&");
    if (cindex > 0) {
      year=yearstr.substring(0,cindex);
    };
};

if (myurl.indexOf("&lasty=") > 0) {
    yearstr=myurl.substring(myurl.indexOf("lasty=")+6);
    cindex=yearstr.indexOf("&");
    if (cindex > 0) {
      	lastyear=yearstr.substring(0,cindex);
    };
};

if (myurl.indexOf("&logscale=") > 0) {
    logstr=myurl.substring(myurl.indexOf("logscale=")+9);
    cindex=yearstr.indexOf("&");
    if (cindex > 0) {
        logscale=logstr.substring(0,cindex);
    };
};


if (typeof(year) == 'undefined')
{
   year = lastyear;
}
if (year == 'undefined')
{
   year = lastyear;
}

if (myurl.indexOf("colors=") > 0) {
    cstr=myurl.substring(myurl.indexOf("colors=")+7);
    cindex=cstr.indexOf("&");
    if (cindex > 0) {
      colors=cstr.substring(0,cindex);
    };
};

if (myurl.indexOf("catmax=") > 0) {
    catstr=myurl.substring(myurl.indexOf("catmax=")+7);
    cindex=catstr.indexOf("&");
    if (cindex > 0) {
      catmax=catstr.substring(0,cindex);
    };
};

if (histo.length > 0)
{
    if (parseInt(year) < 1946)
    {
	copyrights = copyrights_geacron;
    }
}
