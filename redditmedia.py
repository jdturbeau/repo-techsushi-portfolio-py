from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def app_dictionary(strLabel):
   match strLabel:
      case "kv_name":
         strValue = "kv-techsushi-site"
      case "kv_token":
         strValue = "api-reddit-token"
      case "kv_tokentype":
         strValue = "api-reddit-tokentype"
      case "kv_id":
         strValue = "api-reddit-id"
      case "kv_secret":
         strValue = "api-reddit-secret"
      case "url_login":
         strValue = "https://www.reddit.com/api/v1/access_token"
      case "url_oauth":
         strValue = "https://oauth.reddit.com/r/" #{strSubReddit}/new
      case "txt_useragent":
         strValue = "imgdupedetect v0.2 by orbut8888"
      case "html_header":
         strValue = "<head>"
         strValue += "<title>TechSushi - Portfolio</title>"
         strValue += "</head>"
         strValue += "<body>Welcome to the TechSushi - Portfolio page<br><br><br>"
      case "html_footer":
         strValue = "Run through version [1.0.8]</body>"
      case _:
         #default unknown
         strValue = f"Unrecognized value: [ {strLabel} ]"
   
   return strValue
   
def kv_set(strVault, strName, strValue):
   #Only expected to be used during initial Reddit API and Azure KeyVault set up
   #From the Azure WebApp, ensure you have enabled System Identity (WebApp > Settings > Identity > On > Save)
   #From the Azure KeyVault, ensure you assign (Key Vault Secrets Officer?) role to the Azure WebApp identity named above
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strVault}.vault.azure.net/", credential=credential) #kv-techsushi-site
      secret = secret_client.set_secret(strName, strValue) #api-reddit-id
   except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>SET</b>: {e}<br><br>"
      #raise strSetOutput
      return strSetOutput
   #else:
      #strSetOutput = "<b>SET</b> completed successfully<br><br>"
   #finally:
      #strSetOutput = "end of <b>SET</b> script<br><br>"      
   return
   
def kv_get(strVault, strName):
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strVault}.vault.azure.net/", credential=credential)
      secret = secret_client.get_secret(strName)
      strValue = secret.value
      #strGetOutput += f"{secret.name}<br><br>"
      #strGetOutput += f"{secret.value}<br><br>"
   except Exception as e:
      strGetOutput = f"an unexpected error occurred during <b>GET</b>: {e}<br><br>"
      #raise strGetOutput
      return strGetOutput
   #else:
      #strGetOutput = "<b>GET</b> completed successfully<br><br>"
   #finally:
      #strGetOutput = "end of <b>GET</b> script<br><br>"
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
      strUserAgent = app_dictionary("txt_useragent")
      dictHeader = { "User-Agent": strUserAgent }
      roReceived = requests.post(strRedditURL, auth=objClientAuth, data=dictPostData, headers=dictHeader)
      
      #strRefreshOutput += f"{roReceived.status_code}<br><br>{roReceived.text}<br><br>{roReceived.content}<br><br>{roReceived.headers}<br><br>"
      #strRefreshOutput += f"Attempting to parse response for JSON...<br><br>"
      dictReceived = roReceived.json()      
      strToken = dictReceived["access_token"]
      strTokenType = dictReceived["token_type"]
      #strRefreshOutput += f"Attempting to store token...<br><br>"
      kv_set(strVault, "api-reddit-token", strToken)
      kv_set(strVault, "api-reddit-tokentype", strTokenType)
      
      #strRefreshOutput += f"new token stored!<br><br>{strToken}<br><br>{strTokenType}<br><br>"
   except Exception as e:
      #could contain sensitive information in error message
      strRefreshOutput = f"Trouble with <b>REFRESH</b>, review {e}<br><br>{roReceived}<br><br>"
      #raise strRefreshOutput
      return strRefreshOutput
   #else:
      #strRefreshOutput = f"<b>REFRESH</b> complete successfully"
   #finally:
      #strRefreshOutput = f"<b>REFRESH</b> complete"
      
   return

def reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL, strAfter):
   #handle [], [pictures], [videos], [pictures, videos], (gallery?), (other/unknown)
   #handle new, hot, rising, controversial, top
   #check POST vs GET (request.method ==

   try:
      #strTokenType = kv_get(strVault, "api-reddit-tokentype")
      #strToken = kv_get(strVault, "api-reddit-token")
      strUserAgent = app_dictionary("txt_useragent")
      dictHeader = { "Authorization": f"{strTokenType} {strToken}", "User-Agent": strUserAgent }
      #how to handle 'after' here?
      
      roReceived = requests.get(strURL, headers=dictHeader)
      strReqStatus = roReceived.status_code
      match strReqStatus:
         case "403":
            strJsonOutput = f"<b>GETJSON</b>, status code: [ {roReceived.status_code} ]<br>Token type [ {strTokenType} ]<br> Unable to proceed!<br>"
            raise RuntimeError(strJsonOutput)
         case _:
            dictJson = roReceived.json()
            
   except Exception as e:
      #could contain sensitive information in error message
      strJsonOutput = f"Trouble with <b>GETJSON</b>, status code: {roReceived.status_code}<br> review: {e}<br><br>"
      #raise strWebOutput
      return strJsonOutput
   #else:
      #strJsonOutput = f"<b>GETJSON</b> complete successfully"
   #finally:
      #strJsonOutput = f"<b>GETJSON</b> complete"
      
   return dictJson

