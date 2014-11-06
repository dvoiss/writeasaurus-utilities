#!/usr/bin/python

"""
Writeasaurus Population Script

Fetch the writing prompts subreddit,
add them to a local database.

This script wasn't written to be used more than a few times,
it's a one off to get some data into a sqlite database.

"""

import sqlite3
import sys

# our little lib with our schema and it's helper
from writeasaurus_library import *


# main entry-point:
# parse username and password options,
# the test option -t runs some small tests which prints output
def main(argv):
    pp("creating dev database helper")
    dev_helper = PromptsDatabaseHelper.get_dev_database()
    
    # the set of columns from the dev table to transfer
    rows = dev_helper.select_release_columns()
    if rows == None:
        rows = []
    else:
        def build_row(dev_row):
            release_row = (None, dev_row[0], 0, 0)
            return release_row

        # prepare the data:
        rows = map(build_row, rows)

    num_current = len(rows)
    pp("You currently have %s entries in the dev DB" % num_current)

    dev_helper.close()

    if (num_current == 0):
        pp("There is no data to prepare...exiting")
        return

    # create the release DB and transfer the rows over
    pp("creating release database helper")
    release_helper = PromptsDatabaseHelper.get_release_database()
    release_helper.drop_table()
    release_helper.create_table()
    release_helper.insert_many(rows)
    rows = release_helper.select_all()
    release_helper.close()

    num_current = len(rows)
    pp("You now have %s entries in the release DB" % num_current)


# entry-point:
if __name__ == "__main__":
    pp("starting main...")
    main(sys.argv)

