#This script provides a way to query the RxNorm API for
#prescribable drugs based on term types

import requests
import json
import argparse
import xml.etree.ElementTree as ET
import sys
from urllib import unquote
from requests import utils

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-ttys", "--termtypes", required = True, dest = "ttys", help = "Enter TTYs to query, separated by a space")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")


uri = "https://rxnav.nlm.nih.gov"
args = parser.parse_args()
ttys = args.ttys
outputfile=args.outputfile
o = open(outputfile, 'w')


def get(path,query):

    r = requests.get(uri+path, params=query)
    #print(r.url)
    return r.text.encode('utf-8')

def getRxCuisByTermType():
    path = "/REST/allconcepts"
    query = {'tty':ttys}
    results = get(path,query)
    return results


def filterRxCuis(rxcui,filter):
    path = "/REST/rxcui/"+rxcui+"/filter"
    query = {'propName': filter}
    results = get(path,query)
    return results

results = getRxCuisByTermType()
xml = ET.fromstring(results)

for rxcuis in xml.findall(".//minConcept"):
    rxcui = rxcuis.find("rxcui").text

    #now make sure the concept is part of the prescribable subset
    filtered = filterRxCuis(rxcui,'prescribable')
    rxnormdata = ET.fromstring(filtered)

    #only output if the concept belongs to the prescribable subset of RxNorm
    if len(rxnormdata) > 0:
        print rxnormdata.find('rxcui').text + " is prescribable"
        o.write(rxnormdata.find('rxcui').text+"\n")

