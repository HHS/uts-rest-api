# uts-rest-api (beta)
This repository features code samples in various languages that show how to use the Unified Medical Language System (UMLS) Terminology Services REST API.

The [UMLS](http://www.nlm.nih.gov/research/umls) is published twice per year (November and May) as a service of the [National Library of Medicine](http://www.nlm.nih.gov).

For more information please see the UMLS REST API [technical documentation](https://documentation.uts.nlm.nih.gov/rest/home.html).

### Java
To run the Java samples, you can clone this repostiory and then import the pom.xml as an existing maven project in Eclipse or other IDE.  Each java class can be run as a Junit4 test.

### Perl
To run the perl clients, you'll need to install the following perl modules:
*   JSON
*   URI 
*   GET
*   LWP::UserAgent
*   HTML::Form

Note: On OS X, you'll need to install the Mozilla:CA module or set the PERL_LWP_SSL_CA_FILE environment variable to point to the CA X.509 certificates.

### Python
To run the python clients, you'll need to have at Python version 2.7 or above installed on your system.  The scripts have been tested on 2.7 as well as Python 3.0.  You will also need the following python libraries installed:
*   requests
*   json
*   argparse
*   pyquery
*   lxml


