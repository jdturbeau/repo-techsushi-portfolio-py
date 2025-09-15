from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

#app = Flask(__name__)

def kv_set(strVault, strName, strValue):
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strVault}.vault.azure.net/", credential=credential) #kv-techsushi-site
      secret = secret_client.set_secret(strName, strValue) #api-reddit-id
   except Exception as e:
      strWebOutput = f"an unexpected error occurred during <b>SET</b>: {e}<br><br>"
      #raise strWebOutput
      return strWebOutput
   else:
      #strWebOutput = "<b>SET</b> completed successfully<br><br>"
   finally:
      #strWebOutput = "end of <b>SET</b> script<br><br>"      
   return
   
def kv_get(strVault, strName):
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strVault}.vault.azure.net/", credential=credential) #kv-techsushi-site
      secret = secret_client.get_secret(strName)
      strValue = secret.value
      #strWebOutput += f"{secret.name}<br><br>"
      #strWebOutput += f"{secret.value}<br><br>"
   except Exception as e:
      strWebOutput = f"an unexpected error occurred during <b>GET</b>: {e}<br><br>"
      #raise strWebOutput
      return strWebOutput
   else:
      #strWebOutput = "<b>GET</b> completed successfully<br><br>"
   finally:
      #strWebOutput = "end of <b>GET</b> script<br><br>"
   return strValue
   
