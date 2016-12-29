#This script provides a way to query the RxNorm API to determine the status of an RxCUI
#coding=utf-8
#get status of each rxcui
#if active, get all ingredients (IN,MIN,PIN)
#if there is a MIN, add that to the ingredients dictionary, ignore others
#if there is a PIN, add that to the ingredients dictionary, ignore others
#otherwise, add the single ingredient to the ingredients dictionary

import requests
import json
import argparse
import simplejson
import collections
import sys
from requests import utils
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")


uri = "https://rxnav.nlm.nih.gov"
args = parser.parse_args()
inputfile=args.inputfile
outputfile=args.outputfile

ingredients = {}
complete = False

def get(path,query):
  r = requests.get(uri+path, params=query)
  print(r.url)
  return simplejson.loads(r.text)
  
def getRxCuiStatus(rxcui):
  path = "/REST/rxcui/"+rxcui+"/status.json"
  query = {}
  results = get(path,query)
  return results
  
def checkIngredient(rxcui):
   path = "/REST/rxcui/"+rxcui+"/related.json?tty=IN+MIN+PIN"
   query = {}
   results=get(path,query)
   return results
   
def parseIngredient(related):
    
    results = {}
    global complete
    complete = False
    
    for group in related["relatedGroup"]["conceptGroup"]:
        try:
           for properties in group["conceptProperties"]:
               #print properties["rxcui"]+", "+ properties["name"]
               results[group["tty"]] = {"rxcui":properties["rxcui"],"tty":properties["tty"],"name":properties["name"]}
                  
        except:
           KeyError
           
   
    for tty in sorted(results.keys()):
        #print tty
       if "MIN" in results and complete == False:
           #print results["MIN"]
           if results["MIN"]["rxcui"] not in ingredients.keys():
              ingredients[results["MIN"]["rxcui"]] = results["MIN"]
           complete = True
       elif "MIN" not in results and "PIN" in results and complete == False:
           #print results["PIN"]
           if results["PIN"]["rxcui"] not in ingredients.keys():
              ingredients[results["PIN"]["rxcui"]] = results["PIN"]
           complete = True
       elif "MIN" not in results and "PIN" not in results and complete == False:
           #print results["IN"]
           if results["IN"]["rxcui"] not in ingredients.keys():
              ingredients[results["IN"]["rxcui"]] = results["IN"]
           complete == True
    
with open(inputfile, 'r') as f:
     for line in f:        
        rxcui = line.strip()
        json = getRxCuiStatus(rxcui)
        status = json["rxcuiStatus"]["status"].encode('utf-8')
        
        if status == "Active":
            related = checkIngredient(rxcui)
            parseIngredient(related)
                  

f.close()

w = open(outputfile, 'w')

for rows in sorted(ingredients.values()):
    line = '\t'.join(rows.values())
    w.write(line+"\n")
    