def reddit_jsontohtml(jsonContent, lstMediaType, strDestURL):
   #consider [], [pictures], [videos], [pictures, videos], (other/unknown)
   #consider new, hot, rising, controversial, top
   #consider table view for alignment

   try:
      strAfterURL = jsonContent["data"]["after"]
      if not strAfterURL:
         strAfterURL = ""
      else:
         strAfterURL = f"&after={strAfterURL}"
         
      dictThreads = jsonContent["data"]["children"]
      
      #strHtmlOutput = f"<head><base href=\"https://www.reddit.com/\" target=\"_blank\"></head><body>"
      strHtmlOutput = "<br>"
      
      for dictSingle in dictThreads:
         strThreadTitle = dictSingle["data"]["title"]
         strThreadAuthor = dictSingle["data"]["author"]
         strThreadPermalink = dictSingle["data"]["permalink"]
         strThreadComments = dictSingle["data"]["num_comments"]
         strThreadURL = dictSingle["data"]["url"]
         strThreadMedia = dictSingle["data"]["media"]
         strThreadType = dictSingle.get("data", {}).get("post_hint", "Missing")
         
         strHtmlOutput += f"<font size=5><a href=\"{strThreadPermalink}\">{strThreadTitle}</a></font><br>"
         strHtmlOutput += f"<b>{strThreadAuthor}</b> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
         
         #ThreadType : link, image, hosted:video, null, (gallery?)
         match strThreadType:
            case "image":
               strHtmlOutput += f"<img src =\"{strThreadURL}\" width=\"60%\"></img><p>"
            case "rich:video":
               strThreadEmbed = strThreadMedia["oembed"]["html"]
               strThreadEmbed = strThreadEmbed.replace("&lt;","<")
               strThreadEmbed = strThreadEmbed.replace("&gt;",">")
               strThreadEmbed = strThreadEmbed.replace("\"100%\"","\"60%\"")
               strThreadEmbed = strThreadEmbed.replace("position:absolute;","")
               strHtmlOutput += f"{strThreadEmbed}<br><p>"
            #is_gallery: true
            #hosted:video
            #link
            case _:
               strHtmlOutput += f"<font color=red>Error experienced [ {strThreadType} ]</font><p>"
         
         #{strDestURL} & after={strAfterURL}
         strHtmlOutput += f"<p><a href=\"{strDestURL}&{strAfterURL}\">Next Posts</a></p>"

   except Exception as e:
      #could contain sensitive information in error message
      strHtmlOutput = f"Trouble with <b>JSONtoHTML</b>, review: {e}<br><br>{dictThreads}<br><br>"
      return strHtmlOutput
   #else:
      #strWebOutput += "<b>JSONtoHTML</b> completed successfully<br><br>"
   #finally:
      #strWebOutput += "<b>JSONtoHTML</b> completed<br><br>"

   return strHtmlOutput

def html_form(strDestination):
   
   strFormOutput = f"<form action=\"/{strDestination}\" method=\"post\"><!-- Form elements go here -->"
   strFormOutput += f"<label for=\"name\">Subreddit:</label><br><input type=\"text\" id=\"subreddit\" name=\"sub\" placeholder=\"all\" autocomplete=\"off\"><br><br>"
   strFormOutput += f"<label for=\"mediatype\">Type of Media:</label><br><input type=\"checkbox\" id=\"pictures\" name=\"mediatype\" value=\"pictures\" checked><label for=\"pictures\">Pictures</label>"
   strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\"><label for=\"videos\">Videos</label><br><br>"
   #add new, hot, rising, controversial, top
   strFormOutput += f"<label for=\"sort\">Choose Sort Order:</label><br>"
   strFormOutput += f"<select id=\"sort\" name=\"sort\">"
   strFormOutput += f"<option value=\"new\" selected=\"true\">New</option>"
   strFormOutput += f"<option value=\"hot\">Hot</option>"
   strFormOutput += f"<option value=\"rising\">Rising</option>"
   strFormOutput += f"<option value=\"controversial\">Controversial</option>"
   strFormOutput += f"<option value=\"top\">Top</option>"
   strFormOutput += f"</select><br><br>"
   strFormOutput += f"<button type=\"submit\">Browse Media</button></form><br><br>"
   #add (media by) username
   #consider single stream vs gallery view

   #strAfterURL = dictJson["data"]["after"]
   
   return strFormOutput

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
      strWebOutput += f"{strSubReddit}<br><br>"
      strMediaType = request.form.getlist('mediatype')
      strWebOutput += f"{strMediaType}<br><br>"
   except Exception as e:
      strWebOutput += f"Trouble with <b>RETRIEVING FORM ENTRY</b> for 'sub'. See: {e}<br><br>"
      #return strWebOutput
   else:
      strWebOutput += "<b>RETRIEVING FORM ENTRY</b> for 'sub' completed successfully<br><br>"
   finally:
      strWebOutput += "<b>RETRIEVING FORM ENTRY</b> for 'sub completed<br><br>"
   
   return strWebOutput
