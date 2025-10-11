from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
#import re

# https://www.reddit.com/dev/api/
# POST /api/search_subreddits

def html_crafterror(strCraftSource, strFuncError):
   
   # try...except
   #   or verify variables contain values
   strCraftError = f"An unexpected error occurred in <b><u>REDDITMEDIA</u></b> during action [ <b><u>{strCraftSource}</u></b> ]: <font color=red>{strFuncError}</font><br><br>"
   
   return strCraftError
   
def app_dictionary(strDictLabel):
   
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
         strDictValue = "imgdupedetect v0.4 by orbut8888"
      case "html_header":
         strDictValue = "<head>"
         strDictValue += "<title>TechSushi - Portfolio</title>"
         #strDictValue += "<base href=\"https://www.reddit.com/\" target=\"_blank\">"#
         strDictValue += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
         strDictValue += "<meta name=\"description\" content=\"A brief description of my webpage for search engines.\">"
         strDictValue += "</head>"
         strDictValue += "<body>Welcome to the TechSushi - Portfolio page<br><br><br>"
      case "html_footer":
         strDictValue = "Run through version [1.4.0]</body>"
      case _:
         #default unknown
         strDictValue = f"Unrecognized value: [ {strDictLabel} ]"
   
   return strDictValue
   
def kv_set(strSetVault, strSetName, strSetValue):
   
   #Only expected to be used during initial Reddit API and Azure KeyVault set up
   #From the Azure WebApp, ensure you have enabled System Identity (WebApp > Settings > Identity > On > Save)
   #From the Azure KeyVault, ensure you assign (Key Vault Secrets Officer?) role to the Azure WebApp identity named above
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strSetVault}.vault.azure.net/", credential=credential) #kv-techsushi-site
      secret = secret_client.set_secret(strSetName, strSetValue) #api-reddit-id
   except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = html_crafterror("KV_SET", e)
      return strSetOutput
   
   return
   
def kv_get(strGetVault, strGetName):
   
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url=f"https://{strGetVault}.vault.azure.net/", credential=credential)
      secret = secret_client.get_secret(strGetName)
      strGetValue = secret.value
   except Exception as e:
      #could contain sensitive information in error message
      strGetValue = html_crafterror("KV_GET", e)
      return strGetValue
      
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

def reddit_getjson(strGjSubReddit, lstGjMediaType, strGjSort, strGjTokenType, strGjToken, strGjURL):

   #add params for:
   # result count (display limit) - this likely belongs in jsontohtml function
   # list view / gallery view
   # over_18 flag
   #   AFTER attribute? could be built into strURL when passed or have seperate function that accepts params to craft URLs
   
   #check if subreddit exists
   #handle [], [pictures], [videos], [pictures, videos], (gallery?), (other/unknown)
   #handle new, hot, rising, controversial, top
   #check POST vs GET (request.method ==
   
   try:
      strGjUserAgent = app_dictionary("txt_useragent")
      dictGjHeader = { "Authorization": f"{strGjTokenType} {strGjToken}", "User-Agent": strGjUserAgent }
      
      roGjReceived = requests.get(strGjURL, headers=dictGjHeader)
      
      strGjReqStatus = roGjReceived.status_code
      match strGjReqStatus:
         case "403":
            strGjJsonOutput = html_crafterror("GETJSON", f"Unable to proceed!<br>Status Code: {strGjReqStatus}<br>Token type: {strGjTokenType}")
            #unsure why RAISE does not work as expected
            #raise RuntimeError(strJsonOutput)
            return strGjJsonOutput
         case _:
            dictGjJson = roGjReceived.json()
      if not dictGjJson:
         strGjJsonOutput = html_crafterror("GETJSON", f"JSON response is null!<br>Status Code: {strGjReqStatus}<br>Token type: {strGjTokenType}")
         return strGjJsonOutput
      
   except Exception as e:
      #could contain sensitive information in error message
      strGjJsonOutput = html_crafterror("GETJSON", f"{e}<br>URL: {strGjURL}<br>Status Code: {strGjReqStatus}<br>Token type: {strGjTokenType}")
      return strGjJsonOutput

   return dictGjJson

