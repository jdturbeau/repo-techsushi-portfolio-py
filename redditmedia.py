from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import re

# https://www.reddit.com/dev/api/
# POST /api/search_subreddits

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
         #to capture user data, may need to move the /r/ out
         # /user/username/submitted
         strValue = "https://oauth.reddit.com/r/"
      case "txt_useragent":
         strValue = "imgdupedetect v0.3 by orbut8888"
      case "html_header":
         strValue = "<head>"
         strValue += "<title>TechSushi - Portfolio</title>"
         #strValue += "<base href=\"https://www.reddit.com/\" target=\"_blank\">"#
         strValue += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
         strValue += "<meta name=\"description\" content=\"A brief description of my webpage for search engines.\">"
         strValue += "</head>"
         strValue += "<body>Welcome to the TechSushi - Portfolio page<br><br><br>"
      case "html_footer":
         strValue = "Run through version [1.2.0]</body>"
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
   
   return
   
def kv_get(strVault, strName):
   
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strVault}.vault.azure.net/", credential=credential)
      secret = secret_client.get_secret(strName)
      strValue = secret.value
   except Exception as e:
      strGetOutput = f"an unexpected error occurred during <b>GET</b>: {e}<br><br>"
      #raise strGetOutput
      return strGetOutput

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
      
   return

def reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL):
   
   #check if subreddit exists
   #handle [], [pictures], [videos], [pictures, videos], (gallery?), (other/unknown)
   #handle new, hot, rising, controversial, top
   #check POST vs GET (request.method ==
   
   try:
      strUserAgent = app_dictionary("txt_useragent")
      dictHeader = { "Authorization": f"{strTokenType} {strToken}", "User-Agent": strUserAgent }
      
      roReceived = requests.get(strURL, headers=dictHeader)
      
      strReqStatus = roReceived.status_code
      match strReqStatus:
         case "403":
            strJsonOutput = f"<b>GETJSON</b>, status code: [ {roReceived.status_code} ]<br>Token type [ {strTokenType} ]<br> Unable to proceed!<br>"
            #unsure why RAISE does not work as expected
            #raise RuntimeError(strJsonOutput)
            return strJsonOutput
         case _:
            dictJson = roReceived.json()
      if not dictJson:
         strJsonOutput = f"JSON response is null. status code: [ {roReceived.status_code} ]<br>Token type [ {strTokenType} ]<br> Unable to proceed!<br>"
         return strJsonOutput
      
   except Exception as e:
      #could contain sensitive information in error message
      strJsonOutput = f"Trouble with <b>GETJSON</b>, status code: {roReceived.status_code}<br> review: {e}<br>URL [ {strURL} ]<br>Token Type [ {strTokenType} ]<br><br>"
      return strJsonOutput

   return dictJson

