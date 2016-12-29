###Takes a list of CUIs that have a USPMG atoms
###Make a call to the /atoms endpoint
###Check to see if there is an RxNorm atom - if yes, output rxcui,tty,name
###If not, output MTHU code, tty, name

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
parser.add_argument("-o", "--outputfile", required = False, dest = "outputfile", help = "enter a name for your output file")
parser.add_argument("-s", "--sabs", required = False, dest="sabs",help = "enter a comma-separated list of vocabularies, like MSH, SNOMEDCT_US, or RXNORM")
parser.add_argument("-t", "--ttys", required = False, dest="ttys",help = "enter a comma-separated list of term types, like PT,SY,IN")
parser.add_argument("-i", "--inputfile", required = False, dest = "inputfile", help = "enter a name for your input file")


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
pageNumber=1
pageCount=1
if outputfile:
   o = open(outputfile, 'w')

  
def get(path,query):
  r = requests.get(base_uri+path, params=query)
  #print(r.url)
  return simplejson.loads(r.text,object_pairs_hook=OrderedDict)
  
  
def retrieveConceptAtoms(cui):
   
    path = "/rest/content/"+version+"/CUI/"+cui+"/atoms"
    query = {"ticket":AuthClient.getst(tgt)}
    if sabs:
       query["sabs"] = sabs
    if ttys:
       query["ttys"] = ttys
     
     
    results = get(path,query)
    return results
    
done = False  
with open(inputfile, 'r') as f:
    
    for line in f:
        rootSources = {}
        cui = line.strip()
        json = retrieveConceptAtoms(cui)
        for atoms in json["result"]:
             
             slash = atoms["code"].rfind("/")
             code = atoms["code"][slash+1:]
             rootSources[atoms["rootSource"]] = code+"\t"+atoms["termType"]+"\t"+atoms["name"]
             

        for sab in sorted(rootSources.keys()):
            #done = False
            #print values
            #print sab
            if sab == "RXNORM":
                print rootSources[sab]
                o.write(cui+"\t"+rootSources[sab]+"\n")
            elif "RXNORM" not in rootSources:
                print rootSources["USPMG"]
                o.write(cui+"\t"+rootSources["USPMG"]+"\n")
               
               

        
f.close()