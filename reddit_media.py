#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
#import json
import re

# https://www.reddit.com/dev/api/
# POST /api/search_subreddits

def html_crafterror(strCraftMain, strCraftSub, strCraftError):
  # try...except
  #   or verify variables contain values
  try:
    strCraftError = f"An unexpected error occurred in [ <b><u>{strCraftMain}</u></b> ] during action [ <b><u>{strCraftSub}</u></b> ]: <font color=red>{strCraftError}</font><br><br>"
  except Exception as e:
    #could contain sensitive information in error message
    #strCraftOutput = html_crafterror("html_crafterror", e) #don't call self during error
    strCraftError = f"An unexpected error occurred in [ <b><u>REDDIT_MEDIA</u></b> ] during action [ <b><u>HTML_CRAFTERROR</u></b> ]: <font color=red>{e}</font><br><br>"
    return strCraftError
  return strCraftError

def app_sanitize(strToSanitize):

   # try...except
   #   or verify variables contain values
   
   strSanitizePattern = r"[^a-zA-Z0-9\_\+]+"  # inverse - [^a-zA-Z0-9\_\+]+
   strSanitized = re.sub(strSanitizePattern, "", strToSanitize)  # Not concerned about case, removed flags=re.IGNORECASE
   
   return strSanitized

def app_dictionary(strDictLabel):
   
   # try...except
   #   or verify variables contain values
   
   match strDictLabel:
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
         strDictValue = f"Unrecognized value: [ {strDictLabel} ]"
   
   return strDictValue
