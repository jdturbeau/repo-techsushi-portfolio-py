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

   strWebOutput += "<a href=\"/redmedia\">Reddit media retreiver</a><br><br>"
   
   #strWebOutput += "<a href=\"/keysset\">KV set</a><br><br>"
   #strWebOutput += "<a href=\"/keysget\">KV retrieve</a><br><br>"
   #strWebOutput += "<a href=\"/demo\">demo second page routing</a><br><br>"
   #strWebOutput += "<a href=\"/refreshtoken\">refresh api token</a><br><br>"
   #strWebOutput += "<a href=\"/getcontent\">use api token to get content</a><br><br>"
   strWebOutput += "<a href=\"/testpost\">test posting value</a><br><br>"
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
            strSubReddit = request.form.get("sub")
            lstMediaType = request.form.getlist("mediatype")
            strSort = request.form.get("sort", "")
            strAfter = request.args.get("after", "")
            strLimit = request.args.get("limit", "")
         case "GET":
            #handle first load
            #handle next/after
            strSubReddit = request.args.get("sub", "")
            lstMediaType = request.args.getlist("mediatype")
            strSort = request.args.get("sort", "")
            strAfter = request.args.get("after", "")
            strLimit = request.args.get("limit", "")
            #maybe request.GET.get('variable_name')
         case _:
            #default or unknown 
            strSubReddit = "unknown"
      
      strWebOutput += f"Subreddit [ {strSubReddit} ]<br>Media Type [ {lstMediaType} ]<br>Sort [ {strSort} ]<br>After [ {strAfter} ]<br>Limit [ {strLimit} ]<br><br>"
      
      strVault = redditmedia.app_dictionary("kv_name")
      strRedditURL = redditmedia.app_dictionary("url_login")
      redditmedia.kv_refreshtoken(strVault, strRedditURL)

      strTokenType = redditmedia.app_dictionary("kv_tokentype")
      strToken = redditmedia.app_dictionary("kv_token")
      strURL = redditmedia.app_dictionary("url_oauth")
      if strSubReddit:
         strURL += f"/{strSubReddit}/{strSort}"
      dictResponse = redditmedia.reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL, strAfter)
      strDestURL = f"/redmedia?sub={strSubReddit}&sort={strSort}&after={strAfter}"
      strWebOutput += redditmedia.reddit_jsontohtml(dictResponse, lstMediaType, strDestURL)
      
      strWebOutput += redditmedia.app_dictionary("html_footer")
   except Exception as e:
      #could contain sensitive information in error message
      strWebOutput += f"an unexpected error occurred during <b>RETRIEVE</b>: <font color=red>{e}</font><br><br>"
      #raise strWebOutput
      return strWebOutput
   return strWebOutput

if __name__ == '__main__':
   app.run(debug=True)
