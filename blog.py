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
    
    '''
    if not os.path.isfile(strParseFile):
      strAppPath = os.environ.get("APP_PATH", "/home/site/wwwroot")
      strParseFileAlt = f"{strAppPath}{strParseFile}"
      if not os.path.isfile(strParseFileAlt):
        strParseFileAlt = f"{strAppPath}/{strParseFile}"
        strParseFile = strParseFileAlt
      else:
        strParseFile = strParseFileAlt
    '''
    
    #consider "_posts/" if needed
    with open(f"{strParseFile}", "r") as p:
      strParseContent = p.read()
    
  except FileNotFoundError:
    strSetOutput = f"an unexpected error occurred during <b>BLOG PARSE FILE read</b>: The file [ {strParseFile} ] does not exist.<br><br>"
    return strSetOutput
  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG PARSE FILE read</b>: {e}<br><br>"
    return strSetOutput
  ##alt: return render_template("index.html", post_content=strHTML)
  
  try:
    strPattern = r"(?<=title: ).*"   #gi - use re.ignorecase below
    objMatch = re.search(strPattern, strParseContent, re.IGNORECASE)
    strTitle = objMatch.group()
    strPattern = r"(?<=date: ).*"
    objMatch = re.search(strPattern, strParseContent, re.IGNORECASE)
    strDate = objMatch.group()
    strPattern = r"(?<=author: ).*"
    objMatch = re.search(strPattern, strParseContent, re.IGNORECASE)
    strAuthor = objMatch.group()
    #future
    #strPattern = r"(?<=tags: ).*"
    #strTags = re.search(strPattern, strParseContent, re.IGNORECASE)
    strPattern = r"(?<=-----\n)[\s\S]*"
    objMatch = re.search(strPattern, strParseContent, re.IGNORECASE)
    strBody = objMatch.group()
  
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
    
    strFile = dictPostAttribs["File"]
    #File for filename, may need to trim, used for crafting link
    strAppPath = os.environ.get("APP_PATH", "/home/site/wwwroot")
    strFile.replace(strAppPath, "")
    
    strTitle = dictPostAttribs["Title"]
    strDate = dictPostAttribs["Date"]
    strAuthor = dictPostAttribs["Author"]
    strBody = dictPostAttribs["Body"]
    
    strSetOutput = f"<b><a href=\"{strFile}\">{strTitle}</a></b><br>"
    strSetOutput += f"{strDate}&nbsp;&nbsp;&nbsp;&nbsp;{strAuthor}<p>"
    strSetOutput += f"<pre>{strBody}</pre>"

  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT POST</b>: {e}<br>[ {dictPostAttribs} ]<br><br>"
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
    strFile = dictBriefAttribs["File"]
    #File for filename, may need to trim, used for crafting link
    strAppPath = os.environ.get("APP_PATH", "/home/site/wwwroot")
    strFile.replace(strAppPath, "")

    #do we want to trim off the .MD extension as well for URL usage
    
    strTitle = dictBriefAttribs["Title"]
    strDate = dictBriefAttribs["Date"]
    strAuthor = dictBriefAttribs["Author"]
    #strBody = dictBriefAttribs["Body"]
    
    strSetOutput = f"<b><a href=\"{strFile}\">{strTitle}</a></b>&nbsp;&nbsp;&nbsp;&nbsp;"
    strSetOutput += f"{strDate}&nbsp;&nbsp;&nbsp;&nbsp;{strAuthor}<p>"
    #strSetOutput += f"<pre>{strBody}</pre>"

  except Exception as e:
    #could contain sensitive information in error message
    strSetOutput = f"an unexpected error occurred during <b>BLOG FORMAT BRIEF</b>: {e}<br><br>"
    return strSetOutput
  
  return strSetOutput
  
def blog_recent(intCount, strBlogDir):

  try:
    if not intCount:
      intCount = 5
    
    #check if strBlogDir path exists
    
    #lstSortedFiles = [os.path.join(strAppPath, f) for f in lstFiles]
    lstFiles = os.listdir(strBlogDir)
    lstPathFiles = [os.path.join(strBlogDir, f) for f in lstFiles]
        
    #lstFiles = filter(os.path.isfile, lstPathFiles)
    lstFiles = [strFile for strFile in lstPathFiles if os.path.isfile(strFile)]
    #sort by file MODIFIED time
    lstFiles.sort(key=os.path.getmtime)
    #lstFiles.sort(key=os.path.getctime) #created linux?
        
    strSetOutput = ""
    
    #respect intCount or less
    
    for strPostFile in lstFiles:
      #parse file results for article filename, title, date, author, (tags?), body, and formating
      dictBriefAttribs = blog_parsefile(strPostFile)
      
      if not isinstance(dictBriefAttribs, dict):
        strTypeOutput = type(dictBriefAttribs)
        strSetOutput = f"an unexpected error occurred during <b>BLOG RECENT: dictionary variable invalid type: [ {strTypeOutput} ]</b><br><br>[ var: {dictBlogAttrib} ]<br><br>"
        return strSetOutput
        
      strBriefFormat = blog_formatbrief(dictBriefAttribs)
      strSetOutput += strBriefFormat
      strSetOutput += "<br><br>"
    
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG RECENT Retrieve</b>: {e}<br><br>"
      return strSetOutput
  
  return strSetOutput