def reddit_jsontohtml(jsonHtmlContent, lstHtmlMediaType):
   
   #consider [], [images], [videos], [images, videos], (other/unknown)
   #consider new, hot, rising, controversial, top
   #consider table view for alignment

   try:
      if not jsonHtmlContent:
         strHtmlOutput = html_crafterror("JSONtoHTML", f"JSON response provided is null!")
         return strHtmlOutput
      
      
      '''
      #perhaps handle AFTER crafting in a separate function after this function
      #   how to handle or what to expect from strDestURL here then?
      strAfterURL = jsonContent["data"]["after"]
      if not strAfterURL:
         strAfterURL = ""
      else:
         strAfterURL = f"&after={strAfterURL}"
         strDestURL += strAfterURL
      '''
      
      
      
      dictHtmlThreads = jsonHtmlContent["data"]["children"]
      
      strHtmlOutput = "<br>"
      
      for dictHtmlSingle in dictHtmlThreads:
         strSubRed = dictHtmlSingle["data"]["subreddit"]
         strThreadTitle = dictHtmlSingle["data"]["title"]
         strThreadAuthor = dictHtmlSingle["data"]["author"]
         strThreadPermalink = dictHtmlSingle["data"]["permalink"]
         strThreadComments = dictHtmlSingle["data"]["num_comments"]
         strThreadURL = dictHtmlSingle["data"]["url"]
         strThreadMedia = dictHtmlSingle["data"]["media"]
         strThreadType = dictHtmlSingle.get("data", {}).get("post_hint", "Missing")
         
         #"over_18": false
         #is_gallery
         
         strHtmlThreadOutput = f"<font size=5><a href=\"https://www.reddit.com{strThreadPermalink}\">{strThreadTitle}</a></font><br>"
         #regex work in progress
         #strSubRedLink = strDestURL
         #"https://www.reddit.com/user/epicap232/submitted/"
         #/r/u_ExampleUser/new
         #   there is likely a different link for POSTED BY vs u_(user) sub
         #      need to explore this
         strHtmlAuthorLink = f"./redmedia?sub=u_{strThreadAuthor}"
         #strHtmlThreadOutput += f"<a href=\"{strSubRedLink}\">r/{strSubRed}</a> - <a href=\"{strAuthorLink}\"><b>{strThreadAuthor}</b></a> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
         strHtmlThreadOutput += f"<a href=\"./redmedia?sub={strSubRed}\">r/{strSubRed}</a> - <a href=\"{strHtmlAuthorLink}\"><b>{strThreadAuthor}</b></a> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
         
         #ThreadType : link, image, hosted:video, null, (gallery?)
         match strThreadType:
            case "image":
               strHtmlThreadOutput += f"<a href=\"{strThreadURL}\" target=\"_blank\"><img src =\"{strThreadURL}\" width=\"60%\"></img></a><p>"
            case "rich:video":
               strHtmlThreadEmbed = strThreadMedia["oembed"]["html"]
               strHtmlThreadEmbed = strHtmlThreadEmbed.replace("&lt;","<")
               strHtmlThreadEmbed = strHtmlThreadEmbed.replace("&gt;",">")
               strHtmlThreadEmbed = strHtmlThreadEmbed.replace("\"100%\"","\"60%\"")
               strHtmlThreadEmbed = strHtmlThreadEmbed.replace("position:absolute;","")
               strHtmlThreadOutput += f"{strHtmlThreadEmbed}<br><p>"
            case "hosted:video":   
               #*********
               strHtmlThreadOutput = ""
               #strHostedVid = dictSingle["data"]["secure_media"]["fallback_url"]
               #*********
            #case "link":
               #strHtmlThreadOutput = ""
            #"is_video": true
            #"is_gallery": true
            case _:
               #strHtmlThreadOutput += f"<font color=red>unexpected MediaType experienced [ {strThreadType} ]</font><p>"
               strHtmlThreadOutput = ""
         strHtmlOutput += strHtmlThreadOutput
         
      '''
      # consider moving this addition outside of the function
      #   some cases may require running this function multiple times to meet Display Limit setting
      strHtmlOutput += f"<p align=\"right\"><a href=\"{strHtmlDestURL}\">Next Posts</a></p>"
      '''

   except Exception as e:
      #could contain sensitive information in error message
      #strHtmlOutput = f"Trouble with <b>JSONtoHTML</b>, review: {e}<br><br>{dictThreads}<br><br>"
      #strHtmlOutput = html_crafterror("JSONtoHTML", f"{e}<br>URL: {strGjURL}<br>Status Code: {strGjReqStatus}<br>Token type: {strGjTokenType}")
      strHtmlOutput = html_crafterror("JSONtoHTML", e)
      return strHtmlOutput

   return strHtmlOutput

