#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
#import requests
import os #needed for chdir
import markdown

def blog_post(strPostFile):
  
  try:
    #check if file string is not null, then check if file exists
    with open(f"./_posts/{strPostFile}", "r") as p:
      strContent = p.read()
    #strHTML = markdown.markdown(strContent)
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG GET</b>: {e}<br><br>"
      return strSetOutput
  ##alt: return render_template("index.html", post_content=strHTML)

  return strContent

def blog_recent(intCount):

  try:
    if not intCount:
      intCount = 5
      
    os.chdir("./_posts/")
    #lstFiles = filter(os.path.isfile, os.listdir("./_posts/"))
    lstFiles = filter(os.path.isfile, os.listdir())
    lstFiles = [os.path.join("./_posts/", f) for f in files]
    lstFiles.sort(key=os.path.getmtime)
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput = f"an unexpected error occurred during <b>BLOG RECENT</b>: {e}<br><br>"
      return strSetOutput
  
  return lstFiles
