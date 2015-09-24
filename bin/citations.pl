#!/usr/bin/perl

use JSON;
use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../libs";

my %dbconfig = loadconfig("$Bin/../config/clioinfra.conf");
$root = $dbconfig{'dataverseroot'};
$dataverse = $dbconfig{'branch'};
$key = $dbconfig{'key'};

$url = "curl -s -k -u '$key:' $root/dvn/api/data-deposit/v1.1/swordv2/collection/dataverse/$dataverse";
$content = `$url`;
$j = new JSON;
my @handles = split(/<id>/sxi, $content);
foreach $idstr (@handles)
{
   if ($idstr=~/(hdl\:\d+\/\S+?)\"/)
   {
	$handle = $1;
	$url = "$root/dataset.xhtml?persistentId=$handle";
	$handles{$handle} = $url;
   };
}

sub getcitation
{
#     <div id="panelCollapse0" class="collapse in">\s*<div class="panel-body">
}

foreach $handle (sort keys %handles)
{
    my %attr;
    $handleurl = $handles{$handle};
    $attr{$handleurl}{'handleurl'} = $handleurl;
    $attr{$handleurl}{'handle'} = $handle;

    $content = `/usr/bin/wget -q \"$handleurl\" -O - --no-check-certificate`;
    my ($title, $dataset);
    if ($content=~/<span\s+class\=\"breadcrumbActive\">(.+?)<\/span>/sxi)
    {
	$title = $1;
    }

    if ($content=~/<\!\-\-\s+WorldMap\s+Preview\s+\-\->.+?bold\;\">(.+?)<\/span>/sxi)
    {
	$dataset = $1;
    }

    if ($content)
    {
        #print "<p><a href=\"$handles{$handle}\">$title</a></p>\n";
    }
    # <div class="form-group" id="description">
    if ($content=~/<div\s+class\=\"form\-group\"\s+id\=\"description\">(.+?)<\!\-\-\s+END\s+View\s+editMode\s+\-\-\>/sxi)
    {
        $info = $1;
        while ($info=~s/class\=\"col\-sm\-3\s+control\-label\">(.+?)<div\s+class\=\"col\-sm\-9\s+no\-padding\-left\-right">(.+?)<\/div>//sxi)
        {
            my ($item, $value) = ($1, $2);
            if ($item=~/.+>(.+?)</)
            {
                $var = $1;
                $attr{$handleurl}{$var} = $value;
            }
        };
	push(@ranks, $attr{$handleurl});
    }

    
    foreach $url (sort keys %attr)
    {
	%info = %{$attr{$url}};
	
	my $json = encode_json \%info;
	print $json;
    }

}

sub loadconfig
{
    my ($configfile, $DEBUG) = @_;
    my %config;

    open(conf, $configfile);
    while (<conf>)
    {
        my $str = $_;
        $str=~s/\r|\n//g;
        my ($name, $value) = split(/\s*\=\s*/, $str);
        $config{$name} = $value;
    }
    close(conf);

    return %config;
}

