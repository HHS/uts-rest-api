#!/usr/bin/perl

##usage: perl search-terms.pl -u your-umls-username -p your-umls-password -v version -s string
##If you do not provide the version parameter the script queries the latest avaialble UMLS publication.
##Use quotes if your search string has spaces, for example perl search-terms.pl -u username -p password -s "diabetic foot"
##This file searches the UMLS against a string you provide returns CUIs (by default) or source-asserted identifers.
##The full list of fields available for search results is at https://documentation.uts.nlm.nih.gov/rest/search/index.html

use lib "lib";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p,$opt_v,$opt_s);
getopt('upvs');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $version = defined $opt_v ? $opt_v : "current";
my $string = $opt_s || die "please provide a query string";
my $resultCount = 0;

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my $json;
my $client = REST::Client->new();
my %parameters = ();

  	my $pageNum = "1";
  	my $path = "/rest/search/".$version;
  	$parameters{string} = $string;
        #$parameters{searchType} = "exact";
  	##optional parameters to return source-asserted identifiers and filter by source.  You can also use 'sourceConcept' (for SNOMEDCT_US, LNC, NCI,RXNORM) or 'sourceDescriptor' (for MSH,MDR,ICD9CM,ICD10CM,GO)
  	#$parameters{returnIdType} = "code";
  	$parameters{sabs} = "SNOMEDCT_US";
  	
  	print qq{Searching term $string\n};
  	#many term searches will return more than the default page size, which is 25 json objects, so we page through them here.
  	do {
  		$parameters{pageNumber} = $pageNum;
                #$parameters{pageSize} = "10";
                print qq{Page $pageNum Results\n};
  		$json = run_query($path,\%parameters);
  		foreach my $result(@{ $json->{result}{results} }) {
                  
  		printf "%s\n","uri: ".$result->{uri} if defined $result->{uri};
                printf "%s\n","ui: ".$result->{ui} if $result->{ui} ne 'NONE';
                printf "%s\n","name: ".$result->{name} if $result->{name} ne 'NO RESULTS';
                printf "%s\n","Source Vocabulary: ".$result->{rootSource} if defined $result->{rootSource};
                print qq{\n};
  		}
                print qq{----------\n};
  		$pageNum++;
                $resultCount+= scalar(@{ $json->{result}{results} });

  	}

  	##TODO: Add 'next' and 'previous' page URIs to JSON output so we don't have to do this:.
  	while $json->{result}{results}[0]{name} ne 'NO RESULTS';
        ### paging is not fully implemented under the /search endpoint, so we have to discount the one 'NO RESULTS' result.
        $resultCount--;
        print qq{Found $resultCount results\n};


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
	print qq{$uri\n\n};
	my $query = $client->GET($uri) || die "Could not execute query $!\n";
	my $results = $query->responseCode() eq '200'? $query->responseContent: die "Could not execute query $!\n";
	my $json = format_json($results);
	return $json;
}

