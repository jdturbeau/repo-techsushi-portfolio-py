#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
#import requests
import os #needed for chdir and getcwd
import markdown
import re  #import but no need to be in requirements.txt

def blog_parsefile(strParseFile):

  #input:    post full path filename, typically .md
  #output:   dictionary with named attributes from file
  
  try:
    
    #check if file string is not null
    #  then check if file exists
    
    #consider "_posts/" if needed
    with open(f"{strParseFile}", "r") as p:
      strParseContent = p.read()
    
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG PARSE FILE read</b>: {e}<br><br>"
      return strSetOutput
  ##alt: return render_template("index.html", post_content=strHTML)
  
  try:
    strPattern = r"(?<=title: ).*"   #gi - use re.ignorecase below
    strTitle = re.search(strPattern, strParseContent, re.IGNORECASE)
    strPattern = r"(?<=date: ).*"
    strDate = re.search(strPattern, strParseContent, re.IGNORECASE)
    strPattern = r"(?<=author: ).*"
    strAuthor = re.search(strPattern, strParseContent, re.IGNORECASE)
    #future
    #strPattern = r"(?<=tags: ).*"
    #strTags = re.search(strPattern, strParseContent, re.IGNORECASE)
    strPattern = r"(?<=-----\n)[\s\S]*"
    strBody = re.search(strPattern, strParseContent, re.IGNORECASE)
  
    dictParsed = {"File": strParseFile, "Title": strTitle, "Date": strDate, "Author": strAuthor, "Body": strBody}
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG PARSE FILE dictionary creation</b>: {e}<br><br>"
      return strSetOutput

  #caller can check if output is dictionary or string(error)
  #  if isinstance(var, dict):  #checks subclasses of dict
  #  if type(var) is dict:      #does not
  #  can replace dict with str

  return dictParsed

def blog_formatpost(dictPostAttribs):
  
  try:
    #verify dictBriefAttribs first
    if not isinstance(dictPostAttribs, dict):
      strTypeOutput = type(dictPostAttribs)
      strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT POST: dictionary variable invalid type: [ {strTypeOutput} ]</b><br><br>"
      return strSetOutput
    
  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG PARSE FILE dictionary creation</b>: {e}<br><br>"
    return strSetOutput

  try:
    #strHTML = markdown.markdown(strContent)
    
    strFile = dictPostAttribs.File
    #File for filename, may need to trim, used for crafting link
    strAppPath = os.environ.get("APP_PATH", "/home/site/wwwroot")
    strFile.replace(strAppPath,"")
    
    strTitle = dictPostAttribs.Title
    strDate = dictPostAttribs.Date
    strAuthor = dictPostAttribs.Author
    strBody = dictPostAttribs.Body
    
    strSetOutput = f"<b><a href=""{strFile}"">{strTitle}</a></b><br>"
    strSetOutput += f"{strDate}&nbsp;&nbsp;&nbsp;&nbsp;{strAuthor}<p>"
    strSetOutput += f"<pre>{strBody}</pre>"

  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT POST</b>: {e}<br><br>"
    return strSetOutput
    
  return strSetOutput

def blog_formatbrief(dictBriefAttribs):

  #verify dictBriefAttribs first
  try:
    #verify dictBriefAttribs first
    if not isinstance(dictBriefAttribs, dict):
      strTypeOutput = type(dictBriefAttribs)
      strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT BRIEF: dictionary variable invalid type: [ {strTypeOutput} ]</b><br><br>"
      return strSetOutput
    
  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT BRIEF</b>: {e}<br><br>"
    return strSetOutput
  
  try:
    strFile = dictBriefAttribs.File
    #File for filename, may need to trim, used for crafting link
    strAppPath = os.environ.get("APP_PATH", "/home/site/wwwroot")
    strFile.replace(strAppPath,"")
    
    strTitle = dictBriefAttribs.Title
    strDate = dictBriefAttribs.Date
    strAuthor = dictBriefAttribs.Author
    #strBody = dictPostAttribs.Body
    
    strSetOutput = f"<b><a href=""{strFile}"">{strTitle}</a></b>&nbsp;&nbsp;&nbsp;&nbsp;"
    strSetOutput += f"{strDate}&nbsp;&nbsp;&nbsp;&nbsp;{strAuthor}<p>"
    #strSetOutput += f"<pre>{strBody}</pre>"

  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT BRIEF</b>: {e}<br><br>"
    return strSetOutput
  
  return strSetOutput
  
def blog_recent(intCount):

  try:
    if not intCount:
      intCount = 5
    
    #Azure: app_path typically temp folder, such as '/tmp/8ddfd43c8909fcd'
    strAppPath = os.environ.get("APP_PATH", "/home/site/wwwroot")

    #full path example '/tmp/8ddfd43c8909fcd/_posts/2025-0926-test.md'
    strAppPath += "/_posts"
    
    lstFiles = filter(os.path.isfile, os.listdir(f"{strAppPath}"))
    lstSortedFiles = [os.path.join(f"{strAppPath}", f) for f in lstFiles]
    lstSortedFiles.sort(key=os.path.getmtime) #modified
    #lstSortedFiles.sort(key=os.path.getctime) #created linux?
    
    #respect intCount or less
    
    strSetOutput = ""
    
    for strPostFile in lstSortedFiles:
      #parse file results for article filename, title, date, author, (tags?), body, and formating
      dictBlogAttrib = blog_parsefile(strPostFile)
      strBriefFormat = blog_formatbrief(dictBlogAttrib)
      strSetOutput += strBriefFormat
      strSetOutput += "<br><br>"
    
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG RECENT Retrieve</b>: {e}<br><br>"
      return strSetOutput
  
  return strSetOutput
