#!/usr/bin/perl

use vars qw/$libpath/;
use FindBin qw($Bin);
BEGIN { $libpath="$Bin" };
use lib "$libpath";
use lib "$libpath/../libs";
use JSON qw( decode_json );
use Try::Tiny;

$dataset = $ARGV[0];
$DEBUG = $ARGV[1];
my %dbconfig = loadconfig("$Bin/../config/clioinfra.conf");
$dvroot = $dbconfig{'dataverseroot'};
$dataverse = $dbconfig{'branch'};
$key = $dbconfig{'key'};

$path = $dbconfig{'path'};
$root = $dvroot."/dataset.xhtml?persistentId=";

if ($dataset=~/^(\S+)\/(\S+)\:(\d+)\:(\d+)$/)
{
   my ($handle, $uID, $dataset, $id) = ($1, $2, $3, $4);
   $datasethandle = "$uID"."$dataset"."_"."$id";
   $datasetfilename = "$path/$uID"."$dataset"."_"."$id".".csv";
   # Get file info
   $metadatajson = `/usr/bin/wget -q \"$dvroot/api/datasets/$dataset/versions/1.0?key=$key&show_entity_ids=true&q=authorName:*\" --no-check-certificate -O -`;

   print "$metadatajson\n\n" if ($DEBUG);

   if ($DEBUG1)
   {
	$metadata = decode_json( $metadatajson );
        %meta = %{$metadata};
        %metadata = %{$meta{data}{metadataBlocks}{citation}};
	@fields = @{$metadata{fields}};
	foreach $item (@fields)
	{
	    my %info = %{$item};
	    foreach $i (keys %info)
	    {
		print "X $i $info{$i}\n" if ($DEBUG);
	        $title = $info{$i} if ($i=~/value/i && !$title);
	    }
	}
   }

   if ($metadatajson=~/\"id\"\:$id,\"name\"\:\"(.+?)\"/)
   {
	$filename = $1;
	if ($filename=~/(.+)\.(\w+)$/)
	{
	    $ext = $1;
	}
   }

   # Get file
   $ext="csv" unless ($ext);
   $datasetfile = "$id.$ext";
   $file = `/usr/bin/wget -q \"$dvroot/api/access/datafile/$id?key=$key&show_entity_ids=true&q=authorName:*\" -O $path/$id --no-check-certificate`;
   print "<a href=\"$root$handle\" target=_blank>$title</a><br>\ndataset file: $filename\n$file\n";
   print "<br><a href=\"/collabs/export?fileID=$datasethandle\">Export to CSV</a><br>\n";
   print "Dataset: $path/$id\n";

   if (-e "$path/$id" && $filename=~/xlsx/)
   {
	# Clio infra
	$outfile = "$path/$id.csv";
	$outfile = $datasetfilename if ($datasetfilename);
	$convert = `$Bin/xlsx2csv.py $path/$id`;
	if ($convert=~/\S+/)
	{
	    open(file, ">$outfile");
	    print file "$convert";
	    close(file);
	}
	else
	{
            $convert = `$Bin/../modules/xlsx2csv.py -s '4' $path/$id > $outfile`;
	}
   }
   elsif (-e "$path/$id" && $filename=~/xls$/)
   {
 	$outfile = "$path/$id.csv";
	$outfile = $datasetfilename if ($datasetfilename);
        $convert = `/usr/bin/xls2csv -c '|' $path/$id > $outfile`; 
	print "convert $outfile\n" if ($DEBUG);
   }

   if (-e "$outfile")
   {
	#$convert = `$Bin/clio2data.pl --csvfile=$outfile`;
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