def html_crafturl(strSub, strSort, lstMediaType, strAfter, strLimit):

   # add a parameter for URL base
   #   may be able to use this function for reddit api calls
   #   AND local URL format

   strBase = redditmedia.app_dictionary("url_oauth")
   strBase += f"{strSub}/{strSort}?"
   if lstMediaType:
      strBase += ""
   if strAfter:
      strBase += f"after={strAfter}"
   if strLimit:
      strBase += ""
   
   '''
    strURL += f"{strSubReddit}"
      strURL += "/"
      strURL += f"{strSort}"
      #determine ? versus &
      if strAfter:
         strURL += f"?after={strAfter}"
   '''

   # need to add parameter to return
   
   return

def html_form(strFormDestination, strFormSub="all", intFormLimit=10, strSortBy="new", strView="list", bolNSFW=True):
   #need to add input for mediatype in parameters above
   # intFormLimit = minimum number of media items to return
   #   not related to results requested from single API call
   
   #possible additions
   # option to hide header lines (image only)   
   strFormOutput = f"<form action=\"/{strFormDestination}\" method=\"post\"><!-- Form elements go here -->"
   strFormOutput += f"<label for=\"name\">Subreddit: </label><input type=\"text\" id=\"subreddit\" name=\"sub\" placeholder=\"{strFormSub}\" autocomplete=\"off\">"
   strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\" checked><label for=\"images\" disabled>Images</label>"
   strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\" checked><label for=\"videos\" disabled>Videos</label>"
   strFormOutput += f"<br><br>"
   strFormOutput += f"<label for=\"count\">Result Count: </label><input type=\"text\" id=\"count\" name=\"count\" placeholder=\"{intFormLimit}\" autocomplete=\"off\" disabled>"
   strFormOutput += f"<label for=\"sort\"> Sort by: </label><select id=\"sort\" name=\"sort\" disabled>"
   strFormOutput += f"<option value=\"new\" selected=\"true\">New</option>"
   strFormOutput += f"<option value=\"hot\">Hot</option>"
   strFormOutput += f"<option value=\"rising\">Rising</option>"
   strFormOutput += f"<option value=\"controversial\">Controversial</option>"
   strFormOutput += f"<option value=\"top\">Top</option>"
   #strFormOutput += f"<option value=\"random\">Random</option>" #invalid option
   strFormOutput += f"</select>"
   strFormOutput += f"<br><br>"
   strFormOutput += f"<input type=\"radio\" id=\"list\" name=\"view\" value=\"list\" checked disabled><label for=\"list\">List View</label>"
   strFormOutput += f"<input type=\"radio\" id=\"gallery\" name=\"view\" value=\"gallery\" disabled><label for=\"gallery\">Gallery View</label>"
   strFormOutput += f"<input type=\"checkbox\" id=\"nsfw\" name=\"nsfw\" value=\"nsfw\" checked disabled><label for=\"nsfw\">Over_18?</label><br>"
   strFormOutput += f"<br><br>"
   strFormOutput += f"<button type=\"submit\">Browse Media</button>"
   strFormOutput += f"<input type=\"checkbox\" id=\"human\" name=\"human\" value=\"human\" required><label for=\"human\">Are you human?</label>"
   strFormOutput += f"</form><br><br>"

   #   need to add HUMAN? style checkbox here, required before allowing submit, bot stopper-ish
   #      also likely do not want to show results and "next" link on first load - bot could continue w/o human checkbox
   
   #add (media by) username
   #consider single stream vs gallery view
  
   return strFormOutput
