import praw
from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Connect to Reddit
reddit = praw.Reddit(client_id=getenv("CLIENT_ID_"), client_secret=getenv("CLIENT_SECRET_"),
                        user_agent=getenv("USER_AGENT_"), username=getenv("USER_NAME_"), password=getenv("PASSWORD_"))

subreddit = reddit.subreddit('PoliticalCompassMemes')

unread_messages = reddit.inbox.unread()

for message in unread_messages:
    comment = reddit.comment(message.id)
    print('https://reddit.com'+comment.permalink)