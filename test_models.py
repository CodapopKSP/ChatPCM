import gpt_2_simple as gpt2
import os

numReplyCandidates = 3
maxReplyLength = 300
temp = 0.7

prompts = [
    "{|AuthRight|He was a good person, and it’s hard for a good person to be a good president}\n{|Centrist|It's hard for a good person to even become elected to assitant deputy library adjunct administrator.}",
    "{|LibCenter|I mean she's European and talks more about global warming and European shit}\n{|LibCenter|Fact: Greta didn't do shit to stop the BP oil spill.}",
    "{|LibCenter|Now companies will require women to prove menstruation lol}\n{|AuthRight|I mean it’s pretty easy HR policy to implement. Would just make a policy stating women \"are able to claim a max of 5 menstrual days in a given month and can only claim it twice within a month (ex: can’t split the days to have a menstrual day every week Tuesday).\"}",
    "{|Right|> sending billions of dollars to Ukraine\n\nreddit: yay this is cool, I can see Russians die from an HD camera\n\n> train derails in Ohio causing chemical spill\n\nreddit: Trump literally did this}\n{|LibLeft|An actual fair assessment of of why FEMA isn't taking the lead on this:\n\n\nhttps://www.foxnews.com/politics/white-house-explains-why-turned-down-disaster-relief-ohio\n\n\n\nThere needs to be federal legislation to address the issue, work on long term compensation, environmental hazards, etc. \n\n\n\nFEMA short term housing isn't a long term solution. As the articles notes, there's about a dozen federal agencies assisting Ohio currently. Including FEMA in coordinating with the local FEMA offices. \n\n\n---------------\n\nAlso, as others have pointed out, Governor DeWine was slow to declare an emergency. And he says the air and water are fine.\n\n\n>DeWine: \"Science indicates that this water is safe. The air is safe.\"\n\n\n\nhttps://spectrumnews1.com/oh/columbus/news/2023/02/18/the-ohio-department-of-health-helps-east-palestine-move-forward-with-clinic\n\n\n\nHe's been saying that pretty consistently for the past 4 days. But local environmental nonprofits seem generally concerned still: https://www.sierraclub.org/ohio/blog/2023/02/urge-gov-dewine-declare-state-emergency-ohio-and-listen-demands-east-palestine\n\n\n\nIf I lived there, I would not trust Governor DeWine's assurances. I'd like to see him drink a glass of it.}",
    "{|LibCenter|Identity politics was always a psyop to get the left to stop caring about economic justice for all and be satisfied with fake token victories for selected groups.}\n{|LibLeft|Nah. More accurately, people promoted \"equality\" not to actually gain it, but as a way to increase their own power and influence. Once that is achiever, they augment the meaning of \"equality\" in order to gain even more power.}"
]


def main():
    # Choose which model you are using
    checkpoint_dir = resource_path('deep_based')

    models = ["based100k_flairs - 90k v2", "based100k_flairs - 90k v1.5",
              "based100k_flairs - 72k",  "based100k_flairs - 45k"]

    run_name = models[0]
    print(run_name)

    # Start gpt2
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess,
                checkpoint_dir=checkpoint_dir,
                run_name=run_name)

    for prompt in prompts:
        reply = generate_comments(prompt, sess, checkpoint_dir, run_name)
        # print(f"Comment:   {prompt}\n")
        print(f"Reply:   {reply}\n")


# Get absolute path to resource, works for dev and for PyInstaller - I got this from StackOverflow but it works
def resource_path(relative_path):

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Generate a comment using gpt-2-simple
def generateReply(comment, sess, checkpoint_dir, run_name):
    return gpt2.generate(sess,
                         temperature=temp,
                         checkpoint_dir=checkpoint_dir,
                         run_name=run_name,
                         length=maxReplyLength,
                         nsamples=numReplyCandidates,
                         return_as_list=True,
                         prefix=comment)


def generate_comments(prompt, sess, checkpoint_dir, run_name):
    # String manipulation to allow for parsing of data
    delimiter = '"}'
    comment_with_parsers = prompt +"\n{|AuthLeft|"

    # Generate a list of replies
    reply_candidates_raw = []
    reply_candidates_raw += generateReply(comment_with_parsers,
                                          sess, checkpoint_dir, run_name)
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
    
    chosen_reply = ""
    for reply in reply_candidates:
        if len(reply) > len(chosen_reply):
            chosen_reply = reply

    return chosen_reply


if __name__ == "__main__":
    main()
