#!/usr/bin/python
## 6/16/2017 - remove PyQuery dependency
## 5/19/2016 - update to allow for authentication based on api-key, rather than username/pw
## See https://documentation.uts.nlm.nih.gov/rest/authentication.html for full explanation

import requests
#from pyquery import PyQuery as pq
import lxml.html as lh
from lxml.html import fromstring

from cachetools import cached, TTLCache

# Cache tokens for repeated calls.
# Cache tgt for 5 hours
tgt = TTLCache(maxsize=2, ttl=18000)
# Cache st for 4 minutes
st = TTLCache(maxsize=2, ttl=240)

uri="https://utslogin.nlm.nih.gov"
#option 1 - username/pw authentication at /cas/v1/tickets
#auth_endpoint = "/cas/v1/tickets/"
#option 2 - api key authentication at /cas/v1/api-key
auth_endpoint = "/cas/v1/api-key"

class Authentication:

   #def __init__(self, username,password):
   def __init__(self, apikey):
    #self.username=username
    #self.password=password
    self.apikey=apikey
    self.service="http://umlsks.nlm.nih.gov"

   @cached(tgt) 
   def gettgt(self):
     #params = {'username': self.username,'password': self.password}
     params = {'apikey': self.apikey}
     h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
     r = requests.post(uri+auth_endpoint,data=params,headers=h)
     response = fromstring(r.text)
     ## extract the entire URL needed from the HTML form (action attribute) returned - looks similar to https://utslogin.nlm.nih.gov/cas/v1/tickets/TGT-36471-aYqNLN2rFIJPXKzxwdTNC5ZT7z3B3cTAKfSc5ndHQcUxeaDOLN-cas
     ## we make a POST call to this URL in the getst method
     tgt = response.xpath('//form/@action')[0]
     return tgt

   @cached(st) 
   def getst(self,tgt):

     params = {'service': self.service}
     h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
     r = requests.post(tgt,data=params,headers=h)
     st = r.text
     return st
   
   
   


