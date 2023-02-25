import praw
import re
import gpt_2_simple as gpt2
from dotenv import load_dotenv
from os import getenv
import schedule
import time


numReplyCandidates = 3
maxReplyLength = 1000
temp = 0.1
window = 1  # Number of comments to pick from
flair = 'Centrist'  # Flair to generate as
replied = []    # Array of reddit ids of comments the bot has already replied to
replied_users = {} # Dict of users the bot has already replied to, paired with the number of responses it has generated {user: reply#}
submission_id = '' # Target submission under which to post. Remove once bot is released unrestricted
footer = "\n\n^(I'm a bot running a GPT-2 model created by the BasedCount team using PCM comments as training data. If you don't like anything I say, just remember who I was trained on.)"

MAX_TURN = 2 # number of clients running concurrently
CLIENT_TURN = 0 # when should this client post? this should always be lower than MAX_TURN

def main():
    load_dotenv()

    checkpoint_dir = 'deep_based'
    run_name = 'based100k_flairs - 72k'
    # run_name = 'based100k_flairs - 90k'

    # Connect to Reddit
    reddit = praw.Reddit(client_id=getenv("CLIENT_ID"), client_secret=getenv("CLIENT_SECRET"),
                         user_agent=getenv("USER_AGENT"), username=getenv("USER_NAME"), password=getenv("PASSWORD"))

    subreddit = reddit.subreddit('PoliticalCompassMemes')

    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_dir, run_name=run_name)

    schedule.every(20).minutes.do(reply_inbox, reddit=reddit,
                                 sess=sess, checkpoint_dir=checkpoint_dir, run_name=run_name)

    print()

    while True:
        schedule.run_pending()

        prefix = ''
        try:
            target = get_comment(subreddit=subreddit)
            reply = create_reply(target, reddit, sess,
                                 checkpoint_dir, run_name)

            if reply != '':
                replied.append(target.id)
                try:
                    out = target.reply(reply+footer)

                    print('New: https://reddit.com'+out.permalink)
                except Exception as e:   
                    print(str(e))        
                    pass

        except Exception as e:   
            print(str(e))        
            pass


# Fetch a comment's parent and generate a reply to it
def create_reply(target, reddit, sess, checkpoint_dir, run_name):
    prefix = ''
    try:
        parent = get_parent(reddit=reddit, comment=target)
        if parent != None:
            prefix = '{|'+get_flair(parent) + \
                '|'+parent.body+'}\n'
        prefix += '{|'+get_flair(target) + \
            '|'+target.body+'}\n'
        prefix += '{|'+flair+'|'
    except Exception as e:   
        print(str(e))        
        pass

    reply_raw = generate_reply(sess, checkpoint_dir, run_name, comment=prefix)
    return censor_words(reply_raw)


# Generate an answer to each unread reply
def reply_inbox(reddit, sess, checkpoint_dir, run_name):
    # Returns True with these probabilities per num:  0: 100%, 1: 90%, 2: 75%, 3: 40%, 4: 0%
    def quadratic_random_reply(num):
        try:
            if randrange(15)-(num ** 2) >= 0:
                return True
            return False
        except:
            return False

    # Fetch any unread message
    unread_messages = reddit.inbox.unread()
    # Filter the comments
    unread_replies = [message for message in unread_messages if isinstance(
        message, praw.models.Comment)]

    for reply in unread_replies:
        if reply.author not in replied_users.values():
            replied_users[reply.author] = 0
        
        if quadratic_random_reply(replied_users[reply.author]):
            try:
                generated_reply = create_reply(
                    reply, reddit, sess, checkpoint_dir, run_name)

                if generated_reply != '':
                    replied.append(reply.id)
                    try:
                        out = reply.reply(generated_reply+footer)
                        print('Reply: https://reddit.com'+out.permalink)
                    except Exception as e:   
                        print(str(e))        
                        pass
            except Exception as e:   
                print(str(e))        
                pass

        reply.mark_read()


