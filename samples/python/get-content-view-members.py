## usage: python get-content-view-members.py -k <your-api-key> -f <your-output-file>
## You can specify a specific UMLS version with the -v argument, but it is not required
## This script will download the CORE Problem List subset of SNOMED CT
## and save to a file that you specify. There are around 250 pages of output to save - the CORE Problem list contains over 5,500 SNOMED CT codes
## and attributes.  The script takes around 30 minutes to complete depending on your internet connection.

from Authentication import *
import requests
import json
import argparse
import collections
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-k", "--apikey", required = True, dest = "apikey", help = "enter api key from your UTS Profile")
parser.add_argument("-v", "--version", required =  False, dest="version", default = "current", help = "enter version example-2015AA")
parser.add_argument("-f", "--outputfile", required = True, dest = "outputfile", help = "enter a name for your output file")

args = parser.parse_args()
apikey = args.apikey
version = args.version
outputfile=args.outputfile
AuthClient = Authentication(apikey) 

###################################
#get TGT for our session
###################################

tgt = AuthClient.gettgt()
base_uri = "https://uts-ws.nlm.nih.gov"
#C2711988 is the CUI for the SNOMED CT CORE Problem List content view
#Full list of content views is here: https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/content_views.html,
#or over web services at https://uts-ws.nlm.nih.gov/rest/content-views/current?ticket=ST...
content_view_endpoint = "/rest/content-views/"+version+"/CUI/C2711988/members"
tgt = AuthClient.gettgt()
pageNumber=1
pageCount=1
f = open(outputfile, 'w')

#column headers - modify accordingly if you are computing a different subset
f.write("SNOMED_CID|NAME|FIRST_IN_SUBSET|IS_RETIRED_FROM_SUBSET|OCCURRENCE|USAGE|REPLACED_BY_SNOMED_CID\n")

##There are ~ 250 pages in this subset, if you're using the default of 25 objects per page.
while pageNumber<=pageCount:
    
    query = {'ticket':AuthClient.getst(tgt),'pageNumber':pageNumber}
    r = requests.get(base_uri+content_view_endpoint,params=query)
    print(r.url+"\n")
    r.encoding = 'utf-8'
    items  = json.loads(r.text)
    pageCount=items["pageCount"]
    
    print("Fetching page " + str(pageNumber)+" of results\n")
    
    for result in items["result"]:
        
        f.write(result["ui"]+"|"+str(result["name"]))
        
        #MOST CONTENT VIEW MEMBERS DO NOT HAVE ATTRIBUTES, BUT FOR MEMBERS OF THE SNOMED CT CORE PROBLEM LIST
        #THESE ARE THE CURRENT LIST OF ATTRIBUTE NAMES THAT ARE DEFINED. HOWEVER, IN THE DATA THEY ARE NOT ALWAYS PRESENT
        #FOR EXAMPLE, IF IS_RETIRED_FROM_SUBSET = True, THERE IS NO 'OCCURRENCE' OR 'USAGE' ATTRIBUTE AVAILABLE, SO WE MUST CHECK AND THEN
        ##OUTPUT EMPTY FIELDS IF NEEDED    
        attributes=result["contentViewMemberAttributes"]
        
        if len(attributes) > 0:
            
            cv_member_attributes = (("FIRST_IN_SUBSET",""), ('IS_RETIRED_FROM_SUBSET', ""), ("OCCURRENCE", ""), ("USAGE", ""), ("REPLACED_BY_SNOMED_CID", ""))
            cv_member_attributes = collections.OrderedDict(cv_member_attributes)
                        
            existing_attributes = {}
            f.write("|")
            for attribute in attributes:
                existing_attributes[attribute["name"]] = attribute["value"]
            
            for cv_member_attribute in cv_member_attributes.keys():
                
                #populate the attributes that are presented to us in the json
                if cv_member_attribute in existing_attributes.keys():
                    cv_member_attributes[cv_member_attribute] = existing_attributes[cv_member_attribute]
                        
            for i,item in enumerate(list(cv_member_attributes.items())):
                
                ##either print a delimiter or a new line depending on where we are in the list of attributes
                if i < len(list(cv_member_attributes.items())) - 1:
                    f.write(item[1]+"|")
                else:
                    f.write(item[1]+"\n")

        else:
            f.write("\n")
        
    pageNumber+=1 