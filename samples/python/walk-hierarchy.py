#################################################################################
#usage of the script
#usage: retrieve-cui-or-code.py -u USERNAME -p PASSWORD -v VERSION -i IDENTIFIER
#note that computing descendants can take time, especially for terminology concepts with many descendants, closer to the tree-top of a given source vocabulary.
#################################################################################

from Authentication import *
import requests
import json
import argparse

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-u", "--username", required =  True, dest="username", help = "enter username")
parser.add_argument("-p", "--password", required =  True, dest="password", help = "enter passowrd")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-s", "--source", required =  True, dest="source", help = "enter a source vocabulary, like 'SNOMEDCT_US'")
parser.add_argument("-i", "--identifier", required =  True, dest="identifier", help = "enter an identifier, like 9468002")


args = parser.parse_args()
username = args.username
password = args.password
version = args.version
source = args.source
identifier = args.identifier
uri = "https://uts-ws.nlm.nih.gov"

##Choose one of these below to traverse parents, children, ancestors (recursive parents), or descendants (recursive children)
#content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/children"
content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/descendants"
#content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/parents"
#content_endpoint = "/rest/content/"+version+"/source/"+source+"/"+identifier+"/ancestors"

##get at ticket granting ticket for the session
AuthClient = Authentication(username,password)
tgt = AuthClient.gettgt()
pageNumber=0


while True:
    pageNumber += 1
    query = {'ticket':AuthClient.getst(tgt),'pageNumber':pageNumber}
    r = requests.get(uri+content_endpoint,params=query)
    print(r.url)
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    pageCount=items["pageCount"]

    
    print("Results for page " + str(pageNumber)+"\n")
    for result in items["result"]:

      try:
        print "ui: " + result["ui"]
      except:
        NameError
      try:
        print "uri: " + result["uri"]
      except:
        NameError
      try:
        print "name: " + result["name"]
      except:
        NameError
      try:
        print "Source Vocabulary: " + result["rootSource"]
      except:
        NameError
      print "\n"
        
    if pageNumber > pageCount:
        print("End of result set")
        break
    
    print("*********")