import gpt_2_simple as gpt2
import os

# Get absolute path to resource, works for dev and for PyInstaller - I got this from StackOverflow but it works
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

numReplyCandidates = 3
maxReplyLength = 300

# Choose which model you are using
checkpoint_dir = resource_path('deep_based')
# checkpoint_dir = 'deep_based'
run_name = 'based100k_flairs - 90k'

# Start gpt2
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess,
               checkpoint_dir = checkpoint_dir,
               run_name = run_name)

inputComment = input('\nEnter your prompt: ')

# String manipulation to allow for parsing of data
delimiter = '"}'
comment_with_parsers = '{|LibLeft|"' + inputComment + '"}\n{|Centrist|"'

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

# Generate a list of replies
reply_candidates_raw = []
reply_candidates_raw += generateReply(0.7, comment_with_parsers)
reply_candidates_raw += generateReply(0.9, comment_with_parsers)
reply_candidates = []

# Clean the replies and generate a list of pure reply text
for reply in reply_candidates_raw:
    try:
        if delimiter in reply:
            reply_parts = reply.split(delimiter)
            reply = reply_parts[1].replace(comment_with_parsers, '')
            reply = reply.replace('{', '', 1)
            reply = reply.replace('"', '', 1)
            reply_candidates.append(reply)
    except:
        pass

# Print organized list
print()
for reply in reply_candidates:
    print(f"Comment: {inputComment}")
    print(f"Reply:   {reply}\n")
os.system("PAUSE")