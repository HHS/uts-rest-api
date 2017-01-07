#This script takes a list of rxnorm normal forms and attempts to associate with a MIN,PIN, or IN
#coding=utf-8
#get status of each rxcui
#if active, get all ingredients (IN,MIN,PIN)
#if there is a MIN, add that to the ingredients dictionary, ignore others
#if there is a PIN, add that to the ingredients dictionary, ignore others
#if only an IN exists add that to the ingredients dictionary
##at the end, for each IN, check and see if USP has a related salt form PIN via the UMLS API  If so, remove the IN.

import requests
import json
import argparse
import simplejson
import collections
import sys
import time
from requests import utils
from Authentication import *
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")


uts = "https://uts-ws.nlm.nih.gov/"
uri = "https://rxnav.nlm.nih.gov"
#uri = "https://morc3.nlm.nih.gov"
args = parser.parse_args()
apikey = args.apikey
inputfile=args.inputfile
outputfile=args.outputfile

ingredients = {}
complete = False

###################################
#get TGT for our session
###################################
AuthClient = Authentication(apikey) 
tgt = AuthClient.gettgt()

def get(path,query):
      try:
         time.sleep(.05)
         r = requests.get(uri+path, params=query, timeout=10)
         print(r.url)
         return simplejson.loads(r.text)
      except requests.exceptions.RequestException as e:
         print "Connection timing out..."
         sys.exit(1)
   
       
def uts_get(path,query):
  r = requests.get(uts+path, params=query)
  print(r.url)
  if r.status_code == 404:
     #print "404"
     return "no usp atom"
  else:
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
   
def getSaltFormCuis(rxcui):
    cuis = {}
    path = "/REST/rxcui/"+rxcui+"/related.json?tty=PIN"
    query = {}
    results=get(path,query)
    for group in results["relatedGroup"]["conceptGroup"]:
        try:
           for properties in group["conceptProperties"]:
               #print properties["rxcui"]+", "+ properties["name"]
               cuis[properties["rxcui"]] = {"rxcui":properties["rxcui"],"tty":properties["tty"],"name":properties["name"],"umlscui":properties["umlscui"]}
                  
        except:
           KeyError
    #print cuis
    return cuis

 
def checkForUspAtom(cui):
    path = "/rest/content/current/CUI/"+cui+"/atoms"
    query = {"sabs":"USPMG","ttys":"PT","ticket":AuthClient.getst(tgt)}
    results = uts_get(path,query)
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
              #print results["PIN"]["name"]
           complete = True
           
       
       elif "MIN" not in results and "PIN" not in results and results["IN"]["rxcui"] not in ingredients.keys() and complete == False:
           if results["IN"]["rxcui"] not in ingredients.keys():
              ingredients[results["IN"]["rxcui"]] = results["IN"]
           complete = True
       
                        
with open(inputfile, 'r') as f:
     for line in f:        
        rxcui = line.strip()
        json = getRxCuiStatus(rxcui)
        status = json["rxcuiStatus"]["status"].encode('utf-8')
        
        if status == "Active":
            related = checkIngredient(rxcui)
            parseIngredient(related)
        elif status == "Remapped" or status == "Quantified":
            for remapped in json["rxcuiStatus"]["minConceptGroup"]["minConcept"]:
                related = checkIngredient(remapped["rxcui"])
                parseIngredient(related)
                
            
f.close()

w = open(outputfile, 'w')

##cleanup - remove INs that have a salt form with an exising USP atom, and add the USP salt form if it is not already in the ingredients dictionary
for rxcui in ingredients.keys():
    if ingredients[rxcui]["tty"] == "IN":
       saltFormCuis = getSaltFormCuis(rxcui)
       for pin in saltFormCuis.keys():
           ##not all PINs in RxNorm will have UMLS CUIs
           #print saltFormCuis[pin]
           if saltFormCuis[pin]["umlscui"]:
                 uspAtom = checkForUspAtom(saltFormCuis[pin]["umlscui"])
                 if uspAtom != "no usp atom" and rxcui in ingredients.iterkeys():
                     print "removing " + ingredients[rxcui]["name"]
                     #remove the single ingredient form
                     del ingredients[rxcui]
                     #add the USP salt form
                     if saltFormCuis[pin]["rxcui"] not in ingredients.iterkeys():
                        print "adding " + saltFormCuis[pin]["name"]
                        #get rid of the UMLS CUI - we don't need it anymore
                        del saltFormCuis[pin]["umlscui"]
                        ingredients[rxcui] = saltFormCuis[pin]
##output results
for rows in sorted(ingredients.values()):
    line = '|'.join(rows.values())
    w.write(line+"\n")
    
