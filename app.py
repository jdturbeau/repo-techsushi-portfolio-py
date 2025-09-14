from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

app = Flask(__name__)

@app.route("/")
def index():
   return render_template("index.html")

@app.route("/demo")
def demo():
   return render_template("/demo/index.html")

@app.route("/keysset")
def keysset():
   strWebOutput = "begin keysset<br><br>"
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url="https://kv-techsushi-site.vault.azure.net/", credential=credential)
      secret = secret_client.set_secret("api-reddit-id", "nn-FtOW2w8zz7stJwwojIQ")
      secret = secret_client.set_secret("api-reddit-secret", "YXcEaaKMLVnXEYTF1vSi7TOU1q4Edg")
      secret = secret_client.set_secret("api-reddit-tokentype", "bearer")
      #secret = secret_client.set_secret("api-reddit-token", "eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJsb2lkIiwiZXhwIjoxNzU2NzY2MTg3LjA0Mjc3LCJpYXQiOjE3NTY2Nzk3ODcuMDQyNzcsImp0aSI6IkVDM2NSdzYyUllPdWhHS0FtQWRNOTRxTFJNbmZ5USIsImNpZCI6Im5uLUZ0T1cydzh6ejdzdEp3d29qSVEiLCJsaWQiOiJ0Ml8xd3VqZWkybHU5IiwibGNhIjoxNzU2Njc5Nzg3MDI3LCJzY3AiOiJlSnlLVnRKU2lnVUVBQURfX3dOekFTYyIsImZsbyI6Nn0.QKYFkS3OvsU0vSG1LC5-0CFsS-BaprNMISwUCmC9GQVNcUxuQkA5-kxixNWYDwBXfIphmbOaXlMj57qKeszCFYruA1tonfYI0Ac2fOsT8eTyA_MAK_ZGtNLYH_xsO7HCws2-Q0xqeJBPNXnAc7eoiWNiTR1WYH8UFoWnrH1zoDbxHVNo45IlF1XOyJqhCBHUQIVqkL05ASEFnjB3qv3JRcP2pT0reBUjHeU_DSj4XR4YbEiDA5FxrHS5tjYkY-tZjR1IgYI4kmwFwBgrE06wbxamL4ZpM1E5xxJdWpO1VlvwsJuntpYoyg8fXtfFK9duvcGLp0GE3NIm0TptlHqX6Q")
      secret = secret_client.set_secret("api-reddit-token", "abcd")
      strWebOutput += f"{secret.name}<br><br>"
      strWebOutput += f"{secret.value}<br><br>"
      strWebOutput += f"{secret.properties.version}<br><br>"      
   except Exception as e:
      strWebOutput += f"an unexpected error occurred during set: {e}<br><br>"
   else:
      strWebOutput += f"set completed without error<br><br>"
   finally:
      strWebOutput += "end of set<br><br>"

   return strWebOutput

@app.route("/keysget")
def keysget():
   strWebOutput = "begin keysget<br><br>"
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url="https://kv-techsushi-site.vault.azure.net/", credential=credential)
      secret = secret_client.get_secret("api-reddit-token")
      strWebOutput += f"{secret.name}<br><br>"
      strWebOutput += f"{secret.value}<br><br>"
      secret = secret_client.get_secret("api-reddit-tokentype")
      strWebOutput += f"{secret.name}<br><br>"
      strWebOutput += f"{secret.value}<br><br>"
      secret = secret_client.get_secret("api-reddit-id")
      strWebOutput += f"{secret.name}<br><br>"
      strWebOutput += f"{secret.value}<br><br>"
      secret = secret_client.get_secret("api-reddit-secret")
      strWebOutput += f"{secret.name}<br><br>"
      strWebOutput += f"{secret.value}<br><br>"
   except Exception as e:
      strWebOutput += f"an unexpected error occurred during get: {e}<br><br>"
   else:
      strWebOutput += f"get completed without error<br><br>"
   finally:
      strWebOutput += "end of get script<br><br>"

   return strWebOutput


