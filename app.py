from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import redditmedia

app = Flask(__name__)

@app.route("/")
def index():
   #return render_template("index.html")
   strWebOutput = redditmedia.app_dictionary("html_header")
   strWebOutput += "Would you like to visit:<br><br>"

   strWebOutput += "<a href=\"/checktoken\">Check token status</a><br><br>"
   strWebOutput += "<a href=\"/redmedia\">Reddit media retreiver</a><br><br>"
   
   #strWebOutput += "<a href=\"/keysset\">KV set</a><br><br>"
   #strWebOutput += "<a href=\"/keysget\">KV retrieve</a><br><br>"
   #strWebOutput += "<a href=\"/demo\">demo second page routing</a><br><br>"
   #strWebOutput += "<a href=\"/refreshtoken\">refresh api token</a><br><br>"
   #strWebOutput += "<a href=\"/getcontent\">use api token to get content</a><br><br>"
   #strWebOutput += "<a href=\"/testpost\">test posting value</a><br><br>"
   strWebOutput += redditmedia.app_dictionary("html_footer")
   
   return strWebOutput

@app.route("/redmedia", methods=['GET', 'POST'])
def redmedia():
   #table with
   #   overview, what, technologies involved,
   try:
      strWebOutput = redditmedia.app_dictionary("html_header")
      strWebOutput += redditmedia.html_form("redmedia")
      strMethod = request.method
      strWebOutput += f"Method [ {strMethod} ]<br>"
      match strMethod:
         case "POST":
            strSubReddit = request.form.get("sub", "all")
            lstMediaType = request.form.getlist("mediatype")
            strSort = request.form.get("sort", "new")
            strAfter = request.args.get("after", "ignoreP1")
            strLimit = request.args.get("limit", "ignoreP2")
         case "GET":
            #handle first load
            #handle next/after
            strSubReddit = request.args.get("sub", "all")
            lstMediaType = request.args.getlist("mediatype")
            strSort = request.args.get("sort", "new")
            strAfter = request.args.get("after", "ignoreG1")
            strLimit = request.args.get("limit", "ignoreG2")
            #maybe request.GET.get('variable_name')
         case _:
            #default or unknown 
            strSubReddit = "all"
            lstMediaType = ["pictures"]
            strSort = "new"
            strAfter = "ignoreU1"
            strLimit = "ignoreU2"
      if not lstMediaType:
         lstMediaType = ["pictures"]
      
      strWebOutput += f"Subreddit [ {strSubReddit} ]<br>Media Type [ {lstMediaType} ]<br>Sort [ {strSort} ]<br>After [ {strAfter} ]<br>Limit [ {strLimit} ]<br><br>"

      strWebOutput += "... attempting token refresh...<br>"
      
      strVault = redditmedia.app_dictionary("kv_name")
      strRedditURL = redditmedia.app_dictionary("url_login")
      strResult = redditmedia.kv_refreshtoken(strVault, strRedditURL)

      strWebOutput += f"... token refresh successful...[ {strResult} ]<br>"

      strTokenType = redditmedia.app_dictionary("kv_tokentype")
      strToken = redditmedia.app_dictionary("kv_token")
      strURL = redditmedia.app_dictionary("url_oauth")
      strURL += f"{strSubReddit}"
      strURL += "/"
      strURL += f"{strSort}"
      
      strWebOutput += f"... attempting to get json [ {strURL} ]...<br>"
      
      dictResponse = redditmedia.reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL, strAfter)
      
      strWebOutput += f"... get json result... [ {dictResponse} ]<br>"
      strWebOutput += f"... attempting to convert JSON to HTML...<br>"
      
      strDestURL = f"/redmedia?sub={strSubReddit}&sort={strSort}" #&after={strAfter}
      strBody = redditmedia.reddit_jsontohtml(dictResponse, lstMediaType, strDestURL)
      strWebOutput += f"Body [ {strBody} ]<br>"
      
      strWebOutput += f"... JSON to HTML conversion successful...<br>"
      
      strWebOutput += redditmedia.app_dictionary("html_footer")
   except Exception as e:
      #could contain sensitive information in error message
      strWebOutput += f"an unexpected error occurred during <b>RETRIEVE</b>: <font color=red>{e}</font><br><br>"
      #raise strWebOutput
      return strWebOutput
   return strWebOutput

@app.route("/checktoken")
def checktoken():
   try:
      strTokenType = redditmedia.kv_get(strVault, "api-reddit-tokentype")
      strToken = redditmedia.kv_get(strVault, "api-reddit-token")
      strUserAgent = redditmedia.app_dictionary("txt_useragent")
      dictHeader = { "Authorization": f"{strTokenType} {strToken}", "User-Agent": strUserAgent }
      #how to handle 'after' here?
      
      strWebOutput = f"Token type [ {strTokenType} ]<br>Header [ {dictHeader} ]<br>"
      
      roReceived = requests.get(strURL, headers=dictHeader)
      strReqStatus = roReceived.status_code
      
      strWebOutput += f"Status Code [ {strReqStatus} ]<br>"
      
      match strReqStatus:
         case "403":
            strJsonOutput = f"<b>GETJSON</b>, status code: [ {roReceived.status_code} ]<br>Token type [ {strTokenType} ]<br> Unable to proceed!<br>"
            raise RuntimeError(strJsonOutput)
         case _:
            dictJson = roReceived.json()
   except Exception as e:
      #could contain sensitive information in error message
      strWebOutput += f"an unexpected error occurred during <b>RETRIEVE</b>: <font color=red>{e}</font><br><br>"
      return strWebOutput
   return strWebOutput

if __name__ == '__main__':
   app.run(debug=True)
