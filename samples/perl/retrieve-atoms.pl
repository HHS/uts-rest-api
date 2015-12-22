#!/usr/bin/perl

## Compatible with UMLS REST API - version 0.51 Beta
## usage: perl retrieve-atoms.pl -u your-umls-username -p your-umls-password -v version (optional) -i identifier -s source_vocabulary(optional)
## If you do not provide the version parameter the script queries the latest avaialble UMLS publication.
## This file takes a CUI or a source asserted identifier and retrieves atoms according to your query parameters.
## Use the -s flag to specify (optionally) a UMLS source vocabulary.  If you omit this flag the script expects that your -i (identifier) argument will be
## populated with a UMLS CUI.
## The full list of fields available for search results is at https://documentation.uts.nlm.nih.gov/rest/atoms/index.html

use lib "lib";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;
our ($opt_u,$opt_p,$opt_v,$opt_i,$opt_s);
getopt('upvsi');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $version = defined $opt_v ? $opt_v : "current";
my $source = $opt_s;
my $id = $opt_i || die "please provide an identifier";

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my $json;
my $client = REST::Client->new();
my $pageNum = 1;
my $pageCount;
my $resultCount = 0;
my %parameters = ();
my $obj;
my $path = defined $source ? "/rest/content/".$version."/source/".$source."/".$id."/atoms": "/rest/content/".$version."/CUI/".$id."/atoms" ;
my $result;

        ## with /atoms you may get more than the default 25 objects per page.  You can either set your paging to higher values or page through results
	## as in this example.	
	do {
	
	 $parameters{pageNumber} = $pageNum;
	 #$parameters{sabs} = "SNOMEDCT_US";
	 $parameters{language} = "ENG";
	 ##suppressible/obsolete atoms are excluded by default
	 #$parameters{includeSuppressible} = "true";
	 #$parameters{includeObsolete} = "true";
	 #$parameters{ttys} = "PT";
         $json = run_query($path,\%parameters);
	 $pageCount = $json->{pageCount};
	 print qq{On page $pageCount of $pageNum pages\n};
	 
  	    foreach my $atom(@{ $json->{result} }) {
	    
	    
	    printf "%s\n","AUI: ".$atom->{ui};
  	    printf "%s\n","Atom Name: ".$atom->{name};
	    printf "%s\n","Language: ".$atom->{language};
	    printf "%s\n","Term Type: ".$atom->{termType};
	    printf "%s\n","Obsolete: ".$atom->{obsolete};
	    printf "%s\n","Suppressible: ".$atom->{suppressible};
	    printf "%s\n", "Source: ".$atom->{rootSource};
	    printf "%s\n", "CUI: " .$atom->{memberships}->{concept};
	    ## The {memberships} wrapper returned by the /atoms endpoint contains information about to which source concept,code,or source descriptor the atom belongs
	    ## not all vocabularies have source descriptors or source concepts, so we make sure they exist.
	    printf "%s\n", "Source Concept: " .$atom->{memberships}->{sourceConcept} if defined $atom->{memberships}->{sourceConcept};
	    printf "%s\n", "Source Descriptor: " .$atom->{memberships}->{sourceDescriptor} if defined $atom->{memberships}->{sourceDescriptor};
	    printf "%s\n", "Code: " .$atom->{memberships}->{code} if defined $atom->{memberships}->{code};	     
	    print qq{\n};
	    
  	    }
	print qq{-------\n};
	$pageNum++;
	$resultCount += scalar((@{ $json->{result} }));
	}
	##page all the way through until the end.
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
	print qq{$uri\n\n};
	my $query = $client->GET($uri) || die "Could not execute query$!";
	my $results = $query->responseCode() eq '200'? $query->responseContent: die "Could not execute query$!";
	my $json = format_json($results);
	return $json;
}

