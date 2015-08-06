#!/usr/bin/perl

##usage: perl search-terms.pl -u your-umls-username -p your-umls-password
##This file runs some searches on a list of UMLS CUIs and then prints out some basic information.
##The full list of fields available for search results is at https://documentation.uts.nlm.nih.gov/rest/concept/index.html#sample-output

use lib ".";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use JSON::Parse 'valid_json';
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p,$opt_v,$opt_c);
getopt('upvc');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $version = $opt_v || die "please provide a UMLS Version";
my $cui = $opt_c || die "please provide an identifier";

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my $json;
my $client = REST::Client->new();
my $pageNum = "1";
my %parameters = ();
my $obj;
my $path = "/rest/content/current/CUI/".$cui."/atoms";
my $result;

        ## with /atoms you may get more than the default 25 objects per page.  You can either set your paging to higher values or page through results
	## as in this example.
	##TODO: Add support for retrieving atoms from source-asserted identifiers.
	
	do {
	
	 ##Full documentation on query parameters and output is available at https://documentation.uts.nlm.nih.gov/rest/atoms/index.html
	 $parameters{page} = $pageNum;
	 #$parameters{sabs} = "SNOMEDCT_US,ICD10CM";
	 $parameters{language} = "ENG";
	 ##suppressible atoms are excluded by default
	 #$parameters{includeSuppressible} = "true";
         $json = run_query($path,\%parameters);
	 
  	    foreach my $result(@{ $json->{result} }) {
  	    printf "%s\n","Atom Name: ".$result->{name};
	    printf "%s %s|%s\n","Term Type: ".$result->{termType}, "(obsolete) - ".$result->{obsolete}, "(suppressible) - ".$result->{suppressible};
	    printf "%s\n", "Source: ".$result->{rootSource};
	    printf "%s\n", "AUI: ".$result->{ui},"Term Type:" .$result->{termType};
	    printf "%s\n", "CUI: ".$result->{memberships}{concept};
	    printf "%s\n", "Code: ".$result->{memberships}{code};
	    ## not all vocabularies have source descriptors or source concepts, so we make sure they exist.
	    printf "%s\n", "Source Descriptor: ".$result->{memberships}{sourceDescriptor} if defined $result->{memberships}{sourceDescriptor} ;
	    printf "%s\n", "Source Concept: ".$result->{memberships}{sourceConcept} if defined $result->{memberships}{sourceConcept} ;
	    print qq{-------\n};
  	    }
	$pageNum++;
	}
	##make sure our result set is not empty
	while (scalar keys $json->{result} > 0 );
  	  	

sub format_json {
	my $json_in = shift;
	my $json = JSON->new;
	my $obj = $json->decode($json_in) if scalar $json_in;
	#print Dumper(\$obj);
	return $obj;
}

sub run_query {
	
	my ($path, $parameters) = @_;	
	$parameters{ticket} = $ticketClient->getServiceTicket();
	$uri->path($path);
	$uri->query_form($parameters);
	#print qq{$uri\n};
	my $query = $client->GET($uri) || die "Could not execute query$!";
	my $results = $query->responseCode() eq '200'? $query->responseContent: die "Could not execute query$!";
	my $json = format_json($results);
	return $json;
}

