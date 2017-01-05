#This script takes a list of rxnorm normal forms and attempts to associate with a MIN,PIN, or IN
#coding=utf-8
#get status of each rxcui
#if active, get all ingredients (IN,MIN,PIN)
#if there is a MIN, add that to the ingredients dictionary, ignore others
#if there is a PIN, add that to the ingredients dictionary, ignore others
#if only an IN exists, check for a salt form (PIN), and then see if that salt form exists already in USPMG.
#if the PIN does not exist, add the single ingredient form to the list.

import requests
import json
import argparse
import simplejson
import collections
import sys
from requests import utils
from Authentication import *
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")


uts = "https://uts-ws.nlm.nih.gov/"
uri = "https://rxnav.nlm.nih.gov"
args = parser.parse_args()
apikey = args.apikey
inputfile=args.inputfile
outputfile=args.outputfile

ingredients = {}
insFromPins = []
complete = False

###################################
#get TGT for our session
###################################
AuthClient = Authentication(apikey) 
tgt = AuthClient.gettgt()

def get(path,query):
  r = requests.get(uri+path, params=query)
  print(r.url)
  return simplejson.loads(r.text)
  
def uts_get(path,query):
  r = requests.get(uts+path, params=query)
  print(r.url)
  if r.status_code == 404:
     print "Found 404"
     return "404"
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
    global insFromPins
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
              if results["IN"]["name"] not in insFromPins:
                 insFromPins.append(results["IN"]["name"])
           complete = True

       elif "MIN" not in results and "PIN" not in results and results["IN"]["rxcui"] not in ingredients.keys() and complete == False:    
           saltFormCuis = getSaltFormCuis(results["IN"]["rxcui"])
           for rxcui in saltFormCuis:
                  uspAtom = checkForUspAtom(saltFormCuis[rxcui]["umlscui"])
                  ##if there is a USP atom that exists for the salt form, add it into the insFromPins list and add it to the ingredients dictionary
                  ##this prevents RxNorm single ingredient drugs that have salt forms already in the USP Example Drug list from appearing as if they are new
                  if uspAtom!="404" and rxcui not in ingredients.keys():
                       #remove the CUI, we don't need it anymore
                       del saltFormCuis[rxcui]["umlscui"]
                       ingredients[rxcui] = saltFormCuis[rxcui]
                       print "added existing salt form, " + saltFormCuis[rxcui]["name"]+ " to the list of ingredients"
                       if results["IN"]["name"] not in insFromPins:
                          #insFromPins.append(saltFormCuis[rxcui]["name"].lower().split(' ')[0])
                          insFromPins.append(results["IN"]["name"])
                       complete = True
                  #here there is no existing salt form from USP, so we add a new single ingredient as long as it hasn't been added already
                  elif uspAtom == "404" and results["IN"]["rxcui"] not in ingredients.keys():
                        if results["IN"]["name"] not in insFromPins:
                           print "added new salt form, " + saltFormCuis[rxcui]["name"]+ " to the list of ingredients"
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
                  

f.close()

w = open(outputfile, 'w')

for rows in sorted(ingredients.values()):
    line = '|'.join(rows.values())
    w.write(line+"\n")
    
