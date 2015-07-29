#!/usr/bin/perl

##usage: perl retrieve-concept-info.pl -u your-umls-username -p your-umls-password
##This file runs some searches on a list of UMLS CUIs and then prints out some basic information.
##The full list of fields available for CUI retrieval is at https://documentation.uts.nlm.nih.gov/rest/search/index.html#sample-output

use lib ".";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p);
getopt('up');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my %parameters = ();
my $client = REST::Client->new();

open CUIS, "sample-cuis.txt" || die "Could not open sample file$!";

  while(<CUIS>) {
  	my $cui = $_;
  	chomp($cui);  	
  	my $path = "/rest/content/current/CUI/".$cui;
  	my $json = run_query($path,\%parameters);
    my $ui = $json->{result}{ui};
    my $name = $json->{result}{name} ;
    my @stys = @{ $json->{result}{semanticTypes} };
    print qq{$ui|$name|@stys\n};
    my $atoms = $json->{result}{atoms};
    my $definitions = $json->{result}{definitions}; 
    print qq{  atoms:$atoms\n};
    ##Not all CUIs have definitions - if there are none the API returns "definitions:"NONE" in the JSON data.
    print qq{  definitions:$definitions\n};
  }
  
  
sub format_json {
	my $json_in = shift;
	my $json = JSON->new;
	my $obj = $json->decode($json_in);
	#print Dumper(\$obj);
	return $obj;
}

sub run_query {
	
	my ($path, $parameters) = @_;	
	$parameters{ticket} = $ticketClient->getServiceTicket();
	$uri->path($path);
	$uri->query_form($parameters);
	#print qq{$uri\n};
	my $query = $client->GET($uri) || die "could not execute query";
	my $results = $query->responseCode() eq '200'? $query->responseContent: "Not Found";
	my $json = format_json($results) unless $results eq "Not Found";
	return $json unless $results eq "Not Found";
}

