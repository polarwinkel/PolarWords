#!/usr/bin/python3
'''
Database-IO-file of TeXercise
'''

import sqlite3
import os

def checkTables(db):
    ''' makes sure default tables exist in the Database '''
    # sheets:
    cursor = db._connection.cursor()
    sql_command = '''
        CREATE TABLE IF NOT EXISTS users (
            uname VARCHAR(12) NOT NULL PRIMARY KEY,
            pwhash VARCHAR(256),
            salt VARCHAR(256),
            fullName VARCHAR(256),
            instructor BOOLEAN
        );'''
    try:
        cursor.execute(sql_command)
    except sqlite3.OperationalError as err:
        args = list(err.args)
        args.append('Failed to create users table')
        err.args = tuple(args)
        raise
    # edits:
    cursor = db._connection.cursor()
    sql_command = '''
        CREATE TABLE IF NOT EXISTS words (
            wid INTEGER NOT NULL PRIMARY KEY,
            word TEXT NOT NULL,
            desc TEXT NOT NULL,
            hint TEXT NOT NULL,
            extResource BOOLEAN false,
            owner INTEGER NOT NULL,
            tags TEXT,
            mentalScore INTEGER DEFAULT 0,
            writtenScore INTEGER DEFAULT 0,
            created TEXT DEFAULT (DATE('now','localtime')),
            lastMentalKnown TEXT,
            lastWrittenKnown TEXT,
            FOREIGN KEY(owner) REFERENCES users(uname)
        );'''
    try:
        cursor.execute(sql_command)
    except sqlite3.OperationalError as err:
        args = list(err.args)
        args.append('Failed to create words table')
        err.args = tuple(args)
        raise
    db._connection.commit()
