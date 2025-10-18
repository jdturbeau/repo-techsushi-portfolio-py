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
        # to retrieve or refresh access token
        strDictValue = "https://www.reddit.com/api/v1/access_token"
      case "url_oauth":
        # to retrieve subreddit data
        # to capture user data, may need to move the /r/ out
        #   /user/username/submitted
        strDictValue = "https://oauth.reddit.com/r/"
      case "url_appbase":
        strDictValue = "rmrresults"
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
      case "app_defaultparams":  
        # technically should be dictDictValue
        #   reddit_getjson(strGjSubReddit, lstGjMediaType, intGjLimit, strGjSort, strGjView, bolGjNSFW, strAfter, strGjTokenType, strGjToken, strGjURL):
        strDictValue = { 
          "sub": "all",
          "mediatype": "iv",
          "limit": 10,
          "sort": "new",
          "view": "list",
          "nsfw": True,
          "after": "",
        }        
      case _:
        #default unknown
        strDictValue = f"Unrecognized value: [ {strDictAttrib} ]"
      
  except Exception as e:
    #could contain sensitive information in error message
    strDictError = html_crafterror("REDDIT_MEDIA", "APP_DICTIONARY", e)
    return strDictError

  return strDictValue

def kv_set(strSetName, strSetValue):
   
   # Only expected to be used during initial Reddit API and Azure KeyVault set up
   #  From the Azure WebApp, ensure you have enabled System Identity (WebApp > Settings > Identity > On > Save)
   #  From the Azure KeyVault, ensure you assign (Key Vault Secrets Officer?) role to the Azure WebApp identity named above
  
  try:
    # could add vault as a param
    #   though objective is to be self contained and leverage app_dictionary
    strSetVault = app_dictionary("kv_name")
    
    objSetCredential = DefaultAzureCredential()
    objSetSecretClient = SecretClient(vault_url=f"https://{strSetVault}.vault.azure.net/", credential=objSetCredential) #kv-techsushi-site
    objSetSecret = objSetSecretClient.set_secret(strSetName, strSetValue) #api-reddit-id
  
  except Exception as e:
    #could contain sensitive information in error message
    strSetError = html_crafterror("REDDIT_MEDIA", "KV_SET", e)
    return strSetError
    
  # No value returned... necessary?
  
  return

def kv_get(strGetName):

  try:
    # could add vault as a param
    #   though objective is to be self contained and leverage app_dictionary
    strGetVault = app_dictionary("kv_name")
    
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
    # could add vault as a param
    #   though objective is to be self contained and leverage app_dictionary
    #   vault name retrieved in get / set functions
    
    strRefIDLabel = app_dictionary("kv_id")
    strRefID = kv_get(strRefIDLabel)
    strRefSecretLabel = app_dictionary("kv_secret")
    strRefSecret = kv_get(strRefSecretLabel)
    
    objRefClientAuth = (strRefID, strRefSecret)
    dictRefPostData = { "grant_type": "client_credentials" }
    strRefUserAgent = app_dictionary("txt_useragent")
    dictRefHeader = { "User-Agent": strRefUserAgent }

    strRefRedditURL = app_dictionary("url_login")
    
    roRefReceived = requests.post(strRefRedditURL, auth=objRefClientAuth, data=dictRefPostData, headers=dictRefHeader)
    
    dictRefReceived = roRefReceived.json()      
    strRefToken = dictRefReceived["access_token"]
    strRefTokenType = dictRefReceived["token_type"]
    
    strRefTokenLabel = app_dictionary("kv_token")
    kv_set(strRefTokenLabel, strRefToken)
    strRefTokenTypeLabel = app_dictionary("kv_tokentype")
    kv_set(strRefTokenTypeLabel, strRefTokenType)
  
  except Exception as e:
    # could contain sensitive information in error message
    strRefError = html_crafterror("REDDIT_MEDIA", "KV_REFRESHTOKEN", e)  # f"{e}<br><br>{roRefReceived}<br><br>")
    return strRefError
  
  # No value returned... necessary?
  
  return

