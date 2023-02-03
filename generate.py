import gpt_2_simple as gpt2
import sys

sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess)

# Print is here because loading the session writes a ton of stuff to the terminal
print('========================\n')

comment = sys.argv[1]

# Length is in characters, temperature is how random (higher is more), prefix is what the comment starts with/replies to
gpt2.generate(sess, temperature=0.7, prefix='{"comment": "' + comment + '", "reply": "')