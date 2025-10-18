#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
#import json
import re

# https://www.reddit.com/dev/api/
# POST /api/search_subreddits

def html_crafterror(strCraftMain, strCraftSub, strCraftError):
  
  #  verify variables contain values
  
  try:
    strCraftError = f"An unexpected error occurred in [ <b><u>{strCraftMain}</u></b> ] during action [ <b><u>{strCraftSub}</u></b> ]: <font color=red>{strCraftError}</font><br><br>"
  except Exception as e:
    #could contain sensitive information in error message
    #strCraftOutput = html_crafterror("html_crafterror", e) #don't call self during error
    strCraftError = f"An unexpected error occurred in [ <b><u>REDDIT_MEDIA</u></b> ] during action [ <b><u>HTML_CRAFTERROR</u></b> ]: <font color=red>{e}</font><br><br>"
    return strCraftError
  return strCraftError

def app_sanitize(strToSanitize):

   #  verify variables contain values
  
   try:
     strSanitizePattern = r"[^a-zA-Z0-9\_\+]+"  # inverse - [^a-zA-Z0-9\_\+]+
     strSanitized = re.sub(strSanitizePattern, "", strToSanitize)  # Not concerned about case, removed flags=re.IGNORECASE
   except Exception as e:
     #could contain sensitive information in error message
     strSanitizeError = html_crafterror("REDDIT_MEDIA", "APP_SANITIZE", e)
     return strSanitizeError
     
   return strSanitized

def app_dictionary(strDictAttrib):
  
  #  verify variables contain values
  try:
    match strDictAttrib:
      case "kv_name":
        strDictValue = "kv-techsushi-site"
      case "kv_token":
        strDictValue = "api-reddit-token"
      case "kv_tokentype":
        strDictValue = "api-reddit-tokentype"
      case "kv_id":
        strDictValue = "api-reddit-id"
      case "kv_secret":
        strDictValue = "api-reddit-secret"
      case "url_login":
        strDictValue = "https://www.reddit.com/api/v1/access_token"
      case "url_oauth":
        #to capture user data, may need to move the /r/ out
        # /user/username/submitted
        strDictValue = "https://oauth.reddit.com/r/"
      case "txt_useragent":
        strDictValue = "imgdupedetect v0.5 by orbut8888"
      case "html_header":
        strDictValue = "<head>"
        strDictValue += "<title>TechSushi - Portfolio</title>"
        strDictValue += "<!-- <base href=\"https://www.reddit.com/\" target=\"_blank\"> -->"
        strDictValue += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        strDictValue += "<meta name=\"description\" content=\"A brief description of my webpage for search engines.\">"
        strDictValue += "</head>"
        strDictValue += "<body>Welcome to the TechSushi - Portfolio page<br><br><br>"
      case "html_footer":
        strDictValue = "Run through version [1.5.0]</body>"
      case _:
        #default unknown
        strDictValue = f"Unrecognized value: [ {strDictAttrib} ]"
  except Exception as e:
    #could contain sensitive information in error message
    strDictError = html_crafterror("REDDIT_MEDIA", "APP_DICTIONARY", e)
    return strDictError

return strDictValue

def kv_set(strSetVault, strSetName, strSetValue):
   
   # Only expected to be used during initial Reddit API and Azure KeyVault set up
   #  From the Azure WebApp, ensure you have enabled System Identity (WebApp > Settings > Identity > On > Save)
   #  From the Azure KeyVault, ensure you assign (Key Vault Secrets Officer?) role to the Azure WebApp identity named above
  
   try:
      objSetCredential = DefaultAzureCredential()
      objSetSecretClient = SecretClient(vault_url=f"https://{strSetVault}.vault.azure.net/", credential=objSetCredential) #kv-techsushi-site
      objSetSecret = objSetSecretClient.set_secret(strSetName, strSetValue) #api-reddit-id
   except Exception as e:
      #could contain sensitive information in error message
      strSetError = html_crafterror("REDDIT_MEDIA", "KV_SET", e)
      return strSetError
   
  # No value returned... necessary?
  
  return

def kv_get(strGetVault, strGetName):
   
   try:
      objGetCredential = DefaultAzureCredential()
      objGetSecretClient = SecretClient(vault_url=f"https://{strGetVault}.vault.azure.net/", credential=objGetCredential)
      objGetSecret = objGetSecretClient.get_secret(strGetName)
      strGetValue = objGetSecret.value
   except Exception as e:
      #could contain sensitive information in error message
      strGetError = html_crafterror("REDDIT_MEDIA", "KV_GET", e)
      return strGetError
      
   return strGetValue

def kv_refreshtoken(strRefVault, strRefRedditURL):
   
   #https://www.reddit.com/api/v1/access_token
  
   try:
      strRefIDLabel = app_dictionary("kv_id")
      strRefID = kv_get(strRefVault, strRefIDLabel) #kv-techsushi-site
      strRefSecretLabel = app_dictionary("kv_secret")
      strRefSecret = kv_get(strRefVault, strRefSecretLabel)
      
      objRefClientAuth = (strRefID, strRefSecret)
      dictRefPostData = { "grant_type": "client_credentials" }
      strRefUserAgent = app_dictionary("txt_useragent")
      dictRefHeader = { "User-Agent": strRefUserAgent }
      roRefReceived = requests.post(strRefRedditURL, auth=objRefClientAuth, data=dictRefPostData, headers=dictRefHeader)
      
      dictRefReceived = roRefReceived.json()      
      strRefToken = dictRefReceived["access_token"]
      strRefTokenType = dictRefReceived["token_type"]

      strRefTokenLabel = app_dictionary("kv_token")
      kv_set(strRefVault, strRefTokenLabel, strRefToken)
      strRefTokenTypeLabel = app_dictionary("kv_tokentype")
      kv_set(strRefVault, strRefTokenTypeLabel, strRefTokenType)
      
   except Exception as e:
      #could contain sensitive information in error message
      strRefGetValue = html_crafterror("KV_REFRESHTOKEN", f"{e}<br><br>{roRefReceived}<br><br>")
      return strRefreshOutput
      
   return

