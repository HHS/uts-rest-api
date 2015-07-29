#!/usr/bin/perl
use lib ".";
use strict;
use warnings;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;

##create a ticket granting ticket for the session
my $ticketClient = new TicketClient(username=>"your-umls-username",password=>"your-umls-password",service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my %params = ();
my $client = REST::Client->new();
open CUIS, "sample-cuis.txt" || die "Could not open sample file$!";

  while(<CUIS>) {
  	my $cui = $_;
  	chomp($cui);  	
  	my $path = "/rest/content/current/CUI/".$cui;
  	my $json = run_query($path,%params);
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
	
	#TODO - add in handling for 404s once they are returned properly.
	my ($path, %params) = @_;
	$params{ticket} = $ticketClient->getServiceTicket();
	$uri->path($path);
	$uri->query_form(\%params);
	#print qq{$uri\n};
	my $query = $client->GET($uri);
	my $results = $query->responseCode() eq '200'? $query->responseContent: "Not Found";
	my $json = format_json($results) unless $results eq "Not Found";
	return $json unless $results eq "Not Found";
}

