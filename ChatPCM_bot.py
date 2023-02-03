import praw
import gpt_2_simple as gpt2
from dotenv import load_dotenv
from os import getenv

load_dotenv()

reddit = praw.Reddit(client_id = getenv("CLIENT_ID"),
            client_secret = getenv("CLIENT_SECRET"),
            user_agent = getenv("USER_AGENT"),
            username = getenv("USER_NAME"),
            password = getenv("PASSWORD"))

subreddit = reddit.subreddit('PoliticalCompassMemes')

def readComments():
    try:
        for comment in subreddit.stream.comments():
            print(comment.body)
    except:
        pass

while True:
    readComments()