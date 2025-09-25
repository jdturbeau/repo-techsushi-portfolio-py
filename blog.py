#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
#import requests
import os #needed for chdir
import markdown

def blog_post(strPostFile):
  
  #check if file string is not null, then check if file exists
  with open(f"_posts/{strPostFile}", "r") as p:
    strContent = p.read()
  #strHTML = markdown.markdown(strContent)

  ##alt: return render_template("index.html", post_content=strHTML)
  return strContent

def blog_recent(intCount):

  if not intCount:
    intCount = 5
    
  os.chdir("_posts/")
  lstFiles = filter(os.path.isfile, os.listdir("_posts/"))
  lstFiles.sort(key=os.path.getmtime)
  
  return lstFiles
