## Steven Emrick - steve.emrick@nih.gov
## usage: python crosswalk.py -k <your-api-key>
## You can specify a specific UMLS version with the -v argument, but it is not required
## This reads a file with codes from the Human Phenotype Ontology and maps them to the US Edition of SNOMED CT through UMLS CUIs

from __future__ import print_function
from Authentication import *
import requests
import json
import argparse
import collections
import sys
import os

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")

args = parser.parse_args()
apikey = args.apikey
version = args.version
AuthClient = Authentication(apikey)

###################################
#get TGT for our session
###################################

tgt = AuthClient.gettgt()
base_uri = "https://uts-ws.nlm.nih.gov"
crosswalk_endpoint = "/rest/crosswalk/"+version+"/source/HPO"

def crosswalk_code(path):
    query = {'ticket': AuthClient.getst(tgt),'targetSource': 'SNOMEDCT_US'}
    r = requests.get(base_uri + path, params=query)
    #print(r.url + "\n")
    items = json.loads(r.text)
    return items

with open('hpo-codes.txt','r') as f:
     for line in f:
         ##get rid of newlines
         code = line.strip()
         path =  crosswalk_endpoint+"/"+code
         try:
             results = crosswalk_code(path)
             for sourceAtomCluster in results["result"]:
                 print('HPO Code - ' + code+ '\t' + 'SNOMEDCT concept -- ' + sourceAtomCluster["ui"] + ': ' + sourceAtomCluster["name"])

         except ValueError:
             print("No result found for "+code)
             pass

f.close()

