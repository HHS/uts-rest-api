##############################################################################################################################
# Version 1.0 - 7/28/2015
# The ticket client has two methods:
#   getTgt() and getServiceTicket()
#   run getTgt() to obtain your ticket granting ticket.
#   run getServiceTicket() before each call to https://uts-ws.nlm.nih.gov/rest/content or other future endpoints... to obtain a service ticket
#   in your client script, include the line use Authentication::TicketClient;
#   make a new ticket client as follows:
#   my $ticketClient = new TicketClient(username=>"yourusername",password=>"yourpassword",service=>"http://umlsks.nlm.nih.gov",tgt=>"");
##############################################################################################################################

use warnings;
use LWP::UserAgent;
use URI;
use HTML::Form;

package TicketClient;

   sub new {

        my ($class,%args) = @_;
        return bless { %args }, $class;

   }

   sub getTgt {

      my $self = shift;
      my $uri = URI->new("https://utslogin.nlm.nih.gov");
      my $ua = LWP::UserAgent->new;
      $uri->path("/cas/v1/tickets");
      my $query = $ua->post($uri, 
				['username'=>$self->{username}, 
				 'password'=>$self->{password}
				],); 
	  die "Error: ", $query->status_line unless $query->is_success;
			
      my @forms = HTML::Form->parse($query);
      my $form = $forms[0];
      my $tgtUrl = $form->action;
      
      ##actually here we're not getting just the TGT, but the entire URL from the action attribute of the form
      ##returned in the call.  This saves us from having to extract the TGT with substr or something else.
      ##assign the action attribute URL to the 'tgt' property of the TicketClient.
      $self->{tgt} = $tgtUrl;

      }## end getTgt

        sub getServiceTicket {
        
        my $self = shift;
        my $ua = LWP::UserAgent->new;
        my $uri = URI->new($self->{tgt});
        my $query = $ua->post($uri, 
				['service'=>$self->{service}
				],); 
			die "Error: ", $query->status_line unless $query->is_success;
        
        my $st = $query->content;
        return $st;
        
        }
        ## end getServiceTicket


1;