# Return the longest out of WINDOW comments
def get_comment(subreddit):
    # Function for client side validation. Clients should modify this according to their preferences
    def validate_comment(comment):
        # Only post if it's your turn, I.E. COMMENT_TIMESTAMP % MAX_TURN = CLIENT_TURN 
        if not comment.created_utc % MAX_TURN == CLIENT_TURN:
            return False
        # Avoid bot comments
        if comment.author in ["basedcount_bot", "flairchange_bot", "flair-checking-bot", "ChadGPT_bot"]:
            return False
        if comment.id in replied:   # Avoid double answers
            return False
        return True

    target = None
    target_body = ''
    accepted = 0

    for comment in subreddit.stream.comments():
        # Only listen to comments posted under the target submission
        if comment.submission.id == submission_id:
            # Match WINDOW valid comments
            if validate_comment(comment):
                try:
                    # Return the longest of them
                    if len(comment.body) > len(target_body):
                        target = comment
                        target_body = comment.body

                    accepted += 1

                    if accepted >= window:
                        return target
                except Exception as e:   
                    print(str(e))        
                    pass


# Return a comment's parent comment or None
def get_parent(reddit, comment):
    # If parent is not a comment return None
    if not comment.parent_id.startswith('t1_'):
        return None

    try:
        # If parent is a comment, try to fetch it and return it
        return reddit.comment(id=comment.parent_id)
    except Exception as e:   
        print(str(e))        
        return None


# Return a flair in the flairchange_bot format from a Reddit flair ID
def get_flair(comment):
    flair_id = None
    if 'author_flair_template_id' in vars(comment):
        flair_id = comment.author_flair_template_id
    else:
        return 'Unflaired'

    match flair_id:
        case "349ce882-e94e-11e9-bbc4-0e871e36a27e":
            return "Centrist"
        case "42a2355c-e950-11e9-b1c0-0ecdd039149e":
            return "Right"
        case "47a39016-e94e-11e9-9211-0e435e52671c":
            return "LibLeft"
        case "3bd134fa-e94e-11e9-abf5-0e0b2c36e72c":
            return "AuthRight"
        case "46901708-bd3d-11ea-9a8a-0e03ab8df87b":
            return "Grey Centrist"
        case "32035b7c-e950-11e9-9aae-0e7bbe7acab2":
            return "Left"
        case "23ccb4fe-e950-11e9-bccc-0e6fbc667050":
            return "AuthCenter"
        case "392244cc-e950-11e9-8907-0e72bdac403c":
            return "LibCenter"
        case "43071082-e94e-11e9-bdb8-0e39be98ce58":
            return "AuthLeft"
        case "4d9deb08-97b6-11ea-b242-0ee47404e435":
            return "Purple LibRight"
        case "4b819f98-e94e-11e9-9449-0e2d25175ad0":
            return "LibRight"
        case None:
            return "Unflaired"
    return "Unflaired"


# Generate a reply
def generate_reply(sess, checkpoint_dir, run_name, comment):
    reply_candidates_raw = gpt2.generate(sess, temperature=temp, checkpoint_dir=checkpoint_dir, run_name=run_name,
                                         length=maxReplyLength, nsamples=numReplyCandidates, return_as_list=True, prefix=comment)

    delimiter = '}'
    reply_candidates = []

   # Clean the replies and generate a list of pure reply text
    for reply in reply_candidates_raw:
        try:
            candidate = reply.replace(comment, '')  # Remove the prompt
            # Keep only the first reply
            candidate = candidate[:candidate.index(delimiter)]
            candidate = candidate[1:-1]  # Remove wrapping commas
            reply_candidates.append(candidate)
        except Exception as e:   
            print(str(e))        
            pass

    reply = ''

    # Return the longest generated reply
    for candidate in reply_candidates:
        if len(candidate) > len(reply):
            reply = candidate

    output = ''
    try:
        # If the answer isn't clean yet, do another extraction pass
        if ('{' in reply) or ('}' in reply) or ('|' in reply):
            match = re.search(r"{\|[a-zA-Z]+\|(.+)", reply, re.MULTILINE)
            output = match.group(1)
        else:
            output = reply
    except Exception as e:   
        print(str(e))        
        output = reply  # Improve by removing everything before the second '|' and the last '"'

    return output


