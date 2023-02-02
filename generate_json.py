import json
import gpt_2_simple as gpt2


def find_last(s, c):  # Find the last occurrence of a given character
    idx = s.find(c)
    found = -1
    while idx != -1:
        found = idx
        idx = s.find(c, idx + 1)
    return found+1


print('Chat-PCM v0.0.1: Deep Based - Starting up...\n')
sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess)

comment = input('\nEnter your prompt:\n\n')
# comment = "Write your comment here if you don't want to enter it manually"

print()


# Length is in characters, temperature is how random (higher is more), prefix is what the comment starts with/replies to
output = gpt2.generate(
    sess, temperature=0.8, prefix='{"comment": "' + comment + '", "reply": "', return_as_list=True)[0]

pos = find_last(output, '}')
cleaned = '['+output[0:pos]+']'

# res = json.loads(cleaned)
# print(res)

file = open('output.json', 'w')
file.write(cleaned)
print('Text succesfully generated')
