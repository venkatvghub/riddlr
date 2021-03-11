#! /usr/bin/env python2.7

'''
Helper modules for the web-app.
'''

import time
import json
import urllib.parse
from urllib.parse import urljoin
from datetime import date
#from urlparse import urlparse, urljoin

import argon2

__author__ = "Srinidhi Kaushik"
__copyright__ = "Copyright (C) 2017 Srinidhi Kaushik"
__license__ = "MIT"
__version__ = "0.3"
__maintainer__ = "Srinidhi Kaushik"
__email__ = "clickyotomy@users.noreply.github.com"
__status__ = "Production"


# Application configuration path.
APP_CONFIG_PATH = './config.json'


def load_config():
    '''
    Load configuration variables from `config.json'.
    '''
    try:
        with open(APP_CONFIG_PATH, 'r') as config:
            return json.loads(config.read())
    except (IOError, KeyError, ValueError) as err:
        print (': '.join([type(err).__name__, str(err)]) + '.')
        exit(1)


# The current event.
EVENT = load_config()['event']


def is_safe_url(request, target):
    '''
    Check for safe redirects.
    '''
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def user_exists(cursor, uname):
    '''
    Check if a user exists in the database.
    '''
    cursor.execute('SELECT * FROM users WHERE event = %(event)s AND id = %(username)s AND ban = %(ban)s', {'event': EVENT, 'username': uname, 'ban': False})
    data = cursor.fetchall()
    return bool(data) or False
    #return bool(cursor.execute(
    #    'SELECT * FROM users WHERE event = %(event)s AND id = %(username)s AND ban = false', {'event': EVENT, 'username': uname}).fetchall()) or False


def fetch_event_data(cursor, event):
    '''
    Get the event data.
    If it doesn't exist, exit.
    '''
    try:

        cursor.execute(
                'SELECT data FROM events WHERE id = %(event)s', {'event': event})
        data = cursor.fetchone()
        return json.loads(data[0])
    except (KeyError, ValueError):
        print ('Ubale to fetch event data.')
        exit(1)


def event_start(data):
    '''
    Check if the event has started.
    '''
    if data['start'] is not None:
        return int(data['start']) < int(time.time())
    else:
        return True


def validate_user(cursor, username, password):
    '''
    Password check before login.
    '''
    hasher = argon2.PasswordHasher()
    try:
        if user_exists(cursor, username):
            cursor.execute(
                '''
                SELECT password FROM users
                WHERE event = %(event)s AND id = %(username)s AND ban = %(ban)s
                ''', {'event': EVENT, 'username': username, 'ban': False})
            credentials = cursor.fetchone()
            return hasher.verify(credentials[0], password)

    except argon2.exceptions.VerifyMismatchError:
        return False


def get_user_level(cursor, username):
    '''
    Check the current level of the user.
    '''
    if user_exists(cursor, username):
        cursor.execute(
                'SELECT level FROM users WHERE event = %(event)s AND id = %(username)s', {'event': EVENT, 'username': username}
        )
        data = cursor.fetchone()
        return data[0]
    return 0


def validate_answer(data, answer):
    '''
    Validate the answer for next level, hints.
    '''
    correct, hint, text = False, False, ''
    try:
        choices, hints = [], []
        answer = answer.strip()

        if not data['answer']['case']:
            answer = answer.lower()
            choices = [_.lower() for _ in data['answer']['choices']]
            hints = [_['hint'].lower() for _ in data['answer']['hints']]

        else:
            choices = [_ for _ in data['answer']['choices']]
            hints = [_['hint'] for _ in data['answer']['hints']]

        if answer in choices:
            correct, hint, text = True, False, ''
        elif answer in hints:
            correct, hint = False, True
            for texts in data['answer']['hints']:
                if texts['hint'].lower() == answer.lower():
                    text = texts['text']
    except (KeyError, ValueError, AttributeError):
        pass

    return correct, hint, text


def routing(event, token, flag):
    '''
    A 2-way mapping to get level numbers or URL routes.
    '''
    try:
        for level in event['levels']:
            if flag == 'index':
                if token == 'congratulations':
                    return len(event['levels']) + 1
                if level['path'] == token:
                    return level['index']
            elif flag == 'path':
                if int(token) > len(event['levels']):
                    return '/congratulations'
                if level['index'] == token:
                    return '/levels/' + level['path']
    except (KeyError, IndexError, ValueError):
        pass

    if flag == 'path':
        return '/404'
    else:
        return -1


def get_level_data(event, path):
    '''
    Load level data from a URL route.
    '''
    try:
        for level in event['levels']:
            if level['path'] == path:
                return level
    except (KeyError, ValueError, IndexError):
        pass

    return None


def increment(dbconn, username, level):
    '''
    Increment the user level.
    '''
    cursor = dbconn.cursor()
    if user_exists(cursor, username):
        today = date.today()
        cursor.execute(
            '''
            UPDATE users
            SET level = %(level)s, timestamp = %(timestamp)s
            WHERE id = %(username)s
            ''', {'level': level, 'timestamp': today, 'username': username}
        )

    dbconn.commit()


def trackr(cursor, limit):
    '''
    Tracker method for the leaderboard.
    '''
    cursor.execute(
        '''
        SELECT id, level FROM users
        WHERE event = %(event)s AND ban = %(ban)s
        ORDER BY level DESC, timestamp ASC
        LIMIT %(limit)s
        ''', {'event': EVENT, 'limit': limit, 'ban': False}
    )
    return cursor.fetchall()


def admin(cursor, table):
    '''
    Fetch all the data from `users' database.
    '''
    if table == 'users':
        cursor.execute(
            '''
            SELECT id, level, email, phone, timestamp, ban
            FROM users
            WHERE event = %(event)s
            ORDER BY level DESC, timestamp ASC
            ''', {'event': EVENT}
        )
        return cursor.fetchall()
        #return data
    else:
        cursor.execute('SELECT * FROM events')
        return cursor.fetchall()
        #return data

    return []


def is_banned(cursor, username):
    '''
    Check if a player is banned.
    '''

    cursor.execute(
        'SELECT id FROM users where event = %(event)s AND id = %(username)s AND ban = %(ban)s', {'event': EVENT, 'username': username, 'ban': True}
    )
    return bool(cursor.fetchone())
    #return bool(data)
