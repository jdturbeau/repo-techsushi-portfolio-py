def redditimagescrape():
    #import requests
    
    strID = "nn-FtOW2w8zz7stJwwojIQ"
    strST = "YXcEaaKMLVnXEYTF1vSi7TOU1q4Edg"
    
    strURL = "https://www.reddit.com/api/v1/access_token"
    objClientAuth = (strID, strST)
    dictPostData = { "grant_type": "client_credentials" }
    dictHeader = { "User-Agent": "imgdupedetect v0.1 by orbut8888" }
    strWebOutput = "made it"

    roReceived = requests.get(f"{strURL}{strURLParam}", headers=dictHeader)
    #try
    #roReceived = requests.get(strURL)
    #roReceived = requests.post(strURL, auth=objClientAuth, data=dictPostData, headers=dictHeader)
    #strWebOutput = roReceived #.status_code

    #except requests.exceptions.RequestException as e:
    #print(f"An error occurred: {e}")
    #strWebOutput = e
    
    return strWebOutput
