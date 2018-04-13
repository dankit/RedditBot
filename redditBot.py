import praw
import requests
import re
import urllib.request
from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from google.cloud import vision
from google.cloud.vision import types
import os

def search(reddit,comment_list):
    print("Fetching comments!")
    subreddit = reddit.subreddit('test')
    print("Subreddit set to:'{}'".format(subreddit))
    imageContentTypes = ['image/png','image/jpeg','image/png','image/jpg']
    for submission in subreddit.hot(limit=1): #how many threads to fetch
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            if comment not in comment_list:
              s = comment.body
              findUrlsList = re.findall('http[s]?://[a-zA-Z0-9.%^/]*',s) #finds all URLS via regex in the iterated comments
              if len(findUrlsList) != 0:
                  for url in findUrlsList:
                      contentType = getHeaderType(url)
                      if contentType in imageContentTypes:
                          print("URL found: {} \n Content Type = {}".format(url,contentType))
                          imageText = detect_text_uri(url)
                          if imageText != '':
                              print('text = {} \nreplying to comment!'.format(imageText))
                              comment.reply("Image transcription:\n\n{} \n\n I'm a bot!".format(imageText))
                              addCommentToFile(comment.id)
 

       
            
def getHeaderType(url):
    try:
        return requests.head(url).headers['Content-Type']
    except:
        print("Website sent invalid request!")

def initialize():
    reddit = praw.Reddit(client_id='INSERT YOUR OWN INFORMATION HERE',
                     client_secret='INSERT YOUR OWN INFORMATION HERE',
                     password='INSERT YOUR OWN INFORMATION HERE',
                     user_agent='INSERT YOUR OWN INFORMATION HERE',
                     username='INSERT YOUR OWN INFORMATION HERE')
    print("Initialization successful! Logged in as: {}".format(reddit.user.me()))
    return(reddit)

def main():
    reddit = initialize()
    comment_list = repliedTo()
    visionAPIauth()
    print("Currently {} Items in comment list".format(len(comment_list)))
    search(reddit,comment_list) #can add a while true statement to continously run the program!

def addCommentToFile(commentID):
    file = open("commentReplies.txt",'a+')
    file.write(commentID)
    file.close()


def repliedTo():  #for when program is closed annd reopened, makes sure it doesn't duplicate a reply
    file = open("commentReplies.txt",'a+') #read and write mode
    file.seek(0) #a+ mode allows you to append items to text file, but goes to the end of the file, use seek to go back to the top to read it
    replied_comments = []  
    for line in file:
        if line not in replied_comments: #ensures no duplicates
            replied_comments.append(line)
    file.close()
    return(replied_comments)

def visionAPIauth(): #authenticate via json file credentials on local machine, then calls the text detector   
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="INSERT YOUR OWN INFORMATION HERE(JSON FILE CREDS PATH, DOWNLOADED FROM GOOGLE CLOUD PLATFORM -> SERVICE ACCOUNT)" #double backslash to prevent unicode error message
    
def detect_text_uri(uri): #mostly taken from https://cloud.google.com/vision/docs/detecting-text#vision-text-detection-python
    """Detects text in the file located in Google Cloud Storage or on the Web.
    """
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    image.source.image_uri = uri
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return(texts[0].description) #returns text of image

if __name__ == '__main__': #so that it runs the program as a whole, if people want to import functions
         main()             #then it does not run the whole program, and they can run individual functions
                             #put at bottom so it can read all the code above
