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
  # try...except here
  #
  
  # input - URL
  # output - dictionary with named parameters
  
  return

def html_form(dictFormParams):
  #historical - strFormDestination, strFormSub="all", lstFormMediaType="iv", intFormLimit=10, strFormSort="new", strFormView="list", bolFormNSFW=True
  
  try:
    strFormBaseURL = app_dictionary("url_appbase")
    # confirm if baseURL ends with a slash ?
    
    if not 'strFormBaseURL' in locals():
      strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var strFormBaseURL does not exist [ {e} ]")
      return strFormError
    
    strFormSub = dictFormParams["sub"]
    if not 'strFormSub' in locals():
      strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var strFormSub does not exist [ {e} ]")
      return strFormError

    strFormMediaType = dictFormParams["mediatype"]
    if not 'strFormMediaType' in locals():
      strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var strFormMediaType does not exist [ {e} ]")
      return strFormError
    
    intFormLimit = int(dictFormParams["limit"])
    if not 'intFormLimit' in locals():
      strFormError = html_crafterror(""REDDIT_MEDIA", HTML FORM", f"var intFormLimit does not exist [ {e} ]")
      return strFormError

    strFormSort = dictFormParams["sort"]
    if not 'strFormSort' in locals():
      strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var strFormSort does not exist [ {e} ]")
      return strFormError

    strFormView = dictFormParams["view"]
    if not 'strFormView' in locals():
      strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var strFormView does not exist [ {e} ]")
      return strFormError

    bolFormNSFW = dictFormParams["nsfw"]
    if not 'bolFormNSFW' in locals():
      strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var bolFormNSFW does not exist [ {e} ]")
      return strFormError

    strFormAfter = dictFormParams["after"]  # this may be blank
    #if not 'strFormAfter' in locals():
      #strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", f"var strFormAfter does not exist [ {e} ]")
      #return strFormError
  
  
  strFormOutput = f"<form action=\"/{strFormBaseURL}\" method=\"post\"><!-- Form elements go here -->"
  strFormOutput += f"<label for=\"subreddit\">Subreddit: </label><input type=\"text\" id=\"sub\" name=\"subreddit\" placeholder=\"{strFormSub}\" autocomplete=\"off\">"
   
   # translate
   #    strFormOutput += f"<input type=\"checkbox\" id=\"images\" name=\"mediatype\" value=\"images\" checked disabled><label for=\"images\">Images</label>"
   #    strFormOutput += f"<input type=\"checkbox\" id=\"videos\" name=\"mediatype\" value=\"videos\" checked disabled><label for=\"videos\">Videos</label>"
   match strFormMediaType:
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

   # translate strFormSort into drop down selection - new is default selected
   strFormOutput += f"<label for=\"sort\"> Sort by: </label><select id=\"sort\" name=\"sort\" disabled>"
   strFormOutput += f"<option value=\"new\" selected=\"true\">New</option>"
   strFormOutput += f"<option value=\"hot\">Hot</option>"
   strFormOutput += f"<option value=\"rising\">Rising</option>"
   strFormOutput += f"<option value=\"controversial\">Controversial</option>"
   strFormOutput += f"<option value=\"top\">Top</option>"
   strFormOutput += f"</select>"
   strFormOutput += f"<br><br>"
   
   # translate strFormView by checked radio
   strFormOutput += f"<input type=\"radio\" id=\"list\" name=\"view\" value=\"list\" checked disabled><label for=\"list\">List View</label>"
   strFormOutput += f"<input type=\"radio\" id=\"gallery\" name=\"view\" value=\"gallery\" disabled><label for=\"gallery\">Gallery View</label>"

   # translate bolFormNSFW into check
  if bolFormNSFW:
    strFormOutput += f"<input type=\"checkbox\" id=\"nsfw\" name=\"nsfw\" value=\"nsfw\" checked disabled><label for=\"nsfw\">Allow 18+ Content?</label><br>"
  else:
    strFormOutput += f"<input type=\"checkbox\" id=\"nsfw\" name=\"nsfw\" value=\"nsfw\" disabled><label for=\"nsfw\">Allow 18+ Content?</label><br>"
   
   strFormOutput += f"<br><br>"

   #   need to add HUMAN? style checkbox here, required before allowing submit, bot stopper-ish
   #      also likely do not want to show results and "next" link on first load - bot could continue w/o human checkbox
   strFormOutput += "Are you <font color=red>human</font>?<font color=red>*</font>"
   strFormOutput += f"<input type=\"checkbox\" id=\"human\" name=\"human\" value=\"human\" required><label for=\"human\">Yes&emsp;</label>"
   strFormOutput += f"<button type=\"submit\">Browse Media</button>"   
   strFormOutput += f"</form><br><br>"

   #add (media by) username
   #consider single stream vs gallery view

  except Exception as e:
    #could contain sensitive information in error message 
    strFormError = html_crafterror("REDDIT_MEDIA", "HTML FORM", e)
    return strFormError
  
   return strFormOutput

