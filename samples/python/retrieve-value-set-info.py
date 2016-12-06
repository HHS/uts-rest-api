###A script to retrieve code system information from the value set bps definition document.
###Note that the rows of the input file are expected to have the

from Authentication import *
import requests
import json
import argparse
import xml.etree.ElementTree as ET
import sys

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-p", "--profile", required = False, dest = "profile", help = "Enter a binding profile, such as MU2 2016 Update")
parser.add_argument("-o", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")
parser.add_argument("-i", "--inputfile", required = True, dest = "inputfile", help = "enter a name for your input file")


args = parser.parse_args()
apikey = args.apikey
profile = args.profile
outputfile=args.outputfile
inputfile=args.inputfile

AuthClient = Authentication(apikey)
tgt = AuthClient.gettgt()

uri = "https://vsac.nlm.nih.gov/vsac/svs/RetrieveMultipleValueSets"

o = open(outputfile, 'w')

def getCodeSystem(id):
    ticket = AuthClient.getst(tgt)
    query = {'id':id,'ticket':ticket,'version':profile}
    r = requests.get(uri, params=query)
    print(r.url)
    return r.text.encode('utf-8')


with open(inputfile,'r') as f:

    for line in f:
       oid,name,memberOid,memberOidName = line.strip().split("|")
       if len(memberOid) == 0:
           codeSystem = getCodeSystem(oid)
       else:
           codeSystem = getCodeSystem(memberOid)

       xml = ET.fromstring(codeSystem)
       ns = {"ns0":"urn:ihe:iti:svs:2008"}
       codeSystemInfo = {}
       for concepts in xml.findall(".//ns0:ConceptList/ns0:Concept",ns):
           cs = concepts.get('codeSystemName')
           codeSystemVersion = concepts.get('codeSystemVersion')
           codeSystemInfo.setdefault(cs,[]).append(codeSystemVersion)
       sys.stdout.write(oid+"|"+memberOid)

       for k,v in codeSystemInfo.items():
           sys.stdout.write(k+"|"+','.join(set(v)))
           #o.write(oid+"|"+name+"|"+memberOid+"|"+k+"|"+','.join(set(v)))
           o.write(oid + "|" + name + "|" + memberOid + "|"+ memberOidName +"|" + k +"|"+','.join(set(v))+"\n")





