#! /usr/bin/env python2.7

'''
stats.py: Fetch stats from the database.
'''
__author__ = "Srinidhi Kaushik"
__copyright__ = "Copyright (C) 2017 Srinidhi Kaushik"
__license__ = "MIT"
__version__ = "0.2"
__maintainer__ = "Srinidhi Kaushik"
__email__ = "clickyotomy@"
__status__ = "Production"


import re
import time
import json
import argparse
from operator import itemgetter

import requests
import tabulate


# API URL of the server.
API_URL = 'http://{}/sudo'.format

# Fetch X-Auth-Token from `config.json`.
APP_CONFIG_PATH = './config.json'


def load_config():
    '''
    Load configuration variables from `config.json`.
    '''
    try:
        with open(APP_CONFIG_PATH, 'r') as config:
            return json.loads(config.read())
    except (IOError, KeyError, ValueError) as err:
        print ': '.join([type(err).__name__, str(err)]) + '.'
        exit(1)


# Authentication token. Must be the same value as `sudo` in `config.json`.
X_AUTH_TOKEN = {
    'X-Auth-Token': load_config()['sudo']
}


def http_debug(response):
    '''
    Print the request/response debug log.
    '''
    print 'http-request\n{0}\n'.format('-' * len('http-request'))
    print 'url ({0}): {1}'.format(response.request.method,
                                  response.request.url)
    print 'request-headers:'
    print json.dumps(dict(response.request.headers), indent=4)
    if response.request.method != 'GET':
        if response.request.body:
            print 'request-payload:'
            print json.dumps(json.loads(response.request.body), indent=4)
    print '\nhttp-response\n{0}\n'.format('-' * len('http-response'))
    print 'status-code: {0} {1}'.format(response.status_code, response.reason)
    print 'url: {0}'.format(response.url)
    print 'time-elapsed: {0}s'.format(response.elapsed.total_seconds())
    print 'response-headers:'
    print json.dumps(dict(response.headers), indent=4)
    print 'response-content:'
    try:
        print None if response.content is '' else json.dumps(response.json(),
                                                             indent=4)
    except (KeyError, ValueError):
        print '{}'


def fetch(host, table, debug=False):
    '''
    Does an HTTP GET to the API endpoint.
    '''
    url = API_URL(host.strip())

    try:
        response = requests.get(
            url, params={'table': table},
            headers=X_AUTH_TOKEN, allow_redirects=False
        )
        if debug:
            http_debug(response)

        if response.status_code in range(200, 400):
            return response.json()

    except (ValueError, KeyError) as _error:
        error = ': '.join([type(_error).__name__, str(_error)])
        if debug:
            print 'error:\n{0}\n{1}\n'.format('-' * len(error), error)

    except (requests.exceptions.RequestException) as _error:
        error = ': '.join([type(_error).__name__, str(_error)])
        if debug:
            print 'error:\n{0}\n{1}\n'.format('-' * len(error), error)

    return None


def constraints(filters):
    '''
    Filter out data, if required.
    '''
    data = fetch(filters['server'], filters['table'], filters['debug'])

    if data is not None:
        if filters['table'] == 'events':
            return data['events']
        else:
            response = []
            response = [_ for _ in data['users']
                        if re.search(filters['filter'], _['id'])]
            if not filters['ban']:
                response = [_ for _ in response if not _['ban']]

            response = [_ for _ in response if
                        filters['since'] <= _['timestamp'] <= filters['until']
                        ]
            response = sorted(response, key=itemgetter('timestamp'),
                              reverse=filters['reverse'])
            response = response[:filters['limit']]

            return response


def main():
    '''
    Parse arguments, fetch data.
    '''
    description = 'Fetch stats from the game database.'
    socket = 'hostname[:port] of the API server'
    users = 'fetch data from the `users` table'
    events = 'fetch data from the `events` table'
    reverse = 'list active users in reverse chronological order.'
    limit = 'limit the output to N users'
    ban = 'include banned users in the output'
    since = 'list users active since N (timestamp, UTC; default: epoch)'
    until = 'list users active until N (timestamp, UTC; default: now)'
    debug = 'enable debug logs'
    user = 'A valid regular expression for filtering users (default: `.*``)'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--server', help=socket, required=True)

    subparsers = parser.add_subparsers(
        help='sub-commands that can be chosen from',
        description='operations on tables', dest='table'
    )

    users = subparsers.add_parser('users', description=users)
    events = subparsers.add_parser('events', description=events)

    users.add_argument('-l', '--limit', type=int, help=limit, default=None)
    users.add_argument(
        '-r', '--reverse', help=reverse, action='store_true', default=False
    )
    users.add_argument(
        '-b', '--ban', help=ban, action='store_true', default=False
    )
    users.add_argument('-s', '--since', help=since, default=0, type=int)
    users.add_argument(
        '-u', '--until', help=until, default=int(time.time()), type=int
    )
    users.add_argument(
        '-d', '--debug', help=debug, action='store_true', default=False
    )
    users.add_argument(
        '-f', '--filter', help=user, type=str, default='.*'
    )
    events.add_argument(
        '-d', '--debug', help=debug, action='store_true', default=False
    )

    args = vars(parser.parse_args())

    data = constraints(args)

    if args['table'] == 'events':
        for event in data:
            print json.dumps(json.loads(event['data']), indent=4)
            print 'current: {0}, timestamp: {1}.'.format(
                                                    event['current'],
                                                    event['timestamp']
            )
    else:
        headers = data[0].keys() if len(data) else []
        print tabulate.tabulate(
                [_.values() for _ in data], headers=headers, tablefmt='psql')
    print 'count: {}.'.format(len(data))


if __name__ == '__main__':
    main()
