###Takes a list of CUIs that result from /search?string=PT,IN,MIN,PIN&inputType=tty&sabs=RXNORM,USPMG.
###For each of theses CUIs, output the atoms
###If there is a PIN from RxNorm in the same CUI as a USPMG atom, find the RxNorm associated single ingredient form and
###remove it from the final list
###Then go through again and remove USP atoms that are in the same CUI as an RxNorm atom

from Authentication import *
import requests
import simplejson
import argparse
import collections
import sys
from collections import OrderedDict
reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")
parser.add_argument("-s", "--sabs", required = False, dest="sabs",help = "enter a comma-separated list of vocabularies, like MSH, SNOMEDCT_US, or RXNORM")
parser.add_argument("-t", "--ttys", required = False, dest="ttys",help = "enter a comma-separated list of term types, like PT,SY,IN")
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")


args = parser.parse_args()
apikey = args.apikey
version = args.version
outputfile = args.outputfile
inputfile = args.inputfile
sabs = args.sabs
ttys = args.ttys
AuthClient = Authentication(apikey) 

###################################
#get TGT for our session
###################################

tgt = AuthClient.gettgt()
base_uri = "https://uts-ws.nlm.nih.gov"
rxnorm = "https://rxnav.nlm.nih.gov"
pageNumber=1
pageCount=1
auis = {}
if outputfile:
   o = open(outputfile, 'w')

 
def rxnorm_get(path,query):
  r = requests.get(rxnorm+path, params=query)
  print(r.url)
  return simplejson.loads(r.text)
 
def uts_get(path,query):
  r = requests.get(base_uri+path, params=query)
  print(r.url)
  return simplejson.loads(r.text)
  
def getSingleIngredientForm(rxcui):
   path = "/REST/rxcui/"+rxcui+"/related.json?tty=IN"
   query = {}
   #print(r.url)
   results=rxnorm_get(path,query)
   return results
  
def retrieveConceptAtoms(cui):
   
    path = "/rest/content/"+version+"/CUI/"+cui+"/atoms"
    query = {"ticket":AuthClient.getst(tgt)}
    if sabs:
       query["sabs"] = sabs
    if ttys:
       query["ttys"] = ttys
     
     
    results = uts_get(path,query)
    return results
    
with open(inputfile, 'r') as f:
    
    for line in f:
        
        cui = line.strip()
        json = retrieveConceptAtoms(cui)
        for atoms in json["result"]:
             
             slash = atoms["code"].rfind("/")
             code = atoms["code"][slash+1:]
             #rootSources[atoms["rootSource"]] = code+"\t"+atoms["termType"]+"\t"+atoms["name"]
             auis[atoms["ui"]] = {"cui":cui,"code":code,"tty":atoms["termType"],"name":atoms["name"],"sab":atoms["rootSource"]}


f.close()        
##Cleanup - find all PIN atoms in CUI with a USP atom
##Find related single ingredient form and remove it.
    
singleIngredientCuis = []

##identify PINS in the list of all atoms.  
##If there is a PIN from RxNorm that shares a CUI with a USPMG atom, find the CUI of the IN form (/rxcui/related?tty=IN) and remove all
##atoms containing that CUI

for aui1 in auis.keys():
    print '|'.join(auis[aui1].values())        
    if auis[aui1]["tty"] == "PIN":
       print "Found salt form of " + auis[aui1]["cui"] + " " + auis[aui1]["name"]
       print "searching for " + auis[aui1]["code"] + " from " + auis[aui1]["sab"]
       for aui2 in auis.keys():
           if auis[aui1]["cui"] == auis[aui2]["cui"] and auis[aui2]["sab"] == "USPMG": 
              singleIngredients = getSingleIngredientForm(auis[aui1]["code"])
              for properties in singleIngredients["relatedGroup"]["conceptGroup"][0]["conceptProperties"]:
                  singleIngredientCuis.append(properties["umlscui"])

## find the intersection of the 2 dictionaries, and delete the auis that represent single ingredients that already rels to USP salt form
         
sameCuis = [auis[cui]["cui"] for cui in auis.keys() if auis[cui]["cui"] in singleIngredientCuis]

print "Found " + str(len(auis)) + " total atoms in the result set\n"
print "Found " +str(len(sameCuis)) + " CUIs with single ingredient atoms\n"

for cui in auis.keys():
    if auis[cui]["cui"] in sameCuis:
       print "removing " + auis[cui]["name"]
       del auis[cui]


       
removals = []
log = open("removal-log.txt",'w')       
       
for cui1 in auis.keys():
    for cui2 in auis.keys():
        if auis[cui2]["sab"] == "RXNORM" and auis[cui1]["sab"] == "USPMG" and (auis[cui1]["cui"] == auis[cui2]["cui"]):
           print "Found " + cui1 + " and " + cui2 +" in " + auis[cui1]["cui"]
           #identify all USPMG atoms that are merged into the same UMLS CUI as an RxNorm atom
           removals.append(cui1)

print "Removing " + str(len(removals)) + " USP atoms that share a CUI with RxNorm\n" 
         
for cui in auis.keys():
    if cui in removals:
       line = '|'.join(auis[cui].values())
       log.write(line+"\n")
       del auis[cui]
       
print "Total of "+ str(len(auis)) + " atoms are left in results"

w = open(outputfile, 'w')

for fields in auis.values():
    line = '|'.join(fields.values())
    print line+"\n" 
    w.write(line+"\n")    
        





           


  
        
