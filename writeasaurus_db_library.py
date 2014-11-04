#!/usr/bin/python

"""
Writeasaurus DB Helper File

Test suite at end.

"""

import time
import sqlite3
import os

#
# a global print, inserts some newline padding
#
def pp(text):
    print "\n%s" % text

class LoggingColors:
    OK      = '\033[0;32m'
    FAIL    = '\033[1;31m'
    END     = '\033[0;m'

# an internal schema to use:
class PromptSchema:

    # data-bases:
    TEST_DB_NAME = "writeasaurus.test.db"
    DEV_DB_NAME = "writeasaurus.dev.db"
    PROD_DB_NAME = "writeasaurus.db"

    # table:
    TABLE_NAME = "prompts"

    # columns:
    COLUMN_ID = "id"
    COLUMN_DESCRIPTION = "description"
    COLUMN_EXTRA_TEXT = "extra_text"
    COLUMN_SOURCE_ID = "source_id"
    COLUMN_TIMESTAMP = "timestamp"

    # release columns:
    COLUMN_SKIPPED = "skipped"
    COLUMN_COMPLETED = "completed"

    # queries:
    QUERY_CREATE_TABLE = "CREATE TABLE IF NOT EXISTS %s (%s INTEGER PRIMARY KEY AUTOINCREMENT, %s TEXT, %s TEXT, %s TEXT UNIQUE, %s INTEGER DEFAULT 0)" % (TABLE_NAME, COLUMN_ID, COLUMN_DESCRIPTION, COLUMN_EXTRA_TEXT, COLUMN_SOURCE_ID, COLUMN_TIMESTAMP)
    
    QUERY_DROP_TABLE = "DROP TABLE IF EXISTS %s" % TABLE_NAME

    QUERY_INSERT_SINGLE = "INSERT INTO %s VALUES(?, ?, ?, ?, ?)" % TABLE_NAME
    QUERY_INSERT_MANY = "INSERT INTO %s VALUES(?, ?, ?, ?, ?)" % TABLE_NAME

    QUERY_UPDATE = "UPDATE %s SET %s = ? WHERE %s = ?" % (TABLE_NAME, COLUMN_DESCRIPTION, COLUMN_ID)
    QUERY_SELECT = "SELECT * FROM %s" % TABLE_NAME
    QUERY_SELECT_ALL_SLUGS = "SELECT %s FROM %s" % (COLUMN_SOURCE_ID, TABLE_NAME)

    QUERY_RELEASE_CREATE_TABLE = "CREATE TABLE IF NOT EXISTS %s (%s INTEGER PRIMARY KEY AUTOINCREMENT, %s TEXT, %s INTEGER DEFAULT 0, %s INTEGER DEFAULT 0)" % (TABLE_NAME, COLUMN_ID, COLUMN_DESCRIPTION, COLUMN_SKIPPED, COLUMN_COMPLETED)
    QUERY_RELEASE_INSERT_MANY = "INSERT INTO %s VALUES(?, ?, ?, ?)" % TABLE_NAME
    QUERY_RELEASE_SELECT_COLUMNS = "SELECT %s FROM %s" % (COLUMN_DESCRIPTION, TABLE_NAME)

class LogSchema:
    pass
class StorySchema:
    pass

# handles all interaction with the DB:
# opening, closing, creating, deleting, querying, etc.
class PromptsDatabaseHelper(object):

    @classmethod
    def get_test_database(cls):
        return cls(PromptSchema.TEST_DB_NAME)

    @classmethod
    def get_dev_database(cls):
        return cls(PromptSchema.DEV_DB_NAME)

    @classmethod
    def get_release_database(cls):
        return cls(PromptSchema.PROD_DB_NAME)

    # constructor:

    def __init__(self, database):
        # init:
        self.connection = None
        self.cursor = None
        self.database = database
        self.connect()

    # instance methods:

    def execute(self, query):
        self.cursor.execute(query)
    def execute_single(self, query, value):
        self.cursor.execute(query, value)
    def execute_many(self, query, values):
        self.cursor.executemany(query, values)

    def connect(self):
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def close(self):
        if self.connection:
            self.connection.close()

    def insert(self, value):
        self.execute_single(PromptSchema.QUERY_INSERT_SINGLE, value)
        self.connection.commit()

    def insert_many(self, values):
        if self.database == PromptSchema.PROD_DB_NAME:
            self.execute_many(PromptSchema.QUERY_RELEASE_INSERT_MANY, values)
        else:
            self.execute_many(PromptSchema.QUERY_INSERT_MANY, values)
        self.connection.commit()

    def select_one(self):
        self.execute(PromptSchema.QUERY_SELECT)
        return self.cursor.fetchone()

    def select_all(self):
        self.execute(PromptSchema.QUERY_SELECT)
        return self.cursor.fetchall()

    def select_release_columns(self):
        self.execute(PromptSchema.QUERY_RELEASE_SELECT_COLUMNS)
        return self.cursor.fetchall()

    def select_all_slugs(self):
        self.execute(PromptSchema.QUERY_SELECT_ALL_SLUGS)
        return self.cursor.fetchall()

    def create_table(self):
        if self.database == PromptSchema.PROD_DB_NAME:
            self.execute(PromptSchema.QUERY_RELEASE_CREATE_TABLE)
        else:
            self.execute(PromptSchema.QUERY_CREATE_TABLE)
        self.connection.commit()

    def drop_table(self):
        self.execute(PromptSchema.QUERY_DROP_TABLE)
        self.connection.commit()

    def update(self):
        self.execute_single(PromptSchema.QUERY_INSERT_SINGLE, value)
        self.connection.commit()

    def cleanup(self):
        self.close()
        if self.database == PromptSchema.TEST_DB_NAME:
            os.remove(PromptSchema.TEST_DB_NAME)

# entry-point when run as script:
if __name__ == "__main__":
    #
    # START TEST
    #
    
    pp("starting test...")

    pp("creating database helper")
    helper = PromptsDatabaseHelper.get_test_database()

    # main script entry point:
    # try:
    pp("opening connection to database")
    helper.connect()

    pp("clearing database")
    helper.drop_table()

    pp("creating database")
    helper.create_table()

    pp("create mock data")
    # a couple prompts with current unix time as int type to be stored:
    prompts = (
        (1, "A test description", "Source ID (Reddit ID)", "extra-text", int(time.time())),
        (2, "Another description", "Source ID (Different Source ID)", "extra-text-2", int(time.time()))
    )
    helper.insert_many(prompts)

    pp("select recently inserted data:")
    rows = helper.select_all()
    pp(rows)

    pp("select the most recent ID:")
    row = helper.select_one()
    pp(row[2])

    pp("resetting database")
    helper.drop_table()

    # close
    pp("finishing test...")
    helper.close()
    helper.cleanup()

    #
    # END TEST
    #
