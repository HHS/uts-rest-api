#################################################################################
# usage of the script
# usage: python search-terms.py -k APIKEY -v VERSION -s STRING
# see https://documentation.uts.nlm.nih.gov/rest/search/index.html for full docs
# on the /search endpoint
#################################################################################

from __future__ import print_function
from Authentication import *
import requests
import json
import argparse

parser = argparse.ArgumentParser(description='process user given parameters')
#parser.add_argument("-u", "--username", required =  True, dest="username", help = "enter username")
#parser.add_argument("-p", "--password", required =  True, dest="password", help = "enter passowrd")
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-s", "--string", required =  True, dest="string", help = "enter a search term, like 'diabetic foot'")
parser.add_argument("-l", "--library", required =  False, dest="sabs", help = "enter a library like SNOMEDCT_US")
parser.add_argument("-st", "--searchType", required =  False, dest="searchType", help = "enter a search type like exact")
parser.add_argument("-it", "--inputType", required =  False, dest="inputType", help = "enter the search input type like ‘atom’, ‘code’,‘sourceConcept’,‘sourceDescriptor’,‘sourceUi’,‘tty’")
parser.add_argument("-rt", "--returnType", required =  False, dest="returnType", help = "enter the search return type like Use ‘code’,‘sourceConcept’, ‘sourceDescriptor’, or ‘sourceUi’ if you prefer source-asserted identifiers rather than CUIs in your search results.")
args = parser.parse_args()
#username = args.username
#password = args.password
apikey = args.apikey
version = args.version
string = args.string
library=args.sabs
searchType=args.searchType
inputType=args.inputType
returnType=args.returnType
uri = "https://uts-ws.nlm.nih.gov"
content_endpoint = "/rest/search/"+version
##get at ticket granting ticket for the session
AuthClient = Authentication(apikey)
tgt = AuthClient.gettgt()
pageNumber=0
total=0
while True:
    ##generate a new service ticket for each page if needed
    ticket = AuthClient.getst(tgt)
    pageNumber += 1
    query = {'string':string,'ticket':ticket, 'pageNumber':pageNumber,'sabs':library, 'searchType':searchType,'inputType':inputType, 'returnType':returnType}
    #query['includeObsolete'] = 'true'
    #query['includeSuppressible'] = 'true'
    #query['returnIdType'] = "sourceConcept"
    #query['sabs'] = "SNOMEDCT_US"
    r = requests.get(uri+content_endpoint,params=query)
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    jsonData = items["result"]
    #print (json.dumps(items, indent = 4))
    print("Results for page " + str(pageNumber)+"\n")
    
    for result in jsonData["results"]:
        
      try:
        print("ui: " + result["ui"])
      except:
        NameError
      try:
        print("uri: " + result["uri"])
      except:
        NameError
      try:
        print("name: " + result["name"])
      except:
        NameError
      try:
        print("Source Vocabulary: " + result["rootSource"])
      except:
        NameError
      
      print("Page Finished \n")
      total += 1
    
    ##Either our search returned nothing, or we're at the end
    if jsonData["results"][0]["ui"] == "NONE":
        break
    print("*********")
    print("Total Results:",total)
    
    
    
    
    

