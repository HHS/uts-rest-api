#!/usr/bin/perl -w

## usage: perl crosswalk.pl -u your-umls-username -p your-umls-password -v source vocabulary -t source vocabulary term [ -r specify target covabulary]
## Performs a crosswalk using the latest UMLS version and retrieves all codes that share a UMLS CUI with a particular code.
## Examplee: 
## perl crosswalk.pl -u username -p password -v HPO -t HP:0001947
## perl crosswalk.pl -u username -p password -v HPO -t HP:0001947 -r SNOMEDCT_US
## More information: https://documentation.uts.nlm.nih.gov/rest/source-asserted-identifiers/crosswalk/index.html

use lib "lib";
use strict;
use URI;
use Authentication::TicketClient;
use JSON;
use REST::Client;
use Data::Dumper;
use Getopt::Std;

## parse command line arguments
our ($opt_u,$opt_p,$opt_v,$opt_t, $opt_r);
getopt('upvtr');
my $username = $opt_u || die "please provide username";
my $password = $opt_p || die "please provide password";
my $source   = $opt_v || die "Please provide a source vocabulary";
my $term     = $opt_t || die "Please provide a source vocabulary term";

## Create a ticket granting ticket for the session
my $ticketClient = 
  new TicketClient(username=>$opt_u,password=>$opt_p,service=>"http://umlsks.nlm.nih.gov",tgt=>"") || die "could not create TicketClient() object";
my $tgt = $ticketClient->getTgt();
my $uri = new URI("https://uts-ws.nlm.nih.gov");
my $json;
my $client = REST::Client->new();
my %parameters = ();

my $path = sprintf("/rest/crosswalk/current/source/%s/%s", $opt_v, $opt_t);

if ( defined $opt_r && $opt_r ){
  $parameters{'targetSource'} = $opt_r
}

## Query the API
$json = run_query($path,\%parameters);
my $ra_results = $json->{'result'};

## Loop through results
foreach my $result( @$ra_results ) {
  printf("%s %s %s\n", $result->{'rootSource'}, $result->{'ui'}, $result->{'name'} )
}


sub format_json {
  my $json_in = shift;
  my $json    = JSON->new;
  my $obj     = $json->decode($json_in);
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

