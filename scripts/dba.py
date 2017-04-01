#! /usr/bin/env python2.7

'''
dba.py: Database administration; CRUD operations on events and users.
'''

__author__ = "Srinidhi Kaushik"
__copyright__ = "Copyright (C) 2017 Srinidhi Kaushik"
__license__ = "MIT"
__version__ = "0.2"
__maintainer__ = "Srinidhi Kaushik"
__email__ = "clickyotomy@"
__status__ = "Production"


import json
import time
import sqlite3
import argparse


def init(dbpath):
    '''
    Create a new database with `users` and `events` tables.
    '''
    dbconn = sqlite3.connect(dbpath)
    cursor = dbconn.cursor()

    cursor.execute('ATTACH DATABASE ? AS "game"', (dbpath,))

    # Create a users table to store user information.
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS game.users
            (
                id          TEXT NOT NULL UNIQUE,
                password    TEXT NOT NULL,
                event       TEXT NOT NULL,
                level       INTEGER NOT NULL DEFAULT -1,
                email       TEXT NOT NULL,
                phone       TEXT NOT NULL,
                ban         BOOL DEFAULT 0,
                timestamp   DATE
            )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS game.events
            (
                id        TEXT NOT NULL UNIQUE,
                data      TEXT NOT NULL,
                current   BOOL DEFAULT 0,
                timestamp DATE
            )
        '''
    )

    cursor.execute(
        '''
        CREATE INDEX IF NOT EXISTS game.index_user ON users(id)
        '''
    )

    cursor.execute(
        '''
        CREATE INDEX IF NOT EXISTS game.index_event ON users(id)
        '''
    )

    print (
        'Initialized an empty database `game` with `users`, `tables` at `{}`.'
    ).format(dbpath)

    dbconn.commit()
    dbconn.close()


def load(dbpath, event, current=False):
    '''
    Load an event into the database.
    '''
    dbconn = sqlite3.connect(dbpath)
    cursor = dbconn.cursor()

    try:
        if current:
            cursor.execute(
                'UPDATE events set current = ?', (not current)
            )

        cursor.execute(
            'INSERT into events VALUES (?, ?, ?, ?)',
            (event['id'], json.dumps(event), current, int(time.time()))
        )

    except sqlite3.IntegrityError:
        print 'The event `{}` already exists, updating it.'.format(event['id'])
        cursor.execute(
            '''
            UPDATE events
            SET id = ?, current = ?, timestamp = ?, data = ?
            WHERE id = ?
            ''',
            (
                event['id'], current, int(time.time()),
                json.dumps(event), event['id']
            )
        )

    dbconn.commit()
    dbconn.close()
    print 'Database updated.'


def main():
    '''
    The main method, accept and parse arguments.
    '''
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
    parser.add_argument('-c', '--current', action='store_true', default=False,
                        help=current_help)
    parser.add_argument('-f', '--from-file', help=event_help)

    args = vars(parser.parse_args())

    if args['action'] == 'load' and args['from_file'] is None:
        print '{}: error: argument -f/--from-file is required'.format(__file__)
        exit(1)

    if args['action'] == 'load':
        event = json.loads(open(args['from_file'], 'r').read())
        load(args['database_path'], event, args['current'])
    else:
        init(args['database_path'])


if __name__ == '__main__':
    main()
