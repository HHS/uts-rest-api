#!/usr/bin/perl

## This file retrieves basic information of a source-asserted identifer or UMLS CUI.
## usage: perl retrieve-concept-info.pl -u your-umls-username -p your-umls-password -v version -i identifer -s source vocabulary
## If you do not provide the version parameter the script queries the latest avaialble UMLS publication.
## To query the UMLS, omit the 'source' parameter and use UMLS CUI as your 'identifier' parameter.
## The full list of query parameters and fields available for CUI retrieval is at https://documentation.uts.nlm.nih.gov/rest/concept/index.html and
## https://documentation.uts.nlm.nih.gov/rest/source-asserted-identifiers/index.html

use lib ".";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p,$opt_v,$opt_s, $opt_i);
getopt('upvsi');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $version = defined $opt_v ? $opt_v : "current";
my $source = $opt_s;
my $id = $opt_i || die "please provide a UMLS CUI or source-asserted identifier";

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my %parameters = ();
my $client = REST::Client->new();


    my $path = defined $source ? "/rest/content/".$version."/source/".$source."/".$id : "/rest/content/".$version."/CUI/".$id;
    my $json = run_query($path,\%parameters);
    printf "%s\n","Ui: ".$json->{result}{ui};
    printf "%s\n","Name: ".$json->{result}{name};
    ##Semantic Types are only assigned to UMLS CUIs, not codes or concepts from other sources.
    printf "%s\n", "Semantic Type(s): ".join(",", @{ $json->{result}{semanticTypes} }) if  $json->{result}{semanticTypes};
    printf "%s\n","Atom Count: ".$json->{result}{atomCount};
    printf "%s\n","Atoms: ".$json->{result}{atoms};
    printf "%s\n","Definitions: ".$json->{result}{definitions} if defined $json->{result}{definitions};
    ##source-asserted data may have parents and children
    printf "%s\n","Parents: ".$json->{result}{parents} if defined $json->{result}{parents};
    printf "%s\n","Children: ".$json->{result}{children} if defined $json->{result}{children};
    

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
