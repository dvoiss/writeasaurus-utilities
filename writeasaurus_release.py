#!/usr/bin/python

"""
Writeasaurus Population Script

Fetch the writing prompts subreddit,
add them to a local database.

This script wasn't written to be used more than a few times,
it's a one off to get some data into a sqlite database.

"""

import sqlite3
import sys, os, getopt

# makes it easier to edit text, arrows keys are characters and raw_input accepts lines only
# readline allows the user to use the arrow keys and not have it go: "abc...^[[C^[[D^[[C^[[D^[[D"
import readline

# our little lib with our schema and it's helper
from writeasaurus_library import *

# global in the script:
release_helper = PromptsDatabaseHelper.get_release_database()

# main release
# filters rows one by one
def release(filter = True):
    pp("re-creating release tables")

    # reset tables:
    release_helper.drop_story_table()
    release_helper.create_story_table()
    release_helper.drop_table()
    release_helper.create_table()

    pp("getting dev database helper")
    dev_helper = PromptsDatabaseHelper.get_dev_database()

    # the set of columns from the dev table to transfer
    rows = dev_helper.select_release_columns()
    if rows == None:
        rows = []

    # output number of entries:
    num_current = len(rows)

    if (num_current == 0):
        pp("There are no rows. no data to prepare. exiting")
        return

    pp("You currently have %s entries in the dev DB" % num_current)

    pp("preparing to filter rows...")

    # don't put this in the for loop, we don't need directions each time:
    pp("Is the description text OK? enter new text if not, otherwise enter 'y' for yes or 'n' to reject the row")

    # track these:
    rejected_ids = []
    accepted_ids = []

    # approve each row individually, edit them as needed:
    for dev_row in rows:
        reddit_id = dev_row[1]
        try:
            if (rejected_ids.index(reddit_id) or accepted_ids.index(reddit_id)):
                continue
        except ValueError:
            pass

        description = dev_row[0]
        pp(description)

        user_input = raw_input()

        # accept row:
        if user_input.lower() == 'y':
            accepted_ids.append(reddit_id)
            insert(description)
        # reject row:
        elif user_input.lower() == 'n':
            delete(reddit_id)
            rejected_ids.append(reddit_id)
        # edit row:
        else:
            while True:
                description = user_input
                pp(LoggingColors.OK + "Accepted edited row:\n" + LoggingColors.FAIL + "\"" + user_input + "\"" + LoggingColors.END)
                pp("Is the edited text OK? enter new text if not, otherwise enter 'y' for yes or 'n' to reject the row")

                user_input = raw_input()
                if user_input.lower() == 'y':
                    # accepted new description,
                    # tuple is immutable:
                    accepted_ids.append(reddit_id)
                    insert(description)
                    break # out of while loop
                elif user_input.lower() == 'n':
                    rejected_ids.append(reddit_id)
                    delete(reddit_id)
                    break # out of while loop
                else:
                    # entered new text, check whether it's okay
                    pass # the while loop continues, and the user_input var is edited to the new text

    num_rejected = len(rejected_ids)
    pp("You rejected %s entries from the release DB" % num_rejected)
    print(rejected_ids)

    num_accepted = len(accepted_ids)
    pp("You accepted %s entries in the release DB" % num_accepted)
    print(num_accepted)

    # validation: retrieve all
    final_rows = release_helper.select_all()
    release_helper.close()
    num_current = len(final_rows)
    pp("You now have %s entries in the release DB" % num_current)

# delete row:
def delete(id):
    pp(LoggingColors.FAIL + "Rejected row" + LoggingColors.END)
    release_helper.delete(id)

# insert row:
def insert(description):
    # build release rows, format below:
    def build_release_row(description):
        # id, description, skipped, completed
        release_row = (None, description, 0, 0)
        return release_row

    pp(LoggingColors.OK + "Accepted row as is" + LoggingColors.END)
    release_helper.insert(build_release_row(description))

# main entry-point:
# parse username and password options,
# the test option -t runs some small tests which prints output
def main(argv):
    file_name = argv[0]
    help_text = LoggingColors.FAIL + file_name + " -f" + LoggingColors.END

    try:
        passed_args = argv[1:]
        opts, args = getopt.getopt(passed_args, "hf")
    except getopt.GetoptError:
        print help_text
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print help_text
            sys.exit()
        elif opt in ("-f", "--filter"):
            release(True)
            sys.exit()

    pp("starting main...")
    release(False)

# entry-point:
if __name__ == "__main__":
    main(sys.argv)