# Censor every bad word contained in a string
def censor_words(text):
    # List of patterns making up a no-no word. Courtesy of the PCM mods
    patterns = ["(n+|И|ń|ñ|ℕ|Ｎ|ｎ|Ņ|η|ň|ŉ|ŋ|Ƞ|ͷ|ƞ|ǹ|ɳ|ɴ|п|π|И́|ӣ|и̃|ҋ|ӥ|ṅ|ṇ|ṉ|ṋ|ꞥ|ᵰ|ᶇ|ȵ|冂|ᴎ͔|ɴ́)(i+|l|í|î|ï|ì|1|エ|Ⅰ|і|ị|¡|ι|[|]|І|ĩ|į|ȉ|Ї|ȋ|Ϊ|ί|ǐ|ɨ|ɩ|ɪ|!|j|ı|ℹ|ꮖ|ꭵ|Ꮖ|Ꭵ|y|ī)(g+|q+|bb|פפ|ßß|ББ|бб|ВВ|ǥǥ|ƄƄ|ƅƅ|ĝĝ|ġġ|ǥǥ|ğğ|ĝĝ|ǧǧ|ɡɡ|ģģ|ɢɢ|ββ|ꮐꮐ|ᏩᏩ|\U0001F171\U0001F171|\U0001F171\uFE0F\U0001F171\uFE0F|ᶃᶃ|ꞡꞡ|ḡḡ|ɠɠ|66)(let|l3t|nog|a|à|á|â|ä|ã|å|ā|а|ӓ|ą|ȁ|ȃ|ɑ|ă|а̊|а̃|ӓ|ӓ̄|4|æ|α|ᾰ|ᾱ|a̮|(e+|3|З|Е|ε|Ɛ|è|é|ê|ë|ē|ė|ę|е|ě|ȅ|ȩ|ё|ȇ|ѐ|ӗ|ӗ|е̄|е̃|ё̄|Ꭼ|ꭼ|ヨ|∈|a)(r+|г|ŗ|ŕ|ɍ|ř|ȑ|ȓ|ɼ|ℝ|Ꮢ|ꭱ|Я|Я̆|Я̄|Я̈|ʀ|ɾ|ṙ|ṛ|ṝ|ṟ|ꞧ|Ɽ|r̃|ᵲ|ᴚ))(s*|z|ino|man|retard|etard)",
                "nggrs", "fag", "fags", "Нигг(ер|эр|a)", "ニガー", "黑鬼", "k(i|y)(ke|kes|k3|k3s)", "卐", "joggers?", "ngr", "nigs", "tranny", "trannies", "faggot", "faggots", "niglet", "chink", "beaner", "nig-nog", "nignog", "pikey", "subhuman", "sub-human", "sub human", "troon", "troons", "retard", "retarded"]

    # Combine regex patterns into a single pattern
    combined_pattern = re.compile('|'.join(patterns), re.IGNORECASE)

    # Define the function to replace matched text
    def repl_func(match):
        word = match.group(0)
        return '*'*len(word)

    # Censors the R slur in the given text and replaces it with "redditor" and "reddited".
    def censor_r_slur(text):
        redditor_pattern = r'\b(\W*)(r|R)(etard|ETARD)\b'
        reddited_pattern = r'\b(\W*)(r|R)etarded\b'
        return re.sub(reddited_pattern, r'\1reddited', re.sub(redditor_pattern, r'\1redditor', text))

    # Unescape any escaped characters from the generated answer (dataset contains escaped characters)
    def restore_escaped_chars(string):
        return string.encode('utf-8').decode('unicode_escape')

    text = censor_r_slur(text)

    # Use sub() method to replace matched text with censored text
    censored_text = combined_pattern.sub(repl_func, text)

    return restore_escaped_chars(censored_text)


if __name__ == "__main__":
    main()
