#! /usr/bin/env python2.7

'''
dba.py: Database administration; CRUD operations on events and users.
'''

import json
import time
#import sqlite3
import psycopg2
import argparse
from datetime import date

__author__ = "Srinidhi Kaushik"
__copyright__ = "Copyright (C) 2017 Srinidhi Kaushik"
__license__ = "MIT"
__version__ = "0.3"
__maintainer__ = "Srinidhi Kaushik"
__email__ = "clickyotomy@users.noreply.github.com"
__status__ = "Production"


def load_config(config_path):
     '''
     Load configuration variables from `config.json'.
     '''
     try:
         with open(config_path, 'r') as config:
             return json.loads(config.read())
     except (IOError, KeyError, ValueError) as err:
         print (': '.join([type(err).__name__, str(err)]) + '.')
         exit(1)

# Application configuration variables.
APP_CONFIG = {}

def get_db():
    return psycopg2.connect(
                host=APP_CONFIG["db_host"],
                database=APP_CONFIG["db_name"],
                user=APP_CONFIG["db_username"],
                password=APP_CONFIG["db_password"],
                port=APP_CONFIG["db_port"])

def init(dbpath):
    '''
    Create a new database with `users' and `events' tables.
    '''
    dbconn = get_db()
    cursor = dbconn.cursor()

    #cursor.execute('ATTACH DATABASE ? AS "game"', (dbpath,))

    # Create a users table to store user information.
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users
            (
                id          TEXT NOT NULL UNIQUE,
                password    TEXT NOT NULL,
                event       TEXT NOT NULL,
                level       INTEGER NOT NULL DEFAULT -1,
                email       TEXT NOT NULL,
                phone       TEXT NOT NULL,
                ban         BOOL DEFAULT false,
                timestamp   DATE
            )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS events
            (
                id        TEXT NOT NULL UNIQUE,
                data      TEXT NOT NULL,
                current   BOOL DEFAULT false,
                timestamp DATE
            )
        '''
    )

    cursor.execute(
        '''
        CREATE INDEX IF NOT EXISTS index_user ON users(id)
        '''
    )

    cursor.execute(
        '''
        CREATE INDEX IF NOT EXISTS index_event ON users(id)
        '''
    )

    print ('Initialized an empty database `{0}\' with `users\', and `events\''.format(APP_CONFIG["db_name"]))

    dbconn.commit()
    dbconn.close()


def load(dbpath, event, current=False):
    '''
    Load an event into the database.
    '''
    dbconn = get_db()
    cursor = dbconn.cursor()

    today = date.today()
    try:
        if current:
            cursor.execute(
                    'UPDATE events set current = %(current)s', {'current': not current}
            )

        cursor.execute(
                'INSERT into events VALUES (%(id)s, %(event)s, %(current)s, %(timestamp)s)',
                {'id': event['id'], 'event': json.dumps(event), 'current': current, 'timestamp': today}
        )

    except (Exception, psycopg2.DatabaseError) as error:
    #except sqlite3.IntegrityError:
        print ('The event `{}\' already exists, updating it.'.format(
            event['id']
        ))
        cursor.execute(
            '''
            UPDATE events
            SET id = %(event_id)s, current = %(current)s, timestamp = %(timestamp)s, data = %(data)s
            WHERE id = %(id)s
            ''',{'event_id': event['id'], 'current': current, 'timestamp': today, 'data': json.dumps(event), 'id': event['id']}
            #(
            #    event['id'], current, int(time.time()),
            #    json.dumps(event), event['id']
            #)
        )

    dbconn.commit()
    dbconn.close()
    print ('Database updated.')


def main():
    '''
    The main method, accept and parse arguments.
    '''
    global APP_CONFIG
    description = 'Interface for game database administration.'
    init_help = 'init: initialize an empty database; '
    load_help = 'load: insert (or update) an event to (on) the database'
    event_help = 'file to load event data from'
    dbpath_help = 'path to load/save the database from/to'
    current_help = 'mark event as active (and the rest inactive)'

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-a', '--action', choices=('init', 'load'),
                        help=''.join([init_help, load_help]),
                        required=True)
    parser.add_argument('-db', '--database-path', help=dbpath_help,
                        required=True, default='game.db')
    parser.add_argument('-config', '--config-path', help=dbpath_help,
                        required=True, default='./config.json')
    parser.add_argument('-c', '--current', action='store_true', default=False,
                        help=current_help)
    parser.add_argument('-f', '--from-file', help=event_help)

    args = vars(parser.parse_args())
    APP_CONFIG = load_config(args['config_path'])

    if args['action'] == 'load' and args['from_file'] is None:
        print ('{}: error: argument -f/--from-file is required'.format(__file__))
        exit(1)

    if args['action'] == 'load':
        event = json.loads(open(args['from_file'], 'r').read())
        print(event)
        load(args['database_path'], event, args['current'])
    else:
        init(args['database_path'])


if __name__ == '__main__':
    main()
