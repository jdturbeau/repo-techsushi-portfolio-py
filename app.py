from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
#import redditmedia
import reddit_media
import blog
import json
import re  #import but no need to be in requirements.txt
from markupsafe import Markup

app = Flask(__name__)

strBlogDirectory = os.environ.get("APP_PATH", "/home/site/wwwroot")
#strBlogDirectory = os.path.join(app.root_path, "_posts") 
strBlogDirectory = os.path.join(strBlogDirectory, "_posts") 

#clear variables after use
#   del strVarName
#force garbage collect, usually not required, but helpful for intense or high utilization
#   gc.collect()

@app.route("/")
def index():
   #return render_template("index.html")
   strWebOutput = reddit_media.app_dictionary("html_header")
   strWebOutput += "Would you like to visit:<br><br>"

   #strWebOutput += "<a href=\"/rmrhome\">Reddit Media Retreiver - Home</a><br><br>"
   strWebOutput += "<a href=\"/rmrwrap\">Reddit Media Retreiver - CSS Wrapped</a><br><br>"
   strWebOutput += "<a href=\"/display\">MarkDown Blog landing page</a><br><br>"
   #strWebOutput += "<a href=\"/displayblog\">MarkDown Blog - single article</a><br><br>"
   #strWebOutput += "<a href=\"/displaytop\">Display Most Recent Blog Articles</a><br><br>"
   strWebOutput += "<a href=\"/home\">Home CSS Template Test</a><br><br>"
   #strWebOutput += "<a href=\"/career\">Career Path Suggestions</a><br><br>"
   
   strWebOutput += reddit_media.app_dictionary("html_footer")
   
   return strWebOutput


@app.route("/rmrwrap")
def rmrwrap():
   
   # Home call, display search criteria, header/navbar/footer
   # Would not expect any POST here
   
   strWebOutput = " "
   #strWebOutput = reddit_media.app_dictionary("html_header")
   # (strGmBaseDestURL, strGmSubReddit="all", lstGmMediaType=["images, videos"], intGmLimit=10, strGmSort="new", strGmView="list", bolNSFW=True, strAfter="")
   dictFormParams = reddit_media.app_dictionary("app_defaultparams")
   strWebOutput += reddit_media.html_form(dictFormParams)
   #strWebOutput += reddit_media.app_dictionary("html_footer")

   strWebOutput = Markup(strWebOutput)
   strProjName = "Reddit Media Reviewer"
   #strProjOverview = "Testing text"
   strProjUseCase = "Use image hashing to identify bots or duplicate accounts. Or allow doom-scrolling for entertainment."
   #strProjPurpose = Markup("Testing Text")
   strProjSkillTech = Markup("Azure Web App<br>Azure DevOps<br>Azure KeyVault<br>GitHub Actions<br>Python<br>REST API with JSON parsing")
   
   #return render_template("proj_index.html", strProjOverview=strProjOverview, strProjName=strProjName, strProjUseCase=strProjUseCase, strProjPurpose=strProjPurpose, strProjSkillTech=strProjSkillTech, strProjBody=strWebOutput)
   return render_template("proj_index.html", strProjName=strProjName, strProjUseCase=strProjUseCase, strProjSkillTech=strProjSkillTech, strProjBody=strWebOutput)

@app.route("/rmrwrapout", methods=['GET', 'POST'])
def rmrwrapout():

   try:
      strRmrMethod = request.method
      
      match strRmrMethod:
         case "POST":
            strSub = request.form.get("sub", "all")
            strMediaType = request.form.get("mediatype", "iv")
            intLimit = request.form.get("limit", 10)
            strSort = request.form.get("sort", "new")
            strView = request.form.get("view", "list")
            bolNSFW = request.form.get("nsfw", True)
            strAfter = request.args.get("after", "")
            
         case "GET":
            strSub = request.args.get("sub", "all")
            strMediaType = request.args.get("mediatype", "iv")
            intLimit = request.args.get("limit", 10)
            strSort = request.args.get("sort", "new")
            strView = request.args.get("view", "list")
            bolNSFW = request.args.get("nsfw", True)
            strAfter = request.args.get("after", "")
   
         case _:
            # defaults or unknown 
            strSubReddit = "all"
            strMediaType = "iv"
            intLimit = 10
            strSort = "new"
            strView = "list"
            bolNSFW = True
            strAfter = ""
   
      #if lstMediaType == []:
      if not strMediaType in locals():
         strMediaType = "iv"
   
      if int(intLimit) > 30:
         intLimit = 30
      if int(intLimit) < 1:
         intLimit = 1
      
      dictRmrParams = {}
      dictRmrParams["sub"] = reddit_media.app_sanitize(strSub)
      dictRmrParams["mediatype"] = reddit_media.app_sanitize(strMediaType)
      dictRmrParams["limit"] = intLimit
      dictRmrParams["sort"] = reddit_media.app_sanitize(strSort)
      dictRmrParams["view"] = reddit_media.app_sanitize(strView)
      dictRmrParams["nsfw"] = bolNSFW
      dictRmrParams["after"] = reddit_media.app_sanitize(strAfter)
      
      strWebOutput = reddit_media.app_main_getmedia(dictRmrParams)
      strWebOutput = Markup(strWebOutput)
      strProjName = "Reddit Media Retriever"
      #strProjOverview = "Testing text"
      strProjUseCase = "Use image hashing to identify bots or duplicate accounts. Or allow doom-scrolling for entertainment."
      #strProjPurpose = Markup("Testing Text")
      strProjSkillTech = Markup("Azure Web App<br>Azure DevOps<br>Python<br>REST API with JSON result parse")
      
   except Exception as e:
      strRmrError = reddit_media.html_crafterror("APP", "RMROUT", e)
      #if not 'dictRmrParams' in locals():
         #strPrettyJson = f"dictGmResponse is null - [ {e} ]"
      #else:
         #strPrettyJson = "[ {e} ]<br><br>"
         #strPrettyJson += json.dumps(dictGmResponse, indent=4)
         #strRmrError += f"<br><br><pre>{strPrettyJson}</pre>"
      return strRmrError
      
   #return render_template("proj_index.html", strProjOverview=strProjOverview, strProjName=strProjName, strProjUseCase=strProjUseCase, strProjPurpose=strProjPurpose, strProjSkillTech=strProjSkillTech, strProjBody=strWebOutput)
   return render_template("proj_index.html", strProjName=strProjName, strProjUseCase=strProjUseCase, strProjSkillTech=strProjSkillTech, strProjBody=strWebOutput)
   