# ***************************************
#  successful review above. continue below... 2025-1018
# ***************************************

def reddit_getjson(dictGjParams):
  # historical - strGjTokenType, strGjToken, strGjURL, strGjSort

   # to be handled by / used in jsontohtml, unneeded here
   #    strGjSubReddit
   #    lstGjMediaType
   #    intGjLimit
   #    strGjView
   #    bolGjNSFW
   
   # check if subreddit exists

   # function to craft request URL
   
  try:
    strGjURL = app_dictionary("url_oauth")
    
    strGjUserAgent = app_dictionary("txt_useragent")
    
    strGjTokenTypeLabel = app_dictionary("kv_tokentype")
    strGjTokenType = kv_get(strGjTokenTypeLabel)
    strGjTokenLabel = app_dictionary("kv_token")
    strGjToken = kv_get(strGjTokenLabel)

    dictGjHeader = { "Authorization": f"{strGjTokenType} {strGjToken}", "User-Agent": strGjUserAgent }
    roGjReceived = requests.get(strGjURL, headers=dictGjHeader)

    if not 'roGjReceived' in locals():
      strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", f"Response appears null (1): [ {e} ]")
      return strGjError
    
    strGjReqStatus = roGjReceived.status_code
    dictGjJson = roGjReceived.json()

    if not 'strGjReqStatus' in locals():
      strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", f"Response Status Code appears null (2): [ {e} ]")
      return strGjError
      
    if not 'dictGjJson' in locals():
      strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", f"Response appears null (3): [ {e} ]")
      return strGjError
      
    '''
    match strGjReqStatus:
      case "403":
        strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", f"Unable to proceed!<br>Status Code: {strGjReqStatus}")
        # historical - <br>Token type: {strGjTokenType}
        return strGjError
      case _:
        dictGjJson = roGjReceived.json()
        if not 'dictGjJson' in locals():
          strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", f"JSON response is null (dictGjJson)!<br>Response: {roGjReceived}<br>Token type: {strGjTokenType}")
          return strGjError
    '''

  except Exception as e:
    #could contain sensitive information in error message
    if not 'roGjReceived' in locals():
      strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", f"Received content is null (4): [ {e} ]")
      return strGjJsonOutput
    else:
      strGjError = html_crafterror("REDDIT_MEDIA", "GETJSON", e)
      return strGjJsonOutput
  
  return dictGjJson