def reddit_jsontohtml(jsonHtmlContent, dictHtmlParams):
  
  # strHtmlBaseDestURL - local app destination for links
  # reddit_getjson(strGjSubReddit, lstGjMediaType, intGjLimit, strGjSort, strGjView, bolGjNSFW, strAfter, strGjTokenType, strGjToken, strGjURL):
  
  # consider [], [images], [videos], [images, videos], (other/unknown)
  # consider new, hot, rising, controversial, top
  # consider table view for alignment
  #    "sub": "all",
  #     "mediatype": "iv",
  #     "limit": 10,
  #     "sort": "new",
  #     "view": "list",
  #     "nsfw": True,
  #     "after": "",
  
  try:
    
    # Check if json looks like empty response or subreddit invalid 
    if not 'jsonHtmlContent' in locals():
      strHtmlError = html_crafterror("REDDIT_MEDIA", "JSONtoHTML", f"JSON response provided is null!")
      return strHtmlError
    
    intHtmlResults = int(jsonHtmlContent["data"]["dist"])
    if not 'intHtmlResults' in locals():
      strHtmlError = html_crafterror("REDDIT_MEDIA", "JSONtoHTML", f"No results founud. JSON response provided is null!")
      return strHtmlError
    
    if intHtmlResults == 0:
      strHtmlError = html_crafterror("REDDIT_MEDIA", "JSONtoHTML", f"0 results returned. No further results returned or subreddit may not exist!")
      # provide a refresh from beginning link here
      #    in some cases after 5-6 api calls into NEW, no additional results are returned
      return strHtmlError
    
    strHtmlBaseDestURL = app_dictionary("url_appbase")
    strHtmlMediaType = dictHtmlParams["mediatype"] 
    dictHtmlThreads = jsonHtmlContent["data"]["children"]
    # should not need to confirm variables exist or are populated here - three if conditions above should cover
    
    strHtmlOutput = "<br>"
    
    for dictHtmlSingle in dictHtmlThreads:
      strSubRed = dictHtmlSingle["data"]["subreddit"]
      strThreadTitle = dictHtmlSingle["data"]["title"]
      strThreadAuthor = dictHtmlSingle["data"]["author"]
      strThreadPermalink = dictHtmlSingle["data"]["permalink"]
      strThreadComments = dictHtmlSingle["data"]["num_comments"]
      strThreadURL = dictHtmlSingle["data"]["url"]
      strThreadMedia = dictHtmlSingle["data"]["media"]
      strThreadType = dictHtmlSingle.get("data", {}).get("post_hint", "missing")
      bolThreadNsfw = dictHtmlSingle["data"]["over_18"]
      dtThreadUTC = dictHtmlSingle["data"]["created_utc"]
      
      #"over_18": false
      #is_gallery
      
      strHtmlThreadOutput = f"<font size=5><a href=\"https://www.reddit.com{strThreadPermalink}\">{strThreadTitle}</a></font><br>"
      
      strHtmlAuthorLink = f"./{strHtmlBaseDestURL}?sub=u_{strThreadAuthor}"
      strHtmlThreadOutput += f"<a href=\"./{strHtmlBaseDestURL}?sub={strSubRed}\">r/{strSubRed}</a> - <a href=\"{strHtmlAuthorLink}\"><b>{strThreadAuthor}</b></a> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
      
      #ThreadType : link, image, hosted:video, null, (gallery?)
      match strThreadType:
        case "image":
          strHtmlThreadOutput += f"<a href=\"{strThreadURL}\" target=\"_blank\"><img src=\"{strThreadURL}\" width=\"60%\"></img></a><p>"
          case "rich:video":
          strHtmlThreadEmbed = strThreadMedia["oembed"]["html"]
          strHtmlThreadEmbed = strHtmlThreadEmbed.replace("&lt;","<")
          strHtmlThreadEmbed = strHtmlThreadEmbed.replace("&gt;",">")
          strHtmlThreadEmbed = strHtmlThreadEmbed.replace("\"100%\"","\"60%\"")
          strHtmlThreadEmbed = strHtmlThreadEmbed.replace("position:absolute;","")
          strHtmlThreadOutput += f"{strHtmlThreadEmbed}<br><p>"
        case "hosted:video":   
          strHostedVid = dictHtmlSingle["data"]["secure_media"]["reddit_video"]["fallback_url"] # alternatively - strHostedVid = dictHtmlSingle["data"]["media"]["reddit_video"]["fallback_url"]
          #strHtmlThreadOutput += f"<iframe width=\"60%\" src=\"{strHostedVid}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share\" referrerpolicy=\"strict-origin-when-cross-origin\" allowfullscreen title=\"{strThreadTitle}\"></iframe><br><p>"
          strHtmlThreadOutput += f"<iframe src=\"{strHostedVid}\" frameborder=\"0\" allow=\"accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share\" referrerpolicy=\"strict-origin-when-cross-origin\" allowfullscreen title=\"{strThreadTitle}\"></iframe><br><p>"
        #case "link":
          #strHtmlThreadOutput = ""
          #"is_video": true
          #"is_gallery": true
        #case "missing":
        case _:
          #strHtmlThreadOutput += f"<font color=red>unexpected MediaType experienced [ {strThreadType} ]</font><p>"
          strHtmlThreadOutput = ""
      
      # check mediatype param for i and or v to determine if should add to output and count
      
      strHtmlOutput += strHtmlThreadOutput
    
  except Exception as e:
    #could contain sensitive information in error message
    strHtmlError = html_crafterror("REDDIT_MEDIA", "JSONtoHTML", e)
    return strHtmlError
  
  return strHtmlOutput

