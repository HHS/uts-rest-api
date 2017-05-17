##################################################################################################################################################################
# usage of the script
# usage: python walk-hierarchy.py -k APIKEY -v VERSION -s SOURCE -i IDENTIFIER -o operation
# note that computing descendants can take time, especially for terminology concepts with many descendants, closer to the tree-top of a given source vocabulary.
##################################################################################################################################################################

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
parser.add_argument("-s", "--source", required =  True, dest="source", help = "enter a source vocabulary, like 'SNOMEDCT_US'")
parser.add_argument("-i", "--identifier", required =  True, dest="identifier", help = "enter an identifier, like 9468002")
parser.add_argument("-o", "--operation", required = True, dest="operation", help = "choose an operation such as 'children', 'parents', 'descendants', or 'ancestors'")


args = parser.parse_args()
#username = args.username
#password = args.password
apikey = args.apikey
version = args.version
source = args.source
identifier = args.identifier
operation = args.operation
uri = "https://uts-ws.nlm.nih.gov"
content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/"+operation

##get at ticket granting ticket for the session
AuthClient = Authentication(apikey)
tgt = AuthClient.gettgt()
pageNumber=1

while True:
    
    query = {'ticket':AuthClient.getst(tgt),'pageNumber':pageNumber}
    r = requests.get(uri+content_endpoint,params=query)
    print(r.url)
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    pageCount=items["pageCount"]

    
    print("Results for page " + str(pageNumber)+"\n")
    for result in items["result"]:

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
      print("\n")
    pageNumber += 1
    
    if pageNumber > pageCount:
        print("End of result set")
        break
    
    print("*********")
