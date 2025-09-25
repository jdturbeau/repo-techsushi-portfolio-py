#from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
#import requests
#import os
#import markdown

def blog_post(strPostFile):
  
  with open(f"_posts/{strFile}", "r") as p:
    strContent = p.read()
  #strHTML = markdown.markdown(strContent)

  ##alt: return render_template("index.html", post_content=strHTML)
  return strContent

def blog_recent(intCount):
  return
