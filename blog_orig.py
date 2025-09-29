#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
#import requests
import os #needed for chdir and getcwd
import markdown
import re

def blog_post(strPostFile):
  
  '''
  try:
    #check if file string is not null, then check if file exists
    with open(f"_posts/{strPostFile}", "r") as p:
      strContent = p.read()
    #strHTML = markdown.markdown(strContent)
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG GET</b>: {e}<br><br>"
      return strSetOutput
  ##alt: return render_template("index.html", post_content=strHTML)
  '''
  return #strContent

def blog_recent(intCount):

  try:
    if not intCount:
      intCount = 5
    
    #app_path typically temp folder, such as '/tmp/8ddfd43c8909fcd'
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
      lstBlogAttrib = blog_postparse(strPostFile)
      strBriefFormat = blog_briefformat(lstBlogAttrib)
      strSetOutput += strBriefFormat
    
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG RECENT Retrieve</b>: {e}<br><br>"
      return strSetOutput
  
  return strSetOutput

def blog_postparse(strParseFile):

  try:
    #check if file string is not null
    #  then check if file exists
    with open(f"_posts/{strParseFile}", "r") as p:
      strParseContent = p.read()
    
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG GET</b>: {e}<br><br>"
      return strSetOutput
  ##alt: return render_template("index.html", post_content=strHTML)
  
  strPattern = r"(?<=title: ).*"   #gi - use re.ignorecase below
  strTitle = re.search(strPattern, strParseContent, re.IGNORECASE
  strPattern = r"(?<=date: ).*"   #gi - use re.ignorecase below
  strDate = re.search(strPattern, strParseContent, re.IGNORECASE)
  strPattern = r"(?<=author: ).*"   #gi - use re.ignorecase below
  strAuthor = re.search(strPattern, strParseContent, re.IGNORECASE)
  #future
  #strPattern = r"(?<=tags: ).*"   #gi - use re.ignorecase below
  #strTags = re.search(strPattern, strParseContent, re.IGNORECASE)
  strPattern = r"(?<=-----\n)[\s\S]*"   #gi - use re.ignorecase below
  strBody = re.search(strPattern, strParseContent, re.IGNORECASE)

  dictParsed = {"File": strParseFile, "Title": strTitle, "Date": strDate, "Author": strAuthor, "Body": strBody}
  return dictParsed

def blog_postformat(dictPostAttribs):
  #strHTML = markdown.markdown(strContent)
  return

def blog_briefformat(dictBriefAttribs):

  #verify dictBriefAttribs first
  #File for filename, may need to trim, used for crafting link
  strBrief
  
  return

  
def blog_notes():
  '''
    
    strCWD = os.getcwd()
    strSetOutput = f"0 current directory - [ {strCWD} ]<br>"
    #strCWD = os.path.dirname(os.path.realpath(__file__))
    #strSetOutput += f"1 current directory - [ {strCWD} ]<br>"
    
    #contents = os.listdir(app_root)

    #for item in contents:
      #strSetOutput += f"{item}"
      
    #file_path = os.path.join(app_root, '_posts', '2025-0925-welcome.md')
    #strSetOutput += f"3 file path after joins - [ {file_path} ]<br>"
    
    #with open(f"{file_path}", "r") as p:
      #strContent = p.read()

    #strSetOutput += f"4 file content - [ {strContent} ]"
    
    os.chdir("_posts") #avoid... chdir impacts actions going forward and on other pages
    strSetOutput += "1 chdir worked<br>"
    strCWD = os.getcwd()
    strSetOutput += f"2 current directory - [ {strCWD} ]<br>"

    #lstFiles = filter(os.path.isfile, os.listdir())
    strSetOutput += f"3 filter worked<br>"
    
    strSetOutput += f"4 files listing worked [ {lstFiles} ]<br><br>"

    strSetOutput += f"5 path join worked [ {lstSortedFiles} ]<br><br>"
    strSetOutput += "6 sort worked<br>"
    strSetOutput += f"7 sort worked [ {lstSortedFiles} ]<br><br>"
  
  '''
  return