def reddit_jsontohtml(jsonContent, lstMediaType, strDestURL):
   
   #consider [], [images], [videos], [images, videos], (other/unknown)
   #consider new, hot, rising, controversial, top
   #consider table view for alignment

   try:
      if not jsonContent:
         strHtmlOutput = "Error: JSON provided is empty/null!"
         return strHtmlOutput
      strAfterURL = jsonContent["data"]["after"]
      if not strAfterURL:
         strAfterURL = ""
      else:
         strAfterURL = f"&after={strAfterURL}"
         strDestURL += strAfterURL
         
      dictThreads = jsonContent["data"]["children"]
      
      strHtmlOutput = "<br>"
      
      for dictSingle in dictThreads:
         strSubRed = dictSingle["data"]["subreddit"]
         strThreadTitle = dictSingle["data"]["title"]
         strThreadAuthor = dictSingle["data"]["author"]
         strThreadPermalink = dictSingle["data"]["permalink"]
         strThreadComments = dictSingle["data"]["num_comments"]
         strThreadURL = dictSingle["data"]["url"]
         strThreadMedia = dictSingle["data"]["media"]
         strThreadType = dictSingle.get("data", {}).get("post_hint", "Missing")
         
         #"over_18": false
         #is_gallery
         
         strThreadOutput = f"<font size=5><a href=\"https://www.reddit.com/{strThreadPermalink}\">{strThreadTitle}</a></font><br>"
         #regex work in progress
         strSubRedLink = strDestURL
         #"https://www.reddit.com/user/epicap232/submitted/"
         #/r/u_ExampleUser/new
         strAuthorLink = f"./redmedia?sub=u_{strThreadAuthor}"
         strThreadOutput += f"<a href=\"{strSubRedLink}\">r/{strSubRed}</a> - <a href=\"{strAuthorLink}\"><b>{strThreadAuthor}</b></a> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
         
         #ThreadType : link, image, hosted:video, null, (gallery?)
         match strThreadType:
            case "image":
               strThreadOutput += f"<a href=\"{strThreadURL}\" target=\"_blank\"><img src =\"{strThreadURL}\" width=\"60%\"></img></a><p>"
            case "rich:video":
               strThreadEmbed = strThreadMedia["oembed"]["html"]
               strThreadEmbed = strThreadEmbed.replace("&lt;","<")
               strThreadEmbed = strThreadEmbed.replace("&gt;",">")
               strThreadEmbed = strThreadEmbed.replace("\"100%\"","\"60%\"")
               strThreadEmbed = strThreadEmbed.replace("position:absolute;","")
               strThreadOutput += f"{strThreadEmbed}<br><p>"
            case "hosted:video":   
               #*********
               strThreadOutput = ""
               #strHostedVid = dictSingle["data"]["secure_media"]["fallback_url"]
               #*********
               #strThreadEmbed = strThreadMedia["oembed"]["html"]
               #strThreadEmbed = strThreadEmbed.replace("&lt;","<")
               #strThreadEmbed = strThreadEmbed.replace("&gt;",">")
               #strThreadEmbed = strThreadEmbed.replace("\"100%\"","\"60%\"")
               #strThreadEmbed = strThreadEmbed.replace("position:absolute;","")
               #strThreadOutput += f"{strThreadEmbed}<br><p>"
            #case "link":
               #strThreadOutput = ""
            #"is_video": true
            #"is_gallery": true
            case _:
               #strThreadOutput += f"<font color=red>unexpected MediaType experienced [ {strThreadType} ]</font><p>"
               strThreadOutput = ""
         strHtmlOutput += strThreadOutput
         
      strHtmlOutput += f"<p align=\"right\"><a href=\"{strDestURL}\">Next Posts</a></p>"

   except Exception as e:
      #could contain sensitive information in error message
      strHtmlOutput = f"Trouble with <b>JSONtoHTML</b>, review: {e}<br><br>{dictThreads}<br><br>"
      return strHtmlOutput

   return strHtmlOutput

def html_form(strDestination):
   
   #possible additions
   # option to hide header lines (image only)   
   strFormOutput = f"<form action=\"/{strDestination}\" method=\"post\"><!-- Form elements go here -->"
   strFormOutput += f"<label for=\"name\">Subreddit: </label><input type=\"text\" id=\"subreddit\" name=\"sub\" placeholder=\"all\" autocomplete=\"off\">"
   strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\" checked><label for=\"images\">Images</label>"
   strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\" checked><label for=\"videos\">Videos</label>"
   strFormOutput += f"<br><br>"
   strFormOutput += f"<label for=\"sort\">Sort by: </label><select id=\"sort\" name=\"sort\" disabled>"
   strFormOutput += f"<option value=\"new\" selected=\"true\">New</option>"
   strFormOutput += f"<option value=\"hot\">Hot</option>"
   strFormOutput += f"<option value=\"rising\">Rising</option>"
   strFormOutput += f"<option value=\"controversial\">Controversial</option>"
   strFormOutput += f"<option value=\"top\">Top</option>"
   #strFormOutput += f"<option value=\"random\">Random</option>" #invalid option
   strFormOutput += f"</select>"
   strFormOutput += f"<label for=\"count\"> Result Count: </label><input type=\"text\" id=\"count\" name=\"count\" placeholder=\"10\" autocomplete=\"off\" disabled>"
   strFormOutput += f"<br><br>"
   strFormOutput += f"<input type=\"radio\" id=\"list\" name=\"view\" value=\"list\" checked><label for=\"list\">List View</label>"
   strFormOutput += f"<input type=\"radio\" id=\"gallery\" name=\"view\" value=\"gallery\" disabled><label for=\"gallery\">Gallery View</label>"
   strFormOutput += f"<input type=\"checkbox\" id=\"nsfw\" name=\"nsfw\" value=\"nsfw\" disabled><label for=\"nsfw\">Allow over_18 flag?</label>"
   strFormOutput += f"<br><br>"
   strFormOutput += f"<button type=\"submit\">Browse Media</button></form><br><br>"
   #add (media by) username
   #consider single stream vs gallery view
  
   return strFormOutput
