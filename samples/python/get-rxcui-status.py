#This script provides a way to query the RxNorm API to determine the status of an RxCUI
#coding=utf-8
import requests
import json
import argparse
import xml.etree.ElementTree as ET
import simplejson
import time
import sys
from urllib import unquote
from requests import utils
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")


uri = "https://morc3.nlm.nih.gov"
args = parser.parse_args()
inputfile=args.inputfile
outputfile=args.outputfile


def get(path,query):
  time.sleep(.05)
  r = requests.get(uri+path, params=query)
  print(r.url)
  return simplejson.loads(r.text)

def getRxCuiStatus(rxcui):
  path = "/RxNormRest/rxcui/"+rxcui+"/status.json"
  query = {}
  results = get(path,query)
  return results


w = open(outputfile, 'w')
 
rxcuis = {}
 
with open(inputfile, 'r') as f:
     for line in f:
        rxcui = line.strip()
        json = getRxCuiStatus(rxcui)
        status = json["rxcuiStatus"]["status"].encode('utf-8')
        
        if not status == "Active":
            if status  == "Remapped" or status == "Quantified":
            #print rxcui +"\t" + status
               for remapped in json["rxcuiStatus"]["minConceptGroup"]["minConcept"]:
                   print rxcui +"\t"+ status+"\t"+ remapped["rxcui"]
                   rxcuis[rxcui] = {"rxcui":rxcui,"status":status,"remapped":remapped["rxcui"]}

            else:
                rxcuis[rxcui] = {"rxcui":rxcui,"status":status,"remapped":" "}
                
#output
for rows in sorted(rxcuis.values()):
    line = '|'.join(rows.values())
    w.write(line+"\n")
               