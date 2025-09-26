#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
#import requests
import os #needed for chdirand getcwd
import markdown

def blog_post(strPostFile):
  
  try:
    #check if file string is not null, then check if file exists
    with open(f"/_posts/{strPostFile}", "r") as p:
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
    #if not intCount:
      #intCount = 5
    
    strCWD = os.getcwd()
    strSetOutput = f"0 current directory - [ {strCWD} ]<br>"
    #strCWD = os.path.dirname(os.path.realpath(__file__))
    #strSetOutput += f"1 current directory - [ {strCWD} ]<br>"
    
    os.chdir("/_posts/")
    strSetOutput += "1 chdir worked<br>"
    strCWD = os.getcwd()
    strSetOutput += f"2 current directory - [ {strCWD} ]<br>"
    '''
    #lstFiles = filter(os.path.isfile, os.listdir("/_posts/"))
    lstFiles = filter(os.path.isfile, os.listdir())
    strSetOutput += "2 filter worked<br>"
    
    lstFiles = [os.path.join("/_posts/", f) for f in lstFiles]
    strSetOutput += "3 pathjoin worked<br>"
    lstFiles.sort(key=os.path.getmtime)
    strSetOutput += "4 sort worked<br>"
    '''
  except Exception as e:
      #could contain sensitive information in error message
      strSetOutput += f"an unexpected error occurred during <b>BLOG RECENT</b>: {e}<br><br>" #{lstFiles}<br><br>"
      return strSetOutput
  
  return strSetOutput #lstFiles
