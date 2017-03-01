''' 
The script performs the following functions:
   1) Reads in a modified version of the NIOSH csv file
      Corrections and changes to the 2016 NIOSH list include:
      a) afatanib corrected to 'afatinib'
      b) bacillus calmette guerin corrected to bacillus calmette-guerin
      c) ergonovine/methylergonovine broken out into individual ingredients
      d) menopur changed to 'follicle stimulating hormone/luteinizing hormone'
      e) misoprostal corrected to 'misoprostol'
      f) omacetaxin corrected to 'omacetaxine'
   2) Retrieves the RxCUIs for each ingredient
   3) For each ingredient, retrieves the list of RxNorm SCDFs,SBDFs,
   4) MaybeRetrieve the VET_DRUG property for each drug to provide for the Vet community
   5)

'''

import requests
import json
import argparse
import simplejson
import collections
import sys
import time
import csv
from requests import utils
from Authentication import *
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")

uri = "https://rxnav.nlm.nih.gov"
#uri = "https://morc3.nlm.nih.gov"
args = parser.parse_args()
inputfile=args.inputfile

hazardous_drug_products_file = open('hazardous-drug-products.txt','w')
not_found = open('ingredients-not-found.txt','w')
drug_dictionary = {}
drug_ingredients = {} 

def get(path,query):
      try:
         time.sleep(.05)
         r = requests.get(uri+path, params=query, timeout=10)
         print(r.url)
         return simplejson.loads(r.text)
      except requests.exceptions.RequestException as e:
         print "Connection timing out..."
         sys.exit(1)

def getRxcuiByName(name):
    print(name)
    path = "/REST/rxcui.json"
    query = {"name":name}
    results = get(path,query)
    return results
    
def getRelationsByTermType(rxcui,ttys):
##todo - write algorithm.
    path = "/REST/rxcui/"+rxcui+"/related.json"
    query = {"tty":ttys}
    results = get(path,query)
    return results

    
    
def getNormalForms(rxcui_ingredient):
    ###retrieve SCDs/SBDs/GPCKs/BPCKs associated with an ingredient
    global drug_dictionary
    json = getRelationsByTermType(rxcui_ingredient,"SCD SBD GPCK BPCK")
    for related_group in json["relatedGroup"]["conceptGroup"]:
        try:
            for properties in related_group["conceptProperties"]:
                drug_dictionary[properties["rxcui"]] = {"rxcui-ingredient":rxcui_ingredient,"tty":properties["tty"],"rxcui":properties["rxcui"],"name":properties["name"]}
        except:
            KeyError
            print ("no related group for " + rxcui_ingredient)
            not_found.write("no related group found for " + rxcui_ingredient+"\n")
        
    return drug_dictionary

def getDrugForms(rxcui):
    ### retrieve SCDFs/SBDFs associated with each normal form
    global drug_dictionary
    json = getRelationsByTermType(rxcui,"SCDF SBDF")
    for related_group in json["relatedGroup"]["conceptGroup"]:
        try:
            for properties in related_group["conceptProperties"]:
                   drug_forms = {"drug-form":properties["name"]}
                   drug_dictionary[rxcui].update(drug_forms)  
        except:
            KeyError
            print ("no related group for " + rxcui)
            not_found.write("no related group found for " + rxcui+"\n")
                
    return drug_dictionary
    
def getDoseForms(rxcui):
    ### retrieve DFs associated with each normal form
    global drug_dictionary
    json = getRelationsByTermType(rxcui,"DF")
    for related_group in json["relatedGroup"]["conceptGroup"]:
        try:
            for properties in related_group["conceptProperties"]:
                   dose_forms = {"dose-form":properties["name"]}
                   drug_dictionary[rxcui].update(dose_forms)  
        except:
            KeyError
            print ("no related group for " + rxcui)
            not_found.write("no related group found for " + rxcui+"\n")
                
    return drug_dictionary
    
           
with open(inputfile,'r') as niosh:

    reader = csv.DictReader(niosh, delimiter='|')
    for line in reader:
        ingredient_name = line['Generic Name']
        search = getRxcuiByName(ingredient_name)
        try:
            for rxcui_ingredient in search["idGroup"]["rxnormId"]:
                drug_ingredients[rxcui_ingredient] = {"rxcui-ingredient":rxcui_ingredient,"ingredient-name":ingredient_name}
               
        except:
          KeyError
          not_found.write("no related group found for" + ingredient_name+"\n")

##add normal forms
for rxcui_ingredient in drug_ingredients.keys():
    drug_dictionary = getNormalForms(rxcui_ingredient)          
          
##add drug forms
for rxcui in drug_dictionary.keys():
    drug_dictionary = getDoseForms(rxcui)

for rxcui in drug_dictionary.keys():
    drug_dictionary = getDrugForms(rxcui)
   
for rxcui in sorted(drug_dictionary.keys()):
    #print drug_products["rxcui"]
    hazardous_drug_products_file.write('|'.join(drug_dictionary[rxcui].values())+"\n")



 