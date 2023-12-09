#!/usr/bin/python3
'''
Database-IO-file of PolarWords
'''

import sqlite3, json
import os
from modules import dbInit
from datetime import datetime
import hashlib, uuid

class PwDb:
    ''' Database-Connection to the PolarWords-Database '''
    def __init__(self, dbfile):
        if not os.path.exists(dbfile):
            connection = sqlite3.connect(dbfile)
            cursor = connection.cursor()
            # activate support for foreign keys in SQLite:
            sql_command = 'PRAGMA foreign_keys = ON;'
            cursor.execute(sql_command)
            connection.commit()
            connection.close()
        self._connection = sqlite3.connect(dbfile) # _x = potected, __ would be private
        dbInit.checkTables(self)
    
    def reloadDb(self, dbfile):
        '''reloads the database file, i.e. after external changes/sync'''
        self._connection.commit() # not necessary, just to be sure
        self._connection.close()
        self._connection = sqlite3.connect(dbfile)
    
    def addUser(self, uname, passwd):
        '''adds a new non-admin user'''
        salt = uuid.uuid4().hex
        pwhash = hashlib.sha512(passwd.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        cursor = self._connection.cursor()
        sqlTemplate = '''INSERT INTO users (uname, pwhash, salt, instructor)
                VALUES (?, ?, ?, ?);'''
        cursor.execute(sqlTemplate, (uname, pwhash, salt, False))
        self._connection.commit()
    
    def getUsers(self):
        '''returns a list of all normal users'''
        cursor = self._connection.cursor()
        sqlTemplate = '''SELECT uname, instructor FROM users'''
        cursor.execute(sqlTemplate, )
        tup = cursor.fetchall()
        self._connection.commit()
        if tup is None:
            return None
        result = []
        for t in tup:
            result.append({
                    'uname'         : t[0],
                    'instructor'    : t[1]
                })
        return result
    
    def checkUser(self, uname):
        '''check if a user exists'''
        cursor = self._connection.cursor()
        sqlTemplate = '''SELECT * FROM users WHERE uname=?'''
        cursor.execute(sqlTemplate, (uname, )) # TODO: filter with tags and scores
        u = cursor.fetchone()
        self._connection.commit()
        if u != None:
            return True
        return False
    
    def checkPasswd(self, uname, passwd):
        '''checks a password for a uname'''
        cursor = self._connection.cursor()
        sqlTemplate = '''SELECT pwhash, salt FROM users WHERE uname=?'''
        cursor.execute(sqlTemplate, (uname, )) # TODO: filter with tags and scores
        u = cursor.fetchone()
        self._connection.commit()
        if u == None:
            return False
        hashed = hashlib.sha512(passwd.encode('utf-8') + u[1].encode('utf-8')).hexdigest()
        return u[0] == hashed
    
    def getWords(self, user='', tag='', days='9999', mentalScore=5, writtenScore=5):
        '''returns all words for a user that have matching tags and scores'''
        if days==None or days.isdigit() or not int(days)>0:
            days = '99999'
        cursor = self._connection.cursor()
        sqlTemplate = '''SELECT wid, word, desc, owner, tags, mentalScore, writtenScore, created, lastMentalKnown, lastWrittenKnown
                FROM words WHERE owner=?
                AND tags LIKE ?
                AND created > DATE('now', ?)'''
        cursor.execute(sqlTemplate, (user, '%'+tag+'%', '-'+days+' day')) # TODO: filter with tags and scores
        tup = cursor.fetchall()
        self._connection.commit()
        if tup is None:
            return None
        result = []
        for t in tup:
            result.append({
                    'wid'               : t[0],
                    'word'              : t[1],
                    'desc'              : t[2],
                    'owner'             : t[3],
                    'tags'              : t[4],
                    'mentalScore'       : t[5],
                    'writtenScore'      : t[6],
                    'created'           : t[7],
                    'lastMentalKnown'   : t[8],
                    'lastWrittenKnown'  : t[9]
                })
        return result
    
    def getRandomWord(self, user, mS=5, wS=5, tag=''):
        '''get a random word for a user that matches the constraints'''
        cursor = self._connection.cursor()
        sqlTemplate = '''SELECT wid, word, desc, hint, mentalScore, writtenScore FROM words 
                WHERE owner = ?
                AND (mentalScore <= ? OR writtenScore <= ?)
                AND tags LIKE ?
                ORDER BY RANDOM() LIMIT 1;'''
        cursor.execute(sqlTemplate, (user, mS, wS, '%'+tag+'%'))
        w = cursor.fetchone()
        if w != None:
            w = {'wid': w[0], 'word': w[1], 'desc': w[2], 'hint': w[3], 'mS': w[4], 'wS': w[5]}
        else:
            w = {}
        return w
    
    def addWord(self, user, word, desc, hint, tags='', extRecource=False):
        '''adds a word to the database'''
        cursor = self._connection.cursor()
        sqlTemplate = '''INSERT INTO words (word, desc, hint, tags, owner)
                VALUES (?, ?, ?, ?, ?);'''
        cursor.execute(sqlTemplate, (word, desc, hint, tags, user))
        self._connection.commit()
    
    def updateMental(self, user, wid, success):
        '''updates the mentalScore of a word'''
        cursor = self._connection.cursor()
        if success:
            sqlTemplate = '''UPDATE words SET mentalScore = mentalScore+1 
                    WHERE owner=? AND wid=?;'''
            cursor.execute(sqlTemplate, (user, wid))
            sqlTemplate = '''UPDATE words SET lastMentalKnown = CURRENT_TIMESTAMP 
                    WHERE owner=? AND wid=?;'''
            cursor.execute(sqlTemplate, (user, wid))
        else:
            sqlTemplate = '''UPDATE words SET mentalScore = 0 
                    WHERE owner=? AND wid=?;'''
            cursor.execute(sqlTemplate, (user, wid))
        self._connection.commit()
    
    def checkWritten(self, user, wid, word):
        '''checks a word with its description, updating writtenScore accordingly'''
        cursor = self._connection.cursor()
        sqlTemplate = '''SELECT word FROM words WHERE owner=? AND wid=?;'''
        cursor.execute(sqlTemplate, (user, wid))
        wo = cursor.fetchone()
        if wo[0] == word:
            sqlTemplate = '''UPDATE words SET writtenScore = writtenScore+1 
                    WHERE owner=? AND wid=?;'''
            cursor.execute(sqlTemplate, (user, wid))
            sqlTemplate = '''UPDATE words SET lastWrittenKnown = CURRENT_TIMESTAMP 
                    WHERE owner=? AND wid=?;'''
            cursor.execute(sqlTemplate, (user, wid))
            self._connection.commit()
            return True
        else:
            sqlTemplate = '''UPDATE words SET writtenScore = 0 
                    WHERE owner=? AND wid=?;'''
            cursor.execute(sqlTemplate, (user, wid))
            self._connection.commit()
            return wo[0]
    
    def deleteWord(self, user, wid):
        cursor = self._connection.cursor()
        sqlTemplate = '''DELETE FROM words WHERE owner=? AND wid=?;'''
        cursor.execute(sqlTemplate, (user, wid))
        self._connection.commit()
    
