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

# our little lib with our schema and it's helper
from writeasaurus_library import *


# main release
# filters rows one by one
def release(filter = True):
    pp("creating dev database helper")
    dev_helper = PromptsDatabaseHelper.get_dev_database()
    
    # the set of columns from the dev table to transfer
    rows = dev_helper.select_release_columns()
    if rows == None:
        rows = []

    # close:
    dev_helper.close()

    # output number of entries:
    num_current = len(rows)
    pp("You currently have %s entries in the dev DB" % num_current)

    if (num_current == 0):
        pp("There is no data to prepare...exiting")
        return

    approved_rows = []
    rejected_rows = []
    if filter == False:
        # don't filter the rows in any way:
        approved_rows = rows
    else:
        pp("preparing to filter rows...")

        pp("Is the description text OK? enter new text if not, otherwise enter 'y' for yes or 'n' to reject the row")
        # approve each row individually, edit them as needed:
        for dev_row in rows:
            description = dev_row[0]
            pp(description)

            user_input = raw_input()

            # accept row:
            if user_input.lower() == 'y':
                pp(LoggingColors.OK + "Accepted row as is" + LoggingColors.END)
                approved_rows.append(dev_row)
            # reject row:
            elif user_input.lower() == 'n':
                pp(LoggingColors.FAIL + "Rejected row" + LoggingColors.END)
                rejected_rows.append(dev_row)
            # edit row:
            else:
                while True:
                    description = user_input
                    pp(LoggingColors.OK + "Accepted edited row:\n" + LoggingColors.FAIL + "\"" + user_input + "\"" + LoggingColors.END)
                    pp("Is the edited text OK? enter new text if not, otherwise enter 'y' for yes or 'n' to reject the row")

                    user_input = raw_input()
                    if user_input.lower() == 'y':
                        # accepted new description
                        dev_row[0] = description
                        approved_rows.append(dev_row)
                        break # out of while loop
                    elif user_input.lower() == 'n':
                        rejected_rows.append(dev_row)
                        break # out of while loop
                    else:
                        # entered new text, check whether it's okay
                        pass # the while loop continues, and the user_input var is edited to the new text

    # build release rows, format below:
    def build_release_row(dev_row):
        # id, description, skipped, completed
        release_row = (None, dev_row[0], 0, 0)
        return release_row

    # prepare the data:
    final_rows = map(build_release_row, approved_rows)

    # create the release DB and transfer the rows over
    pp("creating release database helper")
    release_helper = PromptsDatabaseHelper.get_release_database()

    # reset tables:
    release_helper.drop_story_table()
    release_helper.create_story_table()

    release_helper.drop_table()
    release_helper.create_table()

    # insert the rows:
    release_helper.insert_many(final_rows)

    # now retrieve all:
    final_rows = release_helper.select_all()
    release_helper.close()

    num_current = len(final_rows)
    pp("You now have %s entries in the release DB" % num_current)


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
