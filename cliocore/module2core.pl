#!/usr/bin/perl

while (<>)
{
    my $str = $_;
    if ($str=~/(import\s+|\/python)/sxi)
    {
	print "$str";
    }
    elsif ($str=~/\S+/sxi)
    {
	print "    $str";
    }
    else
    {
	print "$str"
    }
    
}
