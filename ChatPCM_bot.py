import praw
import gpt_2_simple as gpt2
from dotenv import load_dotenv
from os import getenv

load_dotenv()

numReplyCandidates = 3
maxReplyLength = 1000
checkpoint_dir = 'deep_based'
run_name = 'Key_Value0_1_plus3'
delimiter = '"}'

# Connect to Reddit
reddit = praw.Reddit(client_id = getenv("CLIENT_ID"),
            client_secret = getenv("CLIENT_SECRET"),
            user_agent = getenv("USER_AGENT"),
            username = getenv("USER_NAME"),
            password = getenv("PASSWORD"))

subreddit = reddit.subreddit('PoliticalCompassMemes')

sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess,
               checkpoint_dir = checkpoint_dir,
               run_name = run_name)

# Generate a comment using gpt-2-simple
def generateReply(temp, comment):
    return gpt2.generate(sess,
                  temperature=temp,
                  checkpoint_dir = checkpoint_dir,
                  run_name = run_name,
                  length = maxReplyLength,
                  nsamples = numReplyCandidates,
                  return_as_list = True,
                  prefix = comment)

def generateReplyList(inputComment):
    # Generate a list of replies
    
    reply_candidates_raw = []
    reply_candidates_raw += generateReply(0.7, inputComment)
    reply_candidates_raw += generateReply(0.9, inputComment)
    reply_candidates = []

    # Clean the replies and generate a list of pure reply text
    for reply in reply_candidates_raw:
        try:
            if delimiter in reply:
                reply_parts = reply.split(delimiter)
                reply = reply_parts[0].replace(inputComment, '')
                reply_candidates.append(reply)
        except:
            pass

    # Print organized list
    print("=====================")
    print(f"Comment: {inputComment}\n")
    for reply in reply_candidates:
        print(f"Reply:   {reply}\n")

# Go through comments
def readComments():
    for comment in subreddit.stream.comments():
        try:
            commentText = comment.body
            input = '{"' + commentText + '":"'
            try:
                parent = str(comment.parent())
                parentComment = reddit.comment(id=parent)
                parentText = parentComment.body
                input = parentText + ' }, ' + input
            except:
                pass
            generateReplyList(input)
        except:
            pass




while True:
    readComments()