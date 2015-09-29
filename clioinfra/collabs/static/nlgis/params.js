var myurl=window.location.toString();
var uri = '';
var year;
var mapyear = 2012;
var catmax = 6;
myurl = myurl + '&'
var colors = '';

if (myurl.indexOf("start=") > 0) {
    handle=myurl.substring(myurl.indexOf("start=")+8);
    cindex=myurl.indexOf("&");
    if (cindex > 0) {
      uri=handle.substring(0,cindex);
    };
};

if (myurl.indexOf("dataset=") > 0) {
    handlestr=myurl.substring(myurl.indexOf("dataset=")+8);
    cindex=handlestr.indexOf("&");
    if (cindex > 0) {
      handle=handlestr.substring(0,cindex);
    };
};

if (myurl.indexOf("&year=") > 0) {
    yearstr=myurl.substring(myurl.indexOf("year=")+5);
    cindex=yearstr.indexOf("&");
    if (cindex > 0) {
      year=yearstr.substring(0,cindex);
    };
};

if (typeof(year) == 'undefined') 
{
       if (myurl.indexOf("&lasty=") > 0) {
        yearstr=myurl.substring(myurl.indexOf("lasty=")+6);
        cindex=yearstr.indexOf("&");
    	if (cindex > 0) {
      	year=yearstr.substring(0,cindex);
        };
       };
};

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