@app.route("/refreshtoken")
def refreshtoken():
   try:
      strWebOutput = "begin retrieve credentials<br><br>"
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url="https://kv-techsushi-site.vault.azure.net/", credential=credential)
      secret = secret_client.get_secret("api-reddit-id")
      strID = secret.value
      secret = secret_client.get_secret("api-reddit-secret")
      strSecret = secret.value
      strWebOutput += f"ID: {strID}<br><br>Sec: {strSecret}<br><br>"
   except Exception as e:
      strWebOutput += f"Trouble retrieving id credentials from kv, review: {e}<br><br>"
      return strWebOutput

   try:
      strURL = "https://www.reddit.com/api/v1/access_token"
      objClientAuth = (strID, strSecret)
      dictPostData = { "grant_type": "client_credentials" }
      dictHeader = { "User-Agent": "imgdupedetect v0.1 by orbut8888" }
      roReceived = requests.post(strURL, auth=objClientAuth, data=dictPostData, headers=dictHeader)
      strWebOutput += f"{roReceived.status_code}<br><br>{roReceived.text}<br><br>{roReceived.content}<br><br>{roReceived.headers}<br><br>"
      strWebOutput += f"Attempting to parse response for JSON...<br><br>"
      dictReceived = roReceived.json()      
      strToken = dictReceived["access_token"]
      strWebOutput += f"Attempting to store token...<br><br>"
      secret = secret_client.set_secret("api-reddit-token", strToken)
      strTokenType = dictReceived["token_type"]
      secret = secret_client.set_secret("api-reddit-tokentype", strTokenType)
      strWebOutput += f"new token stored!<br><br>{strToken}<br><br>{strTokenType}<br><br>"
   except Exception as e:
      strWebOutput += f"Trouble with POST or JSON, review {e}<br><br>{roReceived}<br><br>"
      return strWebOutput
   else:
      strWebOutput += f"post json complete successfully"
   finally:
      strWebOutput += f"post json complete"
   return strWebOutput

@app.route("/getcontent")
def getcontent():
   '''
    #, methods=['GET', 'POST'])
   if request.method == 'POST':
      strSubReddit = request.form['sub']
   else
      strSubReddit = "p320"
   
   strSubReddit = request.form['sub']
   if not strSubReddit:
  '''
   
   strSubReddit = "p320"
   
   strWebOutput = f"begin data retrieval of subreddit: {strSubReddit}<br><br>"
   try:
      credential = DefaultAzureCredential()
      secret_client = SecretClient(vault_url="https://kv-techsushi-site.vault.azure.net/", credential=credential)
      strTokenType = secret_client.get_secret("api-reddit-tokentype").value
      strToken = secret_client.get_secret("api-reddit-token").value
      strWebOutput += f"{strTokenType}<br><br>"
      strWebOutput += f"{strToken}<br><br>"
   except Exception as e:
      strWebOutput += f"an unexpected error occurred during token retrieval: {e}<br><br>"
      return strWebOutput
   
   try:
      strWebOutput += "end of get token from kv script<br><br>"
      dictHeader = { "Authorization": f"{strTokenType} {strToken}", "User-Agent": "imgdupedetect v0.1 by orbut8888" }
      strURL = f"https://oauth.reddit.com/r/{strSubReddit}/new"
      strWebOutput += f"{dictHeader}<br><br>"
      roReceived = requests.get(strURL, headers = dictHeader)
      # if roReceived.status_code = 401 (unauthorized), likely need new token
      strWebOutput += f"{roReceived.status_code}<br><br>{roReceived.text}<br><br>{roReceived.content}<br><br>{roReceived.headers}<br><br>"
      dictJson = roReceived.json()
      strAfterURL = dictJson["data"]["after"]
      strWebOutput += f"{strAfterURL}<br><br>"
      strWebOutput += f"text received: [ {roReceived} ]<br><br>"
   except Exception as e:
      strWebOutput += f"an unexpected error occurred during token usage: {e}<br><br>"
      return strWebOutput
   else:
      strWebOutput += f"usage completed without error<br><br>"
   finally:
      strWebOutput += "usage2 completed<br><br>"
   
   try:
      dictThreads = dictJson["data"]["children"]
      
      strWebOutput = f"<head><base href=\"https://www.reddit.com/\" target=\"_blank\"></head><body>"
      
      for dictSingle in dictThreads:
         strThreadTitle = dictSingle["data"]["title"]
         strThreadAuthor = dictSingle["data"]["author"]
         strThreadPermalink = dictSingle["data"]["permalink"]
         strThreadComments = dictSingle["data"]["num_comments"]
         strThreadURL = dictSingle["data"]["url"]
         strThreadMedia = dictSingle["data"]["media"]
         strThreadType = dictSingle.get("data", {}).get("post_hint", "Missing")
         strWebOutput += f"<font size=5><a href=\"{strThreadPermalink}\">{strThreadTitle}</a></font><br>"
         strWebOutput += f"<b>{strThreadAuthor}</b> - {strThreadComments} Comment(s) / Post Type - {strThreadType}<br><p>"
         match strThreadType:
            case "image":
               strWebOutput += f"<img src =\"{strThreadURL}\" width=\"60%\"></img><p>"
            case _:
               strWebOutput += f"<font color=red>Error experienced [ {strThreadType} ]</font><p>"
      strWebOutput += f"<p><a href=\"{strAfterURL}\">Next Posts</a></p>"

   except Exception as e:
      strWebOutput += f"Trouble with JSON, review: {e}<br><br>{dictThreads}<br><br>"
      return strWebOutput
   else:
      strWebOutput += "json parse complete without error<br><br>"
   finally:
      strWebOutput += "json parse completed<br><br>"

   return strWebOutput

if __name__ == '__main__':

  app.run(debug=True)












