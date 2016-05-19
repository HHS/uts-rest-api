#!/usr/bin/python
## 5/19/2016 - update to allow for authentication based on api-key, rather than username/pw
## See https://documentation.uts.nlm.nih.gov/rest/authentication.html for full explanation

import requests
from pyquery import PyQuery as pq
from lxml import etree

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

   def gettgt(self):
     #params = {'username': self.username,'password': self.password}
     params = {'apikey': self.apikey}
     h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
     r = requests.post(uri+auth_endpoint,data=params,headers=h)
     d = pq(r.text)
     ## extract the entire URL needed from the HTML form (action attribute) returned - looks similar to https://utslogin.nlm.nih.gov/cas/v1/tickets/TGT-36471-aYqNLN2rFIJPXKzxwdTNC5ZT7z3B3cTAKfSc5ndHQcUxeaDOLN-cas
     ## we make a POST call to this URL in the getst method
     tgt = d.find('form').attr('action')
     return tgt

   def getst(self,tgt):

     params = {'service': self.service}
     h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
     r = requests.post(tgt,data=params,headers=h)
     st = r.text
     return st
   
   
   


