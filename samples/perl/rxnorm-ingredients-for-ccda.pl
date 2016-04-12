##4/12/2016: Steve Emrick - steve.emrick@nih.gov
##Perl script to retrieve RxNorm IN,MIN,PIN,and BN atoms for C-CDA value sets.
##Run the script as follows: perl rxnorm-ingredients-for-ccda.pl my-rxcuis.txt
##Should be run each month when RxNorm is updated - usually the first Monday of the month

use strict;
use warnings;
use URI;
use REST::Client;
use Data::Dumper;
use XML::Simple qw(:strict);

my %parameters = ();
my $uri = new URI("https://rxnav.nlm.nih.gov");
my $json;
my $client = REST::Client->new();
my $path = "/REST/allconcepts";
my $output = $ARGV[0] || die "Usage: perl rxnorm-ingredients-for-ccda.pl my-rxcuis.txt: Please Provide a file name to output results$!";

open(OUT,">".$output) || die "Unable to open file for writing $!";

##only retrieve these RxNorm TTYs
$parameters{"tty"} = "IN+MIN+BN+PIN";
my $results = run_query($path,\%parameters);
my $xml = XMLin($results,KeyAttr => {},ForceArray=>0);

##just in case you want to see the raw output in object form
#print Dumper(\$xml);

foreach my $minConcept(@{ $xml->{minConceptGroup}->{minConcept}}) {
    
    #printf "%s\n",$minConcept->{rxcui};
    printf OUT "%s\n",$minConcept->{rxcui};
}

sub run_query {
    
        my ($path, $parameters) = @_;
        
        ##this is needed to prevent the '+' sign from being converted to an encoded entity - %2B
        local $URI::Escape::escapes{'+'} = '+';
	$uri->path($path);
	$uri->query_form($parameters);
	print qq{Fetching RxCUIs at $uri\n\n};
	my $query = $client->GET($uri) || die "Could not execute query$!";
	my $results = $query->responseContent;
	return $results;
    
}
