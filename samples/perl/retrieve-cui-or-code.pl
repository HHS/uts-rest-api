#!/usr/bin/perl

## Compatible with UMLS REST API - version 0.60 Beta
## This file retrieves basic information of a source-asserted identifer or UMLS CUI.
## usage: perl retrieve-concept-info.pl -u your-umls-username -p your-umls-password -v version -i identifer -s source vocabulary
## If you do not provide the version parameter the script queries the latest avaialble UMLS publication.
## To query the UMLS, omit the 'source' parameter and use UMLS CUI as your 'identifier' parameter.
## The full list of query parameters and fields available for CUI retrieval is at:
## https://documentation.uts.nlm.nih.gov/rest/concept/index.html and
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
our ($opt_u,$opt_p,$opt_v,$opt_s, $opt_i);
getopt('upvsi');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $id = $opt_i || die "please provide a UMLS CUI or source-asserted identifier";
my $version = defined $opt_v ? $opt_v : "current";
my $source = $opt_s;


##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my %parameters = ();
my $client = REST::Client->new();


    my $path = defined $source ? "/rest/content/".$version."/source/".$source."/".$id : "/rest/content/".$version."/CUI/".$id;
    my $json = run_query($path,\%parameters);
    my $cuiOrCode = $json->{result};

    printf "%s\n","ui- ".$cuiOrCode->{ui};
    printf "%s\n","Number of Atoms- ".$cuiOrCode->{atomCount};
    printf "%s\n","Name- ".$cuiOrCode->{name};
    printf "%s\n","Atoms- ".$cuiOrCode->{atoms};
    printf "%s\n","Definitions- ".$cuiOrCode->{definitions};
    printf "%s\n","Relations- ".$cuiOrCode->{relations};
    printf "%s\n","Highest Ranking Atom- ".$cuiOrCode->{defaultPreferredAtom};
    my $stys = $cuiOrCode->{semanticTypes};
    
    ## Semantic Types are only assigned to UMLS CUIs. There are often more than one semantic type per CUI.
    if (!defined $source) {
       
       printf "%s\n", "Semantic Types:";
       foreach my $sty (@{ $stys }) {
	  printf "%s\n", "uri: ".$sty->{uri};
	  printf "%s\n", "name: ".$sty->{name};
	
        }
    }  
    ##source-asserted data. UMLS CUIs do not have transitive relations.
    printf "%s\n","Parents- ".$cuiOrCode->{parents} if defined $source;
    printf "%s\n","Children- ".$cuiOrCode->{children} if defined $source;
    printf "%s\n","Ancestors- ".$cuiOrCode->{ancestors} if defined $source;
    printf "%s\n","Descendants- ".$cuiOrCode->{descendants} if defined $source;
    
   

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
