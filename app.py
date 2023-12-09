#!/usr/bin/python3
#coding: utf-8
'''
Base file of PolarWords
'''

import os
import sqlite3
from flask import Flask, render_template, request, send_from_directory, make_response, jsonify
from flask import url_for, redirect
import flask_login
import json
from jinja2 import Template

from modules import dbio, settingsIo

# global settings:

dbfile = 'PolarWords.sqlite3'
settingsfile = 'PolarWords.conf'
settings = settingsIo.settingsIo(settingsfile)
host = settings.get('host')
debug = settings.get('debug')

# WebServer stuff:

app = Flask(__name__)

# login-stuff

app.secret_key = settings.get('secret_key')
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    #if username not in users:
    if username != settings.get('admin'):
        db = dbio.PwDb(dbfile)
        if not db.checkUser(username):
            return
    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    #if username not in users:
    if username != settings.get('admin'):
        db = dbio.PwDb(dbfile)
        if not db.checkUser(username):
            return
    user = User()
    user.id = username
    if username == settings.get('admin'):
        user.is_authenticated = settings.checkPw(request.form['password'])
    else:
        if not db.checkPasswd(request.form['username'], request.form['password']):
            return
    return user

# routes

@app.route('/', methods=['GET'])
def index():
    '''show index-page'''
    #if flask_login.current_user.is_anonymous:
    #    return render_template('login.html', relroot='./')
    if settings.get('admin') == '':
        return redirect('_init')
    elif flask_login.current_user.is_anonymous:
        return render_template('index.html', relroot='./')
    elif flask_login.current_user.id == settings.get('admin'):
        return redirect('_instructor')
    else:
        return redirect('_user/'+flask_login.current_user.id)

@app.route('/_init', methods=['GET', 'POST'])
def init():
    if settings.get('admin') == '':
        if request.method == 'GET':
            return render_template('addUser.html', relroot='./', path='_init')
        username = request.form['username']
        password = request.form['password']
        if username != '' and password != '':
            settings.set('admin', username)
            settings.set('password', password)
            return redirect('_login')
        return 'ERROR: Username and/or password was not set!'
    else:
        return 'TeXercise is already initialized!'

@app.route('/_login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return redirect('./')
    username = request.form['username']
    password = request.form['password']
    if username == settings.get('admin'):
        if settings.checkPw(password):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect('_instructor')
    db = dbio.PwDb(dbfile)
    if db.checkUser(username):
        if db.checkPasswd(username, password):
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect('_user/'+username)
    return 'Bad login'

@app.route('/_logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('./')

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

@app.route('/_static/<filename>', methods=['GET'])
def sendStatic(filename):
    '''send static files like css or js'''
    return send_from_directory('static', filename)


@app.route('/_instructor', methods=['GET'])
@flask_login.login_required
def instructor():
    '''show instructor-page'''
    user = flask_login.current_user.id
    if flask_login.current_user.id != settings.get('admin'):
        return '405 not allowed'
    db = dbio.PwDb(dbfile)
    users = db.getUsers()
    return render_template('instructor.html', relroot='./', user=user, users=users, authuser=flask_login.current_user.id)

@app.route('/_user/<user>', methods=['GET'])
@flask_login.login_required
def user(user):
    '''show user-page'''
    if flask_login.current_user.id != settings.get('admin') and flask_login.current_user.id != user:
        return '405 not allowed'
    db = dbio.PwDb(dbfile)
    words = db.getWords(user)
    return render_template('user.html', relroot='../', user=user, words=words, authuser=flask_login.current_user.id)

@app.route('/_addWord', methods=['GET', 'POST'])
@flask_login.login_required
def addWord():
    '''insert (POST) or update (PUT) a new word'''
    if request.method == 'GET':
        return render_template('addWord.html', relroot='./', authuser=flask_login.current_user.id)
    elif request.method == 'POST':
        w = request.json
        db = dbio.PwDb(dbfile)
        db.addWord(flask_login.current_user.id, w['word'], w['desc'], w['hint'], w['tags'])
        return 'ok'

@app.route('/_getWords/<user>', methods=['POST'])
@flask_login.login_required
def getWords(user):
    '''get words list of a user'''
    if flask_login.current_user.id != settings.get('admin') and flask_login.current_user.id != user:
        return '405 not allowed'
    filt = request.json
    db = dbio.PwDb(dbfile)
    words = db.getWords(user, tag=filt['tag'], days=filt['days'])
    if words == None:
        words = {}
    return words

@app.route('/_learnWord', methods=['GET', 'PUT'])
@flask_login.login_required
def learnWord():
    '''get or check a word to learn'''
    user = flask_login.current_user.id
    if request.method == 'GET':
        return render_template('learnWord.html', relroot='./', authuser=user)
    elif request.method == 'PUT':
        db = dbio.PwDb(dbfile)
        job = request.json
        if job['job'] == 'getNew':
            return db.getRandomWord(user, mS=4, wS=4, tag=job['tag'])
        if job['job'] == 'mentalSuccess':
            db.updateMental(user, job['word']['wid'], True)
        elif job['job'] == 'mentalFail':
            db.updateMental(user, job['word']['wid'], False)
        elif job['job'] == 'checkWritten':
            result = db.checkWritten(user, job['word']['wid'], job['word']['word'])
            if result != True:
                return result
        else:
            return 'ERROR: unknown job: '+job['job']
        return db.getRandomWord(user, mS=4, wS=4, tag=job['tag'])

@app.route('/_addUser', methods=['GET', 'POST'])
@flask_login.login_required # TODO: only admin-user!
def addUser():
    if request.method == 'GET':
        return render_template('addUser.html', relroot='./', path='_addUser')
    username = request.form['username']
    password = request.form['password']
    if username != '' and password != '':
        db = dbio.PwDb(dbfile)
        db.addUser(username, password)
        return redirect('./')
    return 'ERROR: Username and/or password was not set!'

@app.route('/_delete/<wid>', methods=['DELETE'])
@flask_login.login_required
def delete(wid):
    '''delete a word'''
    user = flask_login.current_user.id
    db = dbio.PwDb(dbfile)
    db.deleteWord(user, wid)
    return 'ok'

# run it:

if __name__ == '__main__':
    app.run(host=host, debug=debug)
