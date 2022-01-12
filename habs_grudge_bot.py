import os
import praw
import random
import re

enemy_list = ["SCHEIFELE", "KREIDER", "MARCHAND"]
enemy_name = "null"
signature = "\n***\n*^(bleep bloop)*"
name_count = 0

# Get PRAW credentials stored as environment variables.
USER_AGENT = os.getenv("HGB_USER_AGENT")
CLIENT_ID = os.getenv("HGB_CLIENT_ID")
CLIENT_SECRET = os.getenv("HGB_CLIENT_SECRET")
USERNAME = os.getenv("HGB_USERNAME")
PASSWORD = os.getenv("HGB_PASSWORD")

# Get file path to reply_tracker.
FILE_PATH = os.getenv("HGB_FILE_PATH")


# Insult crafting method.
def set_insult(enemy):
    insult_number = random.randint(1, 13)
    if insult_number == 1:
        insult_template = enemy + " couldn’t wheel a tire down a hill." + signature
    elif insult_number == 2:
        insult_template = enemy + "'s family tree is a wreath." + signature
    elif insult_number == 3:
        insult_template = enemy + " couldn't pour water out of a boot if the instructions were on the sole."\
                          + signature
    elif insult_number == 4:
        insult_template = "Anyone who ever loved " + enemy + " was wrong." + signature
    elif insult_number == 5:
        insult_template = enemy + " has the backbone of a chocolate eclair." + signature
    elif insult_number == 6:
        insult_template = enemy + " is as bright as a black hole and twice as dense." + signature
    elif insult_number == 7:
        insult_template = "If " + enemy + " were anymore inbred he would be a sandwich." + signature
    elif insult_number == 8:
        insult_template = enemy + " fights like a cow." + signature
    elif insult_number == 9:
        insult_template = "I'd try to insult " + enemy + ", but I can't top what nature has already accomplished."\
                          + signature
    elif insult_number == 10:
        insult_template = enemy + " is as thick as manure and only half as useful." + signature
    elif insult_number == 11:
        insult_template = "If " + enemy + "'s brains were dynamite, there wouldn't be enough to blow his hat off."\
                          + signature
    elif insult_number == 12:
        insult_template = enemy + " is just a hole in the air." + signature
    elif insult_number == 13:
        insult_template = enemy + " is ten-ply, bud." + signature
    return insult_template


# Get list of IDs for comments that have already been responded to.
if not os.path.isfile(FILE_PATH):
    reply_tracker = []
else:
    with open(FILE_PATH, "r") as file_handler:
        reply_tracker = file_handler.read()
        reply_tracker = reply_tracker.split("\n")
        reply_tracker = list(filter(None, reply_tracker))

# Connect via PRAW
reddit = praw.Reddit(
    user_agent=USER_AGENT,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD
)

# Live stream comments in subreddit.
for comment in reddit.subreddit("habs").stream.comments():
    # Reset name_count and enemy_name.
    enemy_name = "null"
    name_count = 0
    # Check comment against list of comments previously replied to. We only want to reply once per comment.
    if comment.id not in reply_tracker:
        # Remove any punctuation to allow target names to match punctuated strings.
        formatted_comment = re.findall(r'\w+', comment.body)
        # Loop through words in comment and look for a target enemy's name.
        for word in formatted_comment:
            if word.upper() in enemy_list:
                # If target name is found, format it with proper capitalization and increment name_count.
                enemy_name = word.capitalize()
                name_count += 1
        # Reply to comment only if target is acquired. Make sure bot is not replying to itself.
        # Also, the bot only want to take on lone enemies. It is a coward and more than one per comment is too much.
        if enemy_name != "null" and comment.author != "HabsGrudgeBot" and name_count == 1:
            # Call our function for insulting our target.
            insult = set_insult(enemy_name)
            # Reply with tailored insult.
            comment.reply(insult)
            # Monitoring
            print(comment)
            print(insult)
            # Record comment ID as being replied to.
            reply_tracker.append(comment.id)
            # Write reply_tracker to txt file for persisting record.
            with open(FILE_PATH, "w") as file_handler:
                for comment_id in reply_tracker:
                    file_handler.write(comment_id + "\n")

