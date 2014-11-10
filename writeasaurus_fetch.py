#!/usr/bin/python

"""
Writeasaurus Population Script

Fetch the writing prompts subreddit,
add them to a local database.

This script wasn't written to be used more than a few times,
it's a one off to get some data into a sqlite database.

"""

import praw

import re
import time
import json

import sqlite3
import sys, os, getopt

# our little lib with our schema and it's helper
from writeasaurus_library import *

#
# fetch the writingprompts subreddit.
#
def fetch_reddit(username, password):
    # login using python reddit api wrapper - praw
    pp("login to reddit")
    r = praw.Reddit('/u/daveasaurus\'s Writing Prompts script for "Writeasaurus" app. http://github.com/dvoiss')
    if username and password:
        r.login(username, password)
    else:
        r.login()
    subreddit = r.get_subreddit('writingprompts')

    # for testing:
    limit = 10000
    processed_count = 0

    pp("creating database helper")
    helper = PromptsDatabaseHelper.get_dev_database()

    helper.create_table() # create if needed
    
    # the set of processed submission ids
    processed_ids = helper.select_all_slugs()
    if processed_ids == None:
        processed_ids = []

    # drop the table:
    num_current = len(processed_ids)
    if num_current != 0:
        pp("do you really want to delete the entries in the DB? You currently have %s entries" % num_current)
        choice = raw_input().lower()
        if choice == 'y' or choice == 'yes':
            pp("dropping...")
            helper.drop_table()
            helper.create_table()

    # get stories newer than the last story we have in the DB:
    latest_story = None
    # row = helper.select_one()
    # if row:
    #     latest_story = row[2]

    # regex pattern:
    # many prompts follow a pattern: "[WP] Write about a character on a quest for a famous relic!"
    # where the [wp] or [cw] need to be cut off:
    regex_pattern = re.compile("\[\w+\]\s+")

    pp("retrieving entries")
    for submission in subreddit.get_hot(limit=limit, place_holder=latest_story):
        # grab the comment count, don't bother with any writing prompts that have never had responses
        comment_count = submission.num_comments

        # process this submission, prevent dupes, don't re-process submissions:
        if submission.id not in processed_ids: # and comment_count != 0:
            processed_count += 1

            # what are we prompted to do:
            title = submission.title
            # clean title:
            match = regex_pattern.match(title)
            start_index = 0
            if match:
                start_index = match.end()
            #    "[WP] Write about a character on a quest for a famous relic!"
            # =>      "Write about a character on a quest for a famous relic!"
            title = title[start_index:]
            
            # not being used now, but should extra data be saved in the future?
            # extra text
            text = submission.selftext
            # the type of writing prompt: Writing Prompt, Established Universe, Image Prompt, etc.
            type = submission.link_flair_text

            # prompt needs to be a tuple with as many elements as columns,
            # the first element is the ID (auto-increments),
            # the last is the scraped-time
            prompt = (None, title, text, submission.id, int(time.time()))

            # save this submission into the DB
            try:
                helper.insert(prompt)
                processed_ids.append(submission.id)
            except sqlite3.IntegrityError:
                pass

    # exit
    if helper:
        helper.close()

    pp(LoggingColors.OK + ("finished, processed %s entries" % processed_count) + LoggingColors.END)


# main entry-point:
# parse username and password options,
# the test option -t runs some small tests which prints output
def main(argv):
    file_name = argv[0]
    help_text = LoggingColors.FAIL + file_name + " -u <username> -p <password>" + LoggingColors.END
    
    try:
        passed_args = argv[1:]
        opts, args = getopt.getopt(passed_args, "hu:p:", ["username=","password="])
    except getopt.GetoptError:
        print help_text
        sys.exit(2)

    username, password = None, None

    for opt, arg in opts:
        if opt == '-h':
            print help_text
            sys.exit()
        elif opt in ("-u", "--username"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg

    # and off we go:
    pp("starting main...")
    fetch_reddit(username, password)


# entry-point:
if __name__ == "__main__":
    main(sys.argv)

