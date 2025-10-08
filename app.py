from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
import redditmedia
import blog

app = Flask(__name__)

strBlogDirectory = os.environ.get("APP_PATH", "/home/site/wwwroot")
#strBlogDirectory = os.path.join(app.root_path, "_posts") 
strBlogDirectory = os.path.join(strBlogDirectory, "_posts") 

@app.route("/")
def index():
   #return render_template("index.html")
   strWebOutput = redditmedia.app_dictionary("html_header")
   strWebOutput += "Would you like to visit:<br><br>"

   strWebOutput += "<a href=\"/redmedia\">Reddit media retreiver</a><br><br>"
   strWebOutput += "<a href=\"/display\">MarkDown Blog landing page</a><br><br>"
   strWebOutput += "<a href=\"/displayblog\">MarkDown Blog - single article</a><br><br>"
   strWebOutput += "<a href=\"/displaytop\">Display Most Recent Blog Articles</a><br><br>"
   strWebOutput += "<a href=\"/home\">Home CSS Template Test</a><br><br>"
   strWebOutput += "<a href=\"/jsonview\">Reddit JSON Viewer</a><br><br>"
   
   strWebOutput += redditmedia.app_dictionary("html_footer")
   
   return strWebOutput

@app.route("/display")
def display():

   try:
      #strBlogArticle = request.form.get("post", "all")
      strBlogArticle = request.args.get("post", "all")
      
      if strBlogArticle != "all":
         #specific post
         #   does it exist?
         #   retrieve
         #   successful
         #   format
         strBlogArticle = f"{strBlogDirectory}/{strBlogArticle}.md"
         dictPostAttribs = blog.blog_parsefile(strBlogArticle)
         #confirm dict created or error
         strWebOutput = blog.blog_formatpost(dictPostAttribs)
         
      else:
         #retrieve top 10 most recent?
         #   brief format
         strWebOutput = blog.blog_recent(5, strBlogDirectory)

      strWebOutput += "<br><br>blog home link & techsushi home link<br><br>"
      
   except Exception as e:
      #could contain sensitive information in error message
      #   404 article not found?
      strWebOutput += f"an unexpected error occurred during <b>DISPLAY</b>: <font color=red>{e}</font><br><br>"
      return strWebOutput

   return strWebOutput
   
@app.route("/redmedia", methods=['GET', 'POST'])
def redmedia():
   
   #table with
   #   overview, what, technologies involved,
   
   try:
      strWebOutput = redditmedia.app_dictionary("html_header")
      #strWebOutput += redditmedia.html_form("redmedia")
      strMethod = request.method

      
      #Do these cases need to be separate? Yes, form.get vs args.get
      match strMethod:
         case "POST":
            strSubReddit = request.form.get("sub", "all")
            lstMediaType = request.form.getlist("mediatype")
            strSort = request.form.get("sort", "new")
            strAfter = request.args.get("after", "")
            intLimit = request.args.get("limit", 10)
         case "GET":
            #handle first load
            #handle next/after
            strSubReddit = request.args.get("sub", "all")
            lstMediaType = request.args.getlist("mediatype")
            strSort = request.args.get("sort", "new")
            strAfter = request.args.get("after", "")
            intLimit = request.args.get("limit", 10)
         case _:
            #default or unknown 
            strSubReddit = "all"
            lstMediaType = ["images, videos"]
            strSort = "new"
            strAfter = ""
            intLimit = 10
      
      '''
      strSubReddit = request.form.get("sub", "all")
      lstMediaType = request.form.getlist("mediatype")
      strSort = request.form.get("sort", "new")
      strAfter = request.args.get("after", "")
      intLimit = request.args.get("limit", 10)
      #need view type flag
      #need over18 flag
      '''      
      
      if lstMediaType == []:
         lstMediaType = ["images, videos"]

      strWebOutput += redditmedia.html_form("redmedia", strSubReddit, intLimit, strSort)

      #Should - Test if existing token works using known simple api call?
      
      strVault = redditmedia.app_dictionary("kv_name")
      strRedditURL = redditmedia.app_dictionary("url_login")
      strResult = redditmedia.kv_refreshtoken(strVault, strRedditURL)

      #Should - Test if subreddit exists
      
      strTokenType = redditmedia.app_dictionary("kv_tokentype")
      strTokenType = redditmedia.kv_get(strVault, strTokenType)
      strToken = redditmedia.app_dictionary("kv_token")
      strToken = redditmedia.kv_get(strVault, strToken)
      strURL = redditmedia.app_dictionary("url_oauth")
      strURL += f"{strSubReddit}"
      strURL += "/"
      strURL += f"{strSort}"
      #determine ? versus &
      if strAfter:
         strURL += f"?after={strAfter}"

      #strLimit is intended for display limit, not retrieval limit - may not always retrieve media for each thread
      
      #Next - make this "after" change
      #dictResponse = redditmedia.reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL, strAfter)
      #dictResponse = redditmedia.reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL, strLimit, strAfter)
      dictResponse = redditmedia.reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL)
      
      #strWebOutput += f"... get json result... [ {dictResponse} ]<br>"
      #strWebOutput += f"... attempting to convert JSON to HTML...<br>"
      
      strDestURL = f"/redmedia?sub={strSubReddit}&sort={strSort}" #&after={strAfter}
      strBody = redditmedia.reddit_jsontohtml(dictResponse, lstMediaType, strDestURL)
      #strWebOutput += f"Body [ {strBody} ]<br>"
      #strWebOutput += f"... JSON to HTML conversion successful...<br>"
      
      strWebOutput += strBody
      
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
      strVault = redditmedia.app_dictionary("kv_name")
      strTokenType = redditmedia.kv_get(strVault, "api-reddit-tokentype")
      strToken = redditmedia.kv_get(strVault, "api-reddit-token")
      strURL = redditmedia.app_dictionary("url_oauth")
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

