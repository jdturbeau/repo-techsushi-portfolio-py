from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
#import redditmedia

app = Flask(__name__)

@app.route("/")
def index():
   #return render_template("index.html")
  strWebOutput = "<head>"
  strWebOutput += "<title>TechSushi - Portfolio</title>"
  strWebOutput += "</head>"
  strWebOutput += "<body>Welcome to the Tech Sushi - Portfolio page<br><br><br>"
  strWebOutput += "Would you like to visit:<br><br>"
  strWebOutput += "<a href=\"/keysset\">KV set</a><br><br>"
  strWebOutput += "<a href=\"/keysget\">KV retrieve</a><br><br>"
  strWebOutput += "<a href=\"/demo\">demo second page routing</a><br><br>"
  strWebOutput += "<a href=\"/refreshtoken\">refresh api token</a><br><br>"
  strWebOutput += "<a href=\"/getcontent\">use api token to get content</a><br><br>"
  strWebOutput += "<a href=\"/testpost\">test posting value</a><br><br><br>"
  strWebOutput += "</form><br><br><br><br>"
  strWebOutput += "Run through version [060]</body>"
  
  return strWebOutput