def html_crafturl(strCraftBaseURL, dictCraftParams):
  
  # historical - dictCraftAttribsstrCraftSub="all", lstCraftMediaType="iv", intCraftLimit=10, strCraftSort="new", strCraftView="list", bolCraftNSFW=True, strCraftAfter="")
  #    "sub": "all",
  #     "mediatype": "iv",
  #     "limit": 10,
  #     "sort": "new",
  #     "view": "list",
  #     "nsfw": True,
  #     "after": "",
  
  # may use this function for reddit api calls AND local URL format

  # could retrieve app_dictionary default settings and substitute any missing values below instead of error

  # check if url passed has parameters already to strip off first
  
  try:
    
    if not 'strCraftBaseURL' in locals():
      strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var strCraftBaseURL does not exist [ {e} ]")
      return strCraftError
    
    strCraftURL = strCraftBaseURL # should end with /
    
    strCraftSub = dictCraftParams["sub"]
    if not 'strCraftSub' in locals():
      strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var strCraftSub does not exist [ {e} ]")
      return strCraftError

    strCraftMediaType = dictCraftParams["mediatype"]
    if not 'strCraftMediaType' in locals():
      strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var strCraftMediaType does not exist [ {e} ]")
      return strCraftError
    
    intCraftLimit = int(dictCraftParams["limit"])
    if not 'intCraftLimit' in locals():
      strCraftError = html_crafterror(""REDDIT_MEDIA", HTML CRAFTURL", f"var intCraftLimit does not exist [ {e} ]")
      return strCraftError

    strCraftSort = dictCraftParams["sort"]
    if not 'strCraftSort' in locals():
      strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var strCraftSort does not exist [ {e} ]")
      return strCraftError

    strCraftView = dictCraftParams["view"]
    if not 'strCraftView' in locals():
      strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var strCraftView does not exist [ {e} ]")
      return strCraftError

    bolCraftNSFW = dictCraftParams["nsfw"]
    if not 'bolCraftNSFW' in locals():
      strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var bolCraftNSFW does not exist [ {e} ]")
      return strCraftError

    strCraftAfter = dictCraftParams["after"]  # this may be blank
    #if not 'strCraftAfter' in locals():
      #strCraftError = html_crafterror("REDDIT_MEDIA", "HTML CRAFTURL", f"var strCraftAfter does not exist [ {e} ]")
      #return strCraftError
    
    strCraftContains = ".reddit.com/"
    if strCraftContains.lower() in strCraftURL.lower():
      
      # oauth or token refresh - can ignore app handled parameters
      if len(strCraftSub) > 0:
        strCraftURL += f"{strCraftSub}/{strCraftSort}"
      else:
        strCraftURL += f"all/{strCraftSort}"
      
      if len(strCraftAfter) > 0:
        strCraftURL += f"?after={strCraftAfter}"
    
    else:
      
      # likely local URL - include app handled parameters
      
      strCraftSuffix = "?"  
      if len(strCraftSub) > 0:
        strCraftSuffix += f"sub={strCraftSub}&"
      else:
        strCraftSuffix += f"sub=all&"
      
      if len(strCraftMediaType) > 0:
        strCraftSuffix += f"mediatype={strCraftMediaType}&"
      
      if intCraftLimit > 0:
        strCraftLimit = str(intCraftLimit)
        strCraftSuffix += f"limit={strCraftLimit}&"
      
      if len(strCraftSort) > 0:
        strCraftSuffix += f"sort={strCraftSort}&"
      
      if len(strCraftView) > 0:
        strCraftSuffix += f"view={strCraftView}&"
      
      if bolCraftNSFW:
        strCraftSuffix += f"nsfw=True&"
      else:
        strCraftSuffix += f"nsfw=False&"
      
      if len(strCraftAfter) > 0:
        strCraftSuffix += f"after={strCraftAfter}"
    
    #check if last character is ampersand
    if strCraftSuffix[-1] == "&":
      strCraftSuffix = strCraftSuffix[:-1]
    if len(strCraftSuffix) > 0:
      strCraftURL += strCraftSuffix
  
  except Exception as e:
    #could contain sensitive information in error message 
    strCraftError = html_crafterror("REDDIT_MEDIA", "HTML_CRAFTURL", e)
    return strCraftError
  
  return strCraftURL

