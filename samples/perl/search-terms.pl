#!/usr/bin/perl

##usage: perl search-terms.pl -u your-umls-username -p your-umls-password
##If you do not provide the version parameter the script queries the latest avaialble UMLS publication.
##This file runs some searches on a list of terms and then prints out some basic information.
##The full list of fields available for search results is at https://documentation.uts.nlm.nih.gov/rest/search/index.html

use lib ".";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p,$opt_v);
getopt('upv');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $version = defined $opt_v ? $opt_v : "current";

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my $json;
my $client = REST::Client->new();
my %parameters = ();
open TERMS, "sample-terms.txt" || die "Could not open sample file$!";

  while(<TERMS>) {
  	my $term = $_;
  	chomp($term);
  	my $pageNum = "1";
  	my $path = "/rest/search/".$version;
  	
  	$parameters{string} = $term;
  	##optional parameters to return source-asserted identifiers and filter by source.  You can also use 'sourceConcept' (for SNOMEDCT_US, LNC, NCI,RXNORM) or 'sourceDescriptor' (for MSH,MDR,ICD9CM,ICD10CM,GO)
  	#$parameters{returnIdType} = "code";
  	#$parameters{sabs} = "SNOMEDCT_US,ICD10CM";
  	#$parameters{returnIdType} = "aui";
  	
  	print qq{Searching term $term\n};
  	
  	do {
  		#many term searches will return more than the default page size, which is 25 json objects.
  		$parameters{page} = $pageNum;
  		$json = run_query($path,\%parameters);
  		foreach my $result(@{ $json->{result}{results} }) {
  		print qq{ $result->{ui}|$result->{uri}|$result->{rootSource}|$result->{name}\n } if $result->{name} ne 'NO RESULTS';
  			
  		}
  		$pageNum++;

  	}
  	
  	##TODO: Add 'next' and 'previous' page URIs to JSON output so we don't have to do this:.
  	while $json->{result}{results}[0]{name} ne 'NO RESULTS';
  	
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

