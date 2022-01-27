import os
import praw
import random
import re
import yaml

enemy_list = []
insult_list = []
previous_replies = []

FILE_PATH = os.getenv("HGB_FILE_PATH")


def main():
    global insult_list
    global enemy_list
    global previous_replies
    insult_list = populate_insults()
    enemy_list = populate_enemies()
    previous_replies = get_previous_replies()
    stream_comments()


def populate_insults():
    """ Populate insults from config file. """

    with open('insults.yaml') as file:
        try:
            stored_insults = yaml.safe_load(file)
            return stored_insults["insults"]
        except yaml.YAMLError as exception:
            print(exception)


def populate_enemies():
    """ Populate enemies from config file. """

    with open('enemies.yaml') as file:
        try:
            stored_insults = yaml.safe_load(file)
            return stored_insults["enemies"]
        except yaml.YAMLError as exception:
            print(exception)


def get_previous_replies():
    """ Get list of IDs for comments that have already been responded to. """
    if not os.path.isfile(FILE_PATH):
        stored_replies = []
        return stored_replies
    else:
        with open(FILE_PATH, "r") as file:
            stored_replies = file.read()
            stored_replies = stored_replies.split(",")
            stored_replies = list(filter(None, stored_replies))
            return stored_replies


def build_insult(enemy):
    """ Craft the perfect personalized insult. """

    signature = "\n***\n*^((this will eventually link to webpage.)*"
    insult_num = random.randint(0, len(insult_list) - 1)
    insult_template = insult_list[insult_num] % enemy
    insult_template += signature
    return insult_template


def get_connection():
    """ Gather credentials and connect to Reddit """

    # Get PRAW credentials stored as environment variables.
    USER_AGENT = os.getenv("HGB_USER_AGENT")
    CLIENT_ID = os.getenv("HGB_CLIENT_ID")
    CLIENT_SECRET = os.getenv("HGB_CLIENT_SECRET")
    USERNAME = os.getenv("HGB_USERNAME")
    PASSWORD = os.getenv("HGB_PASSWORD")

    # Connect via PRAW.
    connection = praw.Reddit(
        user_agent=USER_AGENT,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=USERNAME,
        password=PASSWORD
    )
    return connection


def record_reply():
    """ Record comment IDs that have been replied to to txt file. """

    with open(FILE_PATH, "w") as file:
        for comment_id in previous_replies:
            file.write(comment_id + ",")


def stream_comments():
    """ Comment streaming loop """
    # Live stream comments in subreddit.
    reddit = get_connection()
    for comment in reddit.subreddit("gsandbox").stream.comments():
        # Reset name_count and enemy_name.
        enemy_name = "null"
        name_count = 0
        # Check comment against list of comments previously replied to. We only want to reply once per comment.
        if comment.id not in previous_replies and comment.author != "HabsGrudgeBot":
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
            if enemy_name != "null" and name_count == 1:
                # Call our function for insulting our target.
                insult = build_insult(enemy_name)
                # Reply with tailored insult.
                # comment.reply(insult)
                # Console monitoring
                print(comment)
                print(insult)
                # Record comment ID as being replied to.
                previous_replies.append(comment.id)
                # Call method to write records to txt file.
                record_reply()


if __name__ == "__main__":
    main()