# ***************************************


      strGmSort = app_sanitize(strGmSort)
      strGmView = app_sanitize(strGmView)
      strAfter = app_sanitize(strAfter)
      
      
      strGmOutput = app_dictionary("html_header")
      
      # ensure distinction between API RESULTS LIMIT and app defined DISPLAY LIMIT
      #    Example - 50 results returned may not equal 50 displayed media items
      
      # need to CAP intLIMIT to avoid malicious use (perhaps 30?)
      #    intLimit is intended for display limit, not retrieval limit - may not always retrieve media for each thread
      if int(intGmLimit) > 30:
         intGmLimit = 30
      if int(intGmLimit) < 1:
         intGmLimit = 1
      
      intGmMediaFound = 0   #m easure found media items against limit desired
      intGmRun = 0   # used to avoid hang/loop cycle for subreddit that may not have any media
      
      strGmOutput += html_form(strGmBaseDestURL, strGmSubReddit, lstGmMediaType, intGmLimit, strGmSort, strGmView, bolGmNSFW)
            
      #Should - Test if existing token works using known simple api call?
      
      strVault = app_dictionary("kv_name")
      strRedditURL = app_dictionary("url_login")
      strResult = kv_refreshtoken(strVault, strRedditURL)
   
      #Should - Test if subreddit exists
      '''
      {
      invalid subreddit
       "kind": "Listing",
       "data": {
           "after": null,
           "dist": 0,
           "modhash": "",
           "geo_filter": "",
           "children": [],
           "before": null
          }
         }
      
      valid subreddit
         "kind": "Listing",
             "data": {
           "after": "t3_1o1cnhp",
           "dist": 25,
           "modhash": "",
           "geo_filter": "",
           "children": [
      '''
      
      strTokenType = app_dictionary("kv_tokentype")
      strTokenType = kv_get(strVault, strTokenType)
      strToken = app_dictionary("kv_token")
      strToken = kv_get(strVault, strToken)

      strGmURL = app_dictionary("url_oauth")
      
      while True:
         
         # Use function to craft URL to pass to API
         #    strGmApiURL is API URL with subreddit, sort, after params
         strGmApiURL = html_crafturl(strGmURL, strGmSubReddit, lstGmMediaType, intGmLimit, strGmSort, strGmView, bolGmNSFW, strAfter)
         
         #dictGmResponse = reddit_getjson(strGmSubReddit, lstGmMediaType, intGmLimit, strGmSort, strGmView, bolGmNSFW, strAfter, strTokenType, strToken, strGmApiURL)
         #   reddit_getjson(strGjTokenType, strGjToken, strGjURL, strGjSort, strAfter):
         dictGmResponse = reddit_getjson(strTokenType, strToken, strGmApiURL, strGmSort, strAfter)
         # strGmBaseDestURL - local app url
         # strGmApiURL - reddit api url
         # Dest URL to be handled outside of function
   
         # is dictGmResponse empty / null / data.dist = 0 / data.before==data.after
         if not 'dictGmResponse' in locals():
            strGmOutput = html_crafterror("APP MAIN GETMEDIA", f"{e}<br>URL: {strGjURL}<br>Token type: {strGjTokenType}")
            return strGmOutput
         
         strGmBody = reddit_jsontohtml(dictGmResponse, lstGmMediaType, strGmBaseDestURL)
   
         # how to check if strGmBody contains HTML vs error
         
         strGmOutput += strGmBody
            
         strAfter = dictGmResponse["data"]["after"]


         '''
         #if not strAfter:
            #strAfter = ""
         #else:
            # re.escape equal sign does not need escape character
            #strGmPattern = r"((?<=after=)(.*?)(?=&))|((?<=after=).*)"
            # strGmApiURL - reddit api url
            strGmApiURL = re.sub(strGmPattern, strAfter, strGmApiURL, flags=re.IGNORECASE)
            # strGmDestURL - local app url
            strGmBaseDestURL = re.sub(strGmPattern, strAfter, strGmBaseDestURL, flags=re.IGNORECASE)
            
            #verify if below is necessary
            
            if not strAfter in strGmBaseDestURL:
               #to craft Next Posts link
               strGmBaseDestURL += f"&after={strAfter}"
            if not strAfter in strGmApiURL:
               #to craft API url for next batch
               strGmApiURL += f"?after={strAfter}"
         '''
         strGmJSON = str(dictGmResponse)
         intGmFound = strGmJSON.count("\"post_hint\":")
         intGmMediaFound += intGmFound
         intGmRun += 1
   
         if intGmMediaFound >= int(intGmLimit):
            # count media results returned, break out of while loop if equal or over limit
            break
         if intGmRun >= 4:
            #prevent undesired loop runaway for subreddits that may not have much or any media
            break
   
      # should use function to craft internal URL
      strGmNextURL = html_crafturl(strGmBaseDestURL, strGmSubReddit, lstGmMediaType, intGmLimit, strGmSort, strGmView, bolGmNSFW, strAfter)
      strGmOutput += f"<p align=\"right\"><a href=\"{strGmNextURL}\">Next Posts</a></p>"
      
      # need to remove after= entry
      #strGmPattern = r"(\&after=)(.*?)(?=&)|(\&after=).*"
      #strGmReturnURL = re.sub(strGmPattern, "", strGmBaseDestURL, flags=re.IGNORECASE)
      # should use function to craft internal URL
      strGmRefreshURL = html_crafturl(strGmBaseDestURL, strGmSubReddit, lstGmMediaType, intGmLimit, strGmSort, strGmView, bolGmNSFW, "")
      strGmOutput += f"<p align=\"right\"><a href=\"{strGmRefreshURL}\">Reload From Beginning</a></p>"
      
      strGmOutput += app_dictionary("html_footer")
   
   except Exception as e:
      strGmOutput = html_crafterror("APP MAIN GETMEDIA", e)
      if not 'dictGmResponse' in locals():
         strPrettyJson = f"dictGmResponse is null"
      else:
         strPrettyJson = json.dumps(dictGmResponse, indent=4)
      strGmOutput += f"<br><br><pre>{strPrettyJson}</pre>"
      return strGmOutput
   return strGmOutput

def app_main_getmedia(strGmBaseDestURL, strGmSubReddit="all", lstGmMediaType="iv", intGmLimit=10, strGmSort="new", strGmView="list", bolGmNSFW=True, strAfter=""):