@app.route("/rmrhome")
def rmrhome():
   
   # Home call, display search criteria, header/navbar/footer
   # Would not expect any POST here

   strWebOutput = reddit_media.app_dictionary("html_header")
   # (strGmBaseDestURL, strGmSubReddit="all", lstGmMediaType=["images, videos"], intGmLimit=10, strGmSort="new", strGmView="list", bolNSFW=True, strAfter="")
   dictFormParams = reddit_media.app_dictionary("app_defaultparams")
   strWebOutput += reddit_media.html_form(dictFormParams)
   strWebOutput += reddit_media.app_dictionary("html_footer")
   
   return strWebOutput


@app.route("/rmrout", methods=['GET', 'POST'])
def rmrout():

   try:
      strRmrMethod = request.method
      
      match strRmrMethod:
         case "POST":
            strSub = request.form.get("sub", "all")
            strMediaType = request.form.get("mediatype", "iv")
            intLimit = request.form.get("limit", 10)
            strSort = request.form.get("sort", "new")
            strView = request.form.get("view", "list")
            bolNSFW = request.form.get("nsfw", True)
            strAfter = request.args.get("after", "")
            
         case "GET":
            strSub = request.args.get("sub", "all")
            strMediaType = request.args.get("mediatype", "iv")
            intLimit = request.args.get("limit", 10)
            strSort = request.args.get("sort", "new")
            strView = request.args.get("view", "list")
            bolNSFW = request.args.get("nsfw", True)
            strAfter = request.args.get("after", "")
   
         case _:
            # defaults or unknown 
            strSubReddit = "all"
            strMediaType = "iv"
            intLimit = 10
            strSort = "new"
            strView = "list"
            bolNSFW = True
            strAfter = ""
   
      #if lstMediaType == []:
      if not strMediaType in locals():
         strMediaType = "iv"
   
      if int(intLimit) > 30:
         intLimit = 30
      if int(intLimit) < 1:
         intLimit = 1
      
      dictRmrParams = {}
      dictRmrParams["sub"] = reddit_media.app_sanitize(strSub)
      dictRmrParams["mediatype"] = reddit_media.app_sanitize(strMediaType)
      dictRmrParams["limit"] = intLimit
      dictRmrParams["sort"] = reddit_media.app_sanitize(strSort)
      dictRmrParams["view"] = reddit_media.app_sanitize(strView)
      dictRmrParams["nsfw"] = bolNSFW
      dictRmrParams["after"] = reddit_media.app_sanitize(strAfter)
      
      strWebOutput = reddit_media.app_main_getmedia(dictRmrParams)
      
   except Exception as e:
      strRmrError = reddit_media.html_crafterror("APP", "RMROUT", e)
      #if not 'dictRmrParams' in locals():
         #strPrettyJson = f"dictGmResponse is null - [ {e} ]"
      #else:
         #strPrettyJson = "[ {e} ]<br><br>"
         #strPrettyJson += json.dumps(dictGmResponse, indent=4)
         #strRmrError += f"<br><br><pre>{strPrettyJson}</pre>"
      return strRmrError
   
   return strWebOutput

@app.route("/home")
def home():
   
   #return render_template('index.html', user_agent = user_agent, client_ip = client_ip)
   return render_template("index.html")

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

@app.route("/career")
def career():

   #remember to import career.py when ready
   
   try:
      strWebCareer = "coming soon"

   except Exception as e:
      #could contain sensitive information in error message
      strWebOutput = f"an unexpected error occurred during <b>CAREERPATH</b>: <font color=red>{e}</font><br><br>"
      return strWebCareer
   
   return strWebCareer

if __name__ == '__main__':
   app.run(debug=True)