@app.route("/displayblog")
def displayblog():
   strPostFile = "_posts/2025-0925-welcome.md"
   #strPostContent = blog.blog_parsefile(strPostFile)
   dictBlogAttrib = blog.blog_parsefile(strPostFile)
   if not isinstance(dictBlogAttrib, dict):
      strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT POST: dictionary variable invalid type: [ {dictBlogAttrib} ]</b><br><br>"
      return strSetOutput
   
   strPostFormat = blog.blog_formatpost(dictBlogAttrib)
   strSetOutput = strPostFormat
   strSetOutput += "<br><br>"
   return strSetOutput

@app.route("/displaytop")
def displaytop():
   
   strTopContent = blog.blog_recent(5)
   
   return strTopContent

@app.route("/home")
def home():
   
   #return render_template('index.html', user_agent = user_agent, client_ip = client_ip)
   return render_template("index.html")

@app.route("/jsonview", methods=['GET', 'POST'])
def jsonview():

   try:
      if not strSubReddit:
         strSubReddit = "all"
      if not intLimit:
         intLimit = 10
      if not strSort:
         strSort = "new"
      if not lstMediaType:
         lstMediaType = ["images, videos"]
         
      strWebOutput = redditmedia.app_dictionary("html_header")
      strWebOutput += redditmedia.html_form("jsonview", strSubReddit, intLimit, strSort)
      strVault = redditmedia.app_dictionary("kv_name")
      strRedditURL = redditmedia.app_dictionary("url_login")
      strResult = redditmedia.kv_refreshtoken(strVault, strRedditURL)
   
      strVault = redditmedia.app_dictionary("kv_name")
      strRedditURL = redditmedia.app_dictionary("url_login")
      strResult = redditmedia.kv_refreshtoken(strVault, strRedditURL)
   
      #Should - Test if subreddit exists
      
      strTokenType = redditmedia.app_dictionary("kv_tokentype")
      strTokenType = redditmedia.kv_get(strVault, strTokenType)
      strToken = redditmedia.app_dictionary("kv_token")
      strToken = redditmedia.kv_get(strVault, strToken)
      strURL = redditmedia.app_dictionary("url_oauth")
      #strURL += f"{strSubReddit}"
      strURL += "/"
      strURL += f"{strSort}"
      #strURL = "all/new"
   
      dictResponse = redditmedia.reddit_getjson(strSubReddit, lstMediaType, strSort, strTokenType, strToken, strURL)
   
      strWebOutput += dictResponse
   except Exception as e:
      #could contain sensitive information in error message
      strWebOutput += f"an unexpected error occurred during <b>JSONVIEW TEST</b>: <font color=red>{e}</font><br><br>"
      return strWebOutput
   
   return strWebOutput

if __name__ == '__main__':
   app.run(debug=True)
