#This script provides a way to query the RxNorm API to determine the status of an RxCUI
#coding=utf-8
#get status of each rxcui
#if active, get all ingredients (IN,MIN,PIN)
#if there is a MIN, add that to the MIN dictionary, ignore others
#if there is a PIN, add that to the PIN dictionary, ignore others
#otherwise, add the single ingredient to the INS dictionary
#todo - improve algorithm so that one call can be made to tty=IN+MIN+PIN, which requires an OrderedDict to make sure that MINS come first, then PINS, then INS

import requests
import json
import argparse
import simplejson
import collections
import sys
from urllib import unquote
from requests import utils
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")


uri = "https://rxnav.nlm.nih.gov"
args = parser.parse_args()
inputfile=args.inputfile
outputfile=args.outputfile

INS = {}
PINS = {}
MINS = {}
isPresent = False

def get(path,query):
  r = requests.get(uri+path, params=query)
  print(r.url)
  return simplejson.loads(r.text)
  
def getRxCuiStatus(rxcui):
  path = "/REST/rxcui/"+rxcui+"/status.json"
  query = {}
  results = get(path,query)
  return results
  
def checkIngredient(rxcui,ingredient):
   path = "/REST/rxcui/"+rxcui+"/related.json?tty="+ingredient
   query = {}
   results=get(path,query)
   return results
   
def parseIngredient(related):
    global isPresent
    
    for group in related["relatedGroup"]["conceptGroup"]:
        try:
           for properties in group["conceptProperties"]:
               #print properties["rxcui"]+", "+ properties["name"]
               if group["tty"] == "MIN" and not properties["rxcui"] in MINS and isPresent == False:
                  MINS[properties["rxcui"]] = properties["name"]
                  isPresent = True
                         
               if group["tty"] == "PIN" and not properties["rxcui"] in PINS and isPresent == False:
                  PINS[properties["rxcui"]] = properties["name"]
                  isPresent = True
               
               if group["tty"] == "IN" and not properties["rxcui"] in INS and isPresent == False:
                  INS[properties["rxcui"]] = properties["name"]
                  isPresent = True
                  
        except:
           KeyError
    return isPresent

with open(inputfile, 'r') as f:
     for line in f:
        isPresent = False
        allIngredients = ("MIN","PIN","IN")
        rxcui = line.strip()
        json = getRxCuiStatus(rxcui)
        status = json["rxcuiStatus"]["status"].encode('utf-8')
        
        if status == "Active":
            for ingredient in allIngredients:
                  if isPresent == False:
                     related = checkIngredient(rxcui,ingredient)
                     print "checking "+ingredient+ " for " + rxcui
                     parseIngredient(related)
                  

f.close()
w = open(outputfile, 'w')

print "printing output file"
            
for rxcui,string in MINS.iteritems():
   w.write(rxcui+"\tMIN\t"+string+"\n")

for rxcui,string in PINS.iteritems():
   w.write(rxcui+"\tPIN\t"+string+"\n")

for rxcui,string in INS.iteritems():
   w.write(rxcui+"\tIN\t"+string+"\n")