def html_parseurl(strPuURL):
  
  #
  # try...except loop here
  #
  
  # input - URL
  # output - dictionary with named parameters
  
  return

# ***************************************
#  successful review above. continue below... 2025-1018
# ***************************************

def html_form(dictFormParams):
  #historical - strFormDestination, strFormSub="all", lstFormMediaType="iv", intFormLimit=10, strFormSort="new", strFormView="list", bolFormNSFW=True):
   
   # add try...except here
   
   # intFormLimit = minimum number of media items to return
   #    not related to results requested from single API call
   
   # possible additions
   #    option to hide header lines (image only)   
   strFormOutput = f"<form action=\"/{strFormDestination}\" method=\"post\"><!-- Form elements go here -->"
   #strFormOutput += f"<label for=\"subreddit\">Subreddit: </label><input type=\"text\" id=\"sub\" name=\"subsubreddit\" placeholder=\"{strFormSub}\" autocomplete=\"off\">"
   strFormOutput += f"<label for=\"subreddit\">Subreddit: </label><input type=\"text\" id=\"sub\" name=\"subreddit\" placeholder=\"{strFormSub}\" autocomplete=\"off\">"
   
   # translate
   #    strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\" checked disabled><label for=\"images\">Images</label>"
   #    strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\" checked disabled><label for=\"videos\">Videos</label>"
   match lstFormMediaType:
      case "i":
         strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\" checked><label for=\"images\">Images</label>"
         strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\"><label for=\"videos\">Videos</label>"
      case "v":
         strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\"><label for=\"images\">Images</label>"
         strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\" checked><label for=\"videos\">Videos</label>"
      case _:
         # covers case "iv" and unknowns
         strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\" checked><label for=\"images\">Images</label>"
         strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\" checked><label for=\"videos\">Videos</label>"
         
   strFormOutput += f"<br><br>"
   strFormOutput += f"<label for=\"count\">Minimum Display Limit: </label><input type=\"number\" id=\"limit\" name=\"count\" min=\"1\" max=\"30\" step=\"1\" placeholder=\"{intFormLimit}\" autocomplete=\"off\" disabled>"

   # translate strFormSort into drop down selection
   strFormOutput += f"<label for=\"sort\"> Sort by: </label><select id=\"sort\" name=\"sort\" disabled>"
   strFormOutput += f"<option value=\"new\" selected=\"true\">New</option>"
   strFormOutput += f"<option value=\"hot\">Hot</option>"
   strFormOutput += f"<option value=\"rising\">Rising</option>"
   strFormOutput += f"<option value=\"controversial\">Controversial</option>"
   strFormOutput += f"<option value=\"top\">Top</option>"
   #strFormOutput += f"<option value=\"random\">Random</option>" #invalid option
   strFormOutput += f"</select>"
   strFormOutput += f"<br><br>"
   
   # translate strFormView by checked radio
   strFormOutput += f"<input type=\"radio\" id=\"list\" name=\"view\" value=\"list\" checked disabled><label for=\"list\">List View</label>"
   strFormOutput += f"<input type=\"radio\" id=\"gallery\" name=\"view\" value=\"gallery\" disabled><label for=\"gallery\">Gallery View</label>"

   # translate bolFormNSFW into check
   strFormOutput += f"<input type=\"checkbox\" id=\"nsfw\" name=\"nsfw\" value=\"nsfw\" checked disabled><label for=\"nsfw\">Allow 18+ Content?</label><br>"
   
   strFormOutput += f"<br><br>"
   #   need to add HUMAN? style checkbox here, required before allowing submit, bot stopper-ish
   #      also likely do not want to show results and "next" link on first load - bot could continue w/o human checkbox
   strFormOutput += "Are you <font color=red>human</font>?<font color=red>*</font>"
   strFormOutput += f"<input type=\"checkbox\" id=\"human\" name=\"human\" value=\"human\" required><label for=\"human\">Yes&emsp;</label>"
   strFormOutput += f"<button type=\"submit\">Browse Media</button>"   
   strFormOutput += f"</form><br><br>"

   #add (media by) username
   #consider single stream vs gallery view
  
   return strFormOutput

# ***************************************

