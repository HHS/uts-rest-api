#!/usr/bin/perl

## Compatible with UTS REST API - version 0.51 Beta
## This file retrieves allows you to retrieve parents, children, ancestors, or descendants of a source-asserted concept, descriptor, or code.
## usage: perl retrieve-concept-info.pl -u your-umls-username -p your-umls-password -v version -i identifer -s source vocabulary
## If you do not provide the version parameter the script queries the latest avaialble UMLS publication.
## The full list of query parameters and fields available for source-asserted data retrieval is at:
## https://documentation.uts.nlm.nih.gov/rest/source-asserted-identifiers/index.html

use lib "lib";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p,$opt_v,$opt_s, $opt_i,$opt_o);
getopt('upvsio');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $version = defined $opt_v ? $opt_v : "current";
my $source = $opt_s || die "please provide a source vocabulary, such as SNOMEDCT_US";
my $id = $opt_i || die "please provide a source-asserted identifier";
my $operation = $opt_o || die "please specify 'children', 'ancestors', 'descendants', or 'parents'";
my $json;
my $pageNum = 1;
my $pageCount;
my $resultCount = 0;

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my %parameters = ();
my $client = REST::Client->new();

my $path =  "/rest/content/".$version."/source/".$source."/".$id."/".$operation;


    do {
    
    $parameters{pageNumber} = $pageNum;
    $json = run_query($path,\%parameters);
    $pageCount = $json->{pageCount};
    print qq{On page $pageNum of $pageCount pages\n};
    
    foreach my $ui (@{ $json->{result} }) {
	
      printf "%s\n","ui- ".$ui->{ui};
      printf "%s\n","Name- ".$ui->{name};
      printf "%s\n","Atoms- ".$ui->{atoms};
      printf "%s\n","Highest Ranking Atom- ".$ui->{defaultPreferredAtom};
      printf "%s\n","Parents - ".$ui->{parents};
      printf "%s\n","Children- ".$ui->{children};
      printf "%s\n","Ancestors- ".$ui->{ancestors};
      printf "%s\n","Descendants- ".$ui->{descendants};
      printf "%s\n","Obsolete- ".$ui->{obsolete};
      print qq{\n};
      
      }
    
    print qq{-------\n};
    $pageNum++;
    $resultCount += scalar(@{$json->{result}});
    }
    
    while ($pageNum < ($pageCount + 1));
    print qq{Found $resultCount total results\n};
   

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
	print qq{$uri\n};
	my $query = $client->GET($uri) || die "Could not execute query$!";
	my $results = $query->responseCode() eq '200'? $query->responseContent: die "Could not execute query$!";
	my $json = format_json($results);
	return $json;
}
