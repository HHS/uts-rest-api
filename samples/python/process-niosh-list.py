''' 
The script performs the following functions:
   1) Reads in a modified version of the NIOSH csv file
      Corrections and changes to the 2016 NIOSH list include:
      a) afatanib corrected to 'afatinib'
      b) bacillus calmette guerin corrected to 'bacillus calmette-guerin'
      c) ergonovine/methylergonovine broken out into individual ingredients with their own rows
      d) menopur changed to 'follicle stimulating hormone/luteinizing hormone'
      e) misoprostal corrected to 'misoprostol'
      f) omacetaxin corrected to 'omacetaxine'
   2) Retrieves the RxCUIs for each ingredient, and place into an ingredient dictionary along with some of the NIOSH information like Pregnancy Cat, Black Box, etc.
   3) For each ingredient, retrieves the list of RxNorm SCD,SBD,GPCK,BPCK (the normal forms) and place into drug_products dictionary.
   4) For each normal form, retrieve SBDF,SCDF,DF,PRESCRIBABLE and VET_DRUG properties
   5) Merge drug_products dictionary and drug_ingredients dictionary
   6) Write output

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
drug_synonyms = open('hazardous-drug-synonyms.txt','w')
not_found = open('ingredients-not-found.txt','w')
drug_dictionary = {}
drug_ingredients = {}
drug_master_view = {}

def get(path,query):
      try:
         time.sleep(.10)
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
    path = "/REST/rxcui/"+rxcui+"/related.json"
    query = {"tty":ttys}
    results = get(path,query)
    return results

def getAllProperties(rxcui):
    path = "/REST/rxcui/"+rxcui+"/allProperties.json"
    query = {"prop":"all"}
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


###could consolidate getDrugForms and getDoseForms into one function with variable term type and dict key inputs    
    
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
    

def getDrugProperties(rxcui):
    global drug_dictionary
    json = getAllProperties(rxcui)
    drug_properties = {"PRESCRIBABLE":"","VET_DRUG":"","SYNONYMS":[]}
    for properties in json["propConceptGroup"]["propConcept"]:
        try:
           if properties["propName"] == "PRESCRIBABLE" and properties["propValue"] == "Y":
              drug_properties["PRESCRIBABLE"] = "PRESCRIBABLE"
           if properties["propName"] == "VET_DRUG" and properties["propValue"] == "US":
              drug_properties["VET_DRUG"] == "VET"
              #print ("found vet drug " + rxcui)
           if properties["propName"] == "RxNorm Synonym":
              #drug_synonyms = {"rxcui":rxcui,"synonym":properties["propValue"]}
              print ("found synonym " + properties["propValue"])
              drug_properties["SYNONYMS"].append(properties["propValue"])
   
        except:
           KeyError
           print("no attribute available for " + rxcui)
    print(drug_properties)     
    drug_dictionary[rxcui].update(drug_properties)
    return drug_dictionary

    
with open(inputfile,'r') as niosh:

    reader = csv.DictReader(niosh, delimiter='|')
    for line in reader:
        ingredient_name = line['Generic Name']
        table_no = line['Table No']
        black_box = line['Black Box']
        preg_cat = line['Preg Cat']
        activity = line['Activity']
        search = getRxcuiByName(ingredient_name)
        try:
            for rxcui_ingredient in search["idGroup"]["rxnormId"]:
                drug_ingredients[rxcui_ingredient] = {"rxcui-ingredient":rxcui_ingredient,"ingredient-name":ingredient_name,"table-no":table_no,"black-box":black_box,"preg_cat":preg_cat,"activity":activity}
               
        except:
          KeyError
          not_found.write("no related group found for" + ingredient_name+"\n")

##add normal forms
for rxcui in drug_ingredients.keys():
    drug_dictionary = getNormalForms(rxcui)          
          
##add dose forms
for rxcui in drug_dictionary.keys():
    drug_dictionary = getDoseForms(rxcui)

##add drug forms
for rxcui in drug_dictionary.keys():
    drug_dictionary = getDrugForms(rxcui)

## check for human prescribable and vet drug properties    
for rxcui in drug_dictionary.keys():
    drug_dictionary = getDrugProperties(rxcui)


for rxcui_ingredient in drug_ingredients.keys():
    for rxcui,rows in drug_dictionary.iteritems():
        for value in rows.values():
            if value == rxcui_ingredient:
               drug_master_view[rxcui] = dict(drug_ingredients[rxcui_ingredient], **drug_dictionary[rxcui])
               drug_master_view[rxcui]['niosh-drug-form'] = "NIOSH Category "+drug_master_view[rxcui]['table-no'] + " " + drug_master_view[rxcui]['dose-form']
    
for rxcui in sorted(drug_dictionary.keys()):
    #print drug_products["rxcui"]
    #hazardous_drug_products_file.write('|'.join(drug_master_view[rxcui].values())+"\n")
    for key,value in drug_master_view[rxcui].items():
        if key == "SYNONYMS":
           for synonym in value:
               drug_synonyms.write(rxcui+"|"+synonym+"\n")
    
    ##Don't need synonyms anymore so we remove from the dictionary
    del drug_master_view[rxcui]["SYNONYMS"]               
    hazardous_drug_products_file.write('|'.join(drug_master_view[rxcui].values())+"\n")     
        

    
     
     
     
     

 