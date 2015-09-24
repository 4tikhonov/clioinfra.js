#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../libs";

$root = "http://collab.iisg.nl/web";
$collab = $ARGV[0];
$action = $ARGV[1];
$base = $ARGV[2];
$collab = "labourconflicts" unless ($collab);
$collab=~s/\/$//g;
#$collab = "labourconflicts/datafiles";
$remove = "\/web\/";

$url = "$root/$collab/";
$templatedir = "$Bin/templates";
$liferay = "$Bin/templates/lifeclear.html";
$liferay = "$Bin/templates/liferay.html";

if ($base eq 'iisg')
{
   $url = "http://www.iisg.nl/$collab/";
   $baseurl = $url;
   if ($collab=~/^(\S+?)\//)
   {
	$baseurl = $1;
   }

   if ($collab=~/^(\S+)\/(\S+\.\w+)$/)
   {
	($baseurl, $baseuri) = ($1, $2);
	$baseurl = "http://www.iisg.nl/$1";
   }
}
if ($base eq 'liferay')
{
   $content = readfile($liferay);
   print "$content\n";
   exit(0);
}
if ($collab eq 'frontpage')
{
   $content = readfile("$templatedir/frontpage.html");
   print "$content\n";
   exit(0);
}

$html = `/usr/bin/wget -q \"$url\" -O -`;
#$action = "menu";
$action = "content" unless ($action);

if ($action eq 'menu')
{
   if ($html=~/<ul\s+id\=\"main\-menu\">(.+?)<\/ul>/sxi)
   {
        $menuhtml = $1;
        #print "$menuhtml\n";
        my @li = split(/<li\s+.+?>\s*/sxi, $menuhtml);
        foreach $item (@li)
        {
            if ($item=~/<a.+?href\=\"(\S+)\".*>(.+?)<\/a>/sxi)
            {
                my ($url, $title) = ($1, $2);
                $title=~s/<\S+>//g;
                $url=~s/\;jsession\S+//g;
                $url=~s/^\S+?$remove//g;
                print "$url $title\n";
            }
        }
   }
}
if ($action eq 'content')
{
   if ($html=~/<div\s+class\=\"journal-content-article\".+?>(.+?)<\/div><\/div>/sxi)
   {
	$content = $1;
	$content=~s/\=\"http\S+?collab\.iisg\S+?\//\=\"\//g;
	$content=~s/\=\"$remove/\=\"\/collabs\/?project\=/g;
   }
   if ($html=~/div\s+id\="companyname\">(.+?)<\/div><\/div>/)
   {
	$title = $1;
   }

   if ($html=~/<h2>(.+?)<\/h2>/sxi)
   {
	$title = $1;
   }
   if ($html=~/<\/h2>(.+?)<div\s+class\=\"nav\s+footer\">/sxi)
   {
	$content = $1;
	$content=~s/<\!\-\-.+?\-\->//gxi;
	if ($content=~/^(.{32766})/sxi)
	{
	    $content = $1;
	}
	@strings = split(/\r\n/, $content);
	foreach $item (@strings)
	{
	    if ($item=~/\=\"(.+?)\"/)
	    {
		$uri = $1;
		if ($uri=~/(\w+\.php)/)
		{
		    $new = "/collabs/?project=$collab/$1&base=$base";	    
		    $item=~s/$uri/$new/g;
		}
		elsif ($uri!~/http/sxi && $uri=~/(\S+\.\w{3})/)
		{
		    $new = "$baseurl/$1";	
		    $item=~s/$uri/$new/g;
		}
	    }
	}

	$newcontent = "@strings";
	if ($newcontent)
	{
	   $content = $newcontent;	
	}
   }

   $content=~s/\r//g;
   print "<h1 class=\"title\" id=\"page-title\">$title</h1>$content\n";
}

sub readfile
{
   my ($filename, $DEBUG) = @_;
   open(file, "$filename");
   @content = <file>;
   close(file);
   $content = "@content";
   return $content;
}