def kv_refreshtoken(strVault, strRedditURL):
   #https://www.reddit.com/api/v1/access_token
   try:
      strID = kv_get(strVault, "api-reddit-id") #kv-techsushi-site
      strSecret = kv_get(strVault, "api-reddit-secret")
      
      #kv_get(strVault, "api-reddit-tokentype")
      #kv_get(strVault, "api-reddit-token")
      
      objClientAuth = (strID, strSecret)
      dictPostData = { "grant_type": "client_credentials" }
      dictHeader = { "User-Agent": "imgdupedetect v0.2 by orbut8888" }
      roReceived = requests.post(strRedditURL, auth=objClientAuth, data=dictPostData, headers=dictHeader)
      
      #strWebOutput += f"{roReceived.status_code}<br><br>{roReceived.text}<br><br>{roReceived.content}<br><br>{roReceived.headers}<br><br>"
      #strWebOutput += f"Attempting to parse response for JSON...<br><br>"
      dictReceived = roReceived.json()      
      strToken = dictReceived["access_token"]
      strTokenType = dictReceived["token_type"]
      #strWebOutput += f"Attempting to store token...<br><br>"
      kv_set(strVault, ("api-reddit-token", strToken)
      kv_set(strVault, ("api-reddit-tokentype", strTokenType)
      
#      strWebOutput += f"new token stored!<br><br>{strToken}<br><br>{strTokenType}<br><br>"
   except Exception as e:
      #could contain sensitive information in error message
      strWebOutput = f"Trouble with <b>REFRESH</b>, review {e}<br><br>{roReceived}<br><br>"
      #raise strWebOutput
      return strWebOutput
   else:
      #strWebOutput = f"<b>REFRESH</b> complete successfully"
   finally:
      #strWebOutput = f"<b>REFRESH</b> complete"
      
   return

def reddit_getjson(strSubReddit, lstMediaType, strTokenType, strToken, strURL):
   #handle [], [pictures], [videos], [pictures, videos], (other/unknown)
   #check POST vs GET (request.method ==

   strTokenType = kv_get(strVault, "api-reddit-tokentype")
   strToken = kv_get(strVault, "api-reddit-token")
   dictHeader = { "Authorization": f"{strTokenType} {strToken}", "User-Agent": "imgdupedetect v0.1 by orbut8888" }
   strURL = strURL #fhttps://oauth.reddit.com/r/{strSubReddit}/new
   
   roReceived = requests.get(strURL, headers = dictHeader)
   # if roReceived.status_code = 401 (unauthorized), likely need new token
   dictJson = roReceived.json()
   #strAfterURL = dictJson["data"]["after"]
   
   return dictJson

def reddit_jsontohtml(jsonContent):
   #consider [], [pictures], [videos], [pictures, videos], (other/unknown)

   
   return

def html_form():
   
   strWebOutput += f"<form action=\"/testpost\" method=\"post\"><!-- Form elements go here -->"
   strWebOutput += f"<label for=\"name\">Subreddit:</label><br><input type=\"text\" id=\"subreddit\" name=\"sub\" placeholder=\"p320\" autocomplete=\"off\">"
   strWebOutput += f"<input type=\"checkbox\" id=\"pictures\" name=\"mediatype\" value=\"pictures\" checked><label for=\"pictures\">Pictures</label>"
   strWebOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\"><label for=\"videos\">Videos</label><br><br>"
   strWebOutput += f"<button type=\"submit\">Browse Media</button></form><br><br>"

   return strWebOutput





def getcontent():
   
   
    
   try:
      strWebOutput += "end of get token from kv script<br><br>"
      dictHeader = { "Authorization": f"{strTokenType} {strToken}", "User-Agent": "imgdupedetect v0.1 by orbut8888" }
      strURL = f"https://oauth.reddit.com/r/{strSubReddit}/new"
      strWebOutput += f"{dictHeader}<br><br>"
      roReceived = requests.get(strURL, headers = dictHeader)
      # if roReceived.status_code = 401 (unauthorized), likely need new token
      strWebOutput += f"{roReceived.status_code}<br><br>{roReceived.text}<br><br>{roReceived.content}<br><br>{roReceived.headers}<br><br>"
      dictJson = roReceived.json()
      strAfterURL = dictJson["data"]["after"]
      strWebOutput += f"{strAfterURL}<br><br>"
      strWebOutput += f"text received: [ {roReceived} ]<br><br>"
   except Exception as e:
      strWebOutput += f"an unexpected error occurred during token usage: {e}<br><br>"
      return strWebOutput
   else:
      strWebOutput += f"usage completed without error<br><br>"
   finally:
      strWebOutput += "usage2 completed<br><br>"
   
   try:
      dictThreads = dictJson["data"]["children"]
      
      strWebOutput = f"<head><base href=\"https://www.reddit.com/\" target=\"_blank\"></head><body>"
      
      for dictSingle in dictThreads:
         strThreadTitle = dictSingle["data"]["title"]
         strThreadAuthor = dictSingle["data"]["author"]
         strThreadPermalink = dictSingle["data"]["permalink"]
         strThreadComments = dictSingle["data"]["num_comments"]
         strThreadURL = dictSingle["data"]["url"]
         strThreadMedia = dictSingle["data"]["media"]
         strThreadType = dictSingle.get("data", {}).get("post_hint", "Missing")
         strWebOutput += f"<font size=5><a href=\"{strThreadPermalink}\">{strThreadTitle}</a></font><br>"
         strWebOutput += f"<b>{strThreadAuthor}</b> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
         match strThreadType:
            case "image":
               strWebOutput += f"<img src =\"{strThreadURL}\" width=\"60%\"></img><p>"
            case _:
               strWebOutput += f"<font color=red>Error experienced [ {strThreadType} ]</font><p>"
      strWebOutput += f"<p><a href=\"{strAfterURL}\">Next Posts</a></p>"

   except Exception as e:
      strWebOutput += f"Trouble with JSON, review: {e}<br><br>{dictThreads}<br><br>"
      return strWebOutput
   else:
      strWebOutput += "json parse complete without error<br><br>"
   finally:
      strWebOutput += "json parse completed<br><br>"

   return strWebOutput

def testpost():
   try:
      strMethod = request.method
      strWebOutput = f"{strMethod}<br><br>"
   except Exception as e:
      strWebOutput += f"Trouble with gathering request method. See: {e}<br><br>"
      #return strWebOutput
   else:
      strWebOutput += "gathering request method complete without error<br><br>"
   finally:
      strWebOutput += "gathering request method completed<br><br>"
   try:
      strSubReddit = request.form.get('sub')
      #strSubReddit = strSubReddit.get['sub']
      strWebOutput += f"{strSubReddit}<br><br>"
      #strMediaType = request.form.get('mediatype')
      strMediaType = request.form.getlist('mediatype')
      strWebOutput += f"{strMediaType}<br><br>"
   except Exception as e:
      strWebOutput += f"Trouble with gathering form entry for 'sub'. See: {e}<br><br>"
      #return strWebOutput
   else:
      strWebOutput += "gathering form entry for 'sub' complete without error<br><br>"
   finally:
      strWebOutput += "gathering form entry for 'sub completed<br><br>"
   
   
   return strWebOutput

if __name__ == '__main__':
   app.run(debug=True)
