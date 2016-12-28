#This script provides a way to query the RxNorm API to determine the status of an RxCUI
#coding=utf-8
import requests
import json
import argparse
import xml.etree.ElementTree as ET
import simplejson
import sys
from urllib import unquote
from requests import utils
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")

uri = "https://rxnav.nlm.nih.gov"
args = parser.parse_args()
inputfile=args.inputfile

def get(path,query):
  r = requests.get(uri+path, params=query)
  #print(r.url)
  return simplejson.loads(r.text)

def getRxCuiStatus(rxcui):
  path = "/REST/rxcui/"+rxcui+"/status.json"
  query = {}
  results = get(path,query)
  return results
    
    
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
            else:
               print rxcui+"\t"+ status