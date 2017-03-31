#! /usr/bin/env python2.7

'''
game.py: Server-side logic for riddlr.
'''

__author__ = "Srinidhi Kaushik"
__copyright__ = "Copyright (C) 2017 Srinidhi Kaushik"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Srinidhi Kaushik"
__email__ = "clickyotomy@"
__status__ = "Production"


import json
import time
import sqlite3
import itertools
from datetime import datetime, timedelta

import argon2

from flask import (
    Flask, render_template, abort,
    request, redirect, jsonify, session, g
)
from flask_login import (
    LoginManager, current_user, login_user,
    logout_user, login_required, UserMixin
)
from flask_seasurf import SeaSurf

from utils import (
    user_exists, event_start, fetch_event_data, validate_user, get_user_level,
    routing, get_level_data, validate_answer, increment, is_safe_url, trackr,
    admin, is_banned
)

# Application configuration path.
APP_CONFIG_PATH = './config.json'


# Authenticated users.
class User(UserMixin):
    '''
    Class for maintaining the state of the logged users; integrated with
    flask-login for user and session management.
    '''
    def __init__(self, username):
        self.id = username


# Load application configuration.
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


# Variable for development environemnt (set to `False` in production).
ENV_DEV = True

# Application configuration variables.
APP_CONFIG = load_config()

# Flask config: app name, configuration, secrets, logins, CSRF, etc.
app = Flask(__name__)
app.secret_key = APP_CONFIG['secret']
csrf = SeaSurf(app)

# flask-login stuff.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# Current year.
YEAR = datetime.now().year


# Establish connection to the database.
def get_db():
    '''
    Use database in the application cntext.
    '''
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(APP_CONFIG['dbpath'])
    return db


# Load the event data.
with app.app_context():
    EVENT_DATA = fetch_event_data(get_db().cursor(), APP_CONFIG['event'])


@app.teardown_appcontext
def teardown_db(_):
    '''
    Teardown sequence.
    '''
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Custom exception class.
class GameException(Exception):
    pass


@app.before_request
def make_session_permanent():
    '''
    Session lifetime.
    '''
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=12)


@login_manager.user_loader
def load_user(username):
    '''
    Callback method for login_manager.
    '''
    present = user_exists(get_db().cursor(), username)
    if not present:
        return None
    return User(username)


@app.route('/', methods=['GET'])
def home():
    '''
    The home-page.
    '''
    return render_template(
        'index.html',
        event=EVENT_DATA['name'],
        host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
        social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
        intro=EVENT_DATA['intro']
    )


@csrf.include
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Registers a user.
    '''
    hasher = argon2.PasswordHasher()
    reason = 'Unknown error.'
    if request.method == 'POST':
        try:
            uname = request.form.get('uname')
            pword = request.form.get('pword')

            if pword != request.form.get('pword_c'):
                reason = 'Passwords do not match.'
                raise GameException

            pword_hash = hasher.hash(pword)

            cursor = get_db().cursor()
            if not user_exists(cursor, uname):
                cursor.execute(
                    '''
                    INSERT INTO users
                    (id, password, event, level,
                    email, phone, ban, timestamp)
                    VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        uname, pword_hash, APP_CONFIG['event'], 1,
                        request.form.get('email'),
                        request.form.get('phone'),
                        False, int(time.time())
                    )
                )
                get_db().commit()
            else:
                reason = 'Username `{}` is already taken.'.format(uname)
                raise GameException

            reason = 'Successfully registered `{}`.'.format(uname)

        except GameException:
            return render_template(
                'register.html', event=EVENT_DATA['name'],
                host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
                social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
                error=True, reg=False, reason=reason, year=YEAR,
            )

        return render_template(
            'register.html', event=EVENT_DATA['name'],
            host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
            social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
            error=False, reg=True, reason=reason, year=YEAR,
        )

    else:
        return render_template(
            'register.html', event=EVENT_DATA['name'],
            host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
            social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
            error=False, reg=False, reason='', year=YEAR,
        )


@csrf.include
@app.route('/login', methods=['GET', 'POST'])
def login():
    reason = 'Unknown error.'
    redir = request.args.get('next')

    if redir is None:
        redir = ''
    else:
        redir = '?next={}'.format(redir)

    if not event_start(EVENT_DATA):
        if ENV_DEV:
            pass
        else:
            return redirect('/')

    if request.method == "POST":
        try:
            uname = request.form.get('uname').strip()
            pword = request.form.get('pword').strip()

            if validate_user(get_db().cursor(), uname, pword):
                auth_user = User(uname)
                login_user(auth_user)

                if request.args.get('next') is None:
                    if current_user.is_authenticated:
                        return redirect(
                            routing(
                                EVENT_DATA,
                                get_user_level(
                                    get_db().cursor(),
                                    current_user.id
                                ), 'path'
                            )
                        )

                if is_safe_url(request, request.args.get('next')):
                    return redirect(request.args.get('next'))
                else:
                    abort(400)
            else:
                reason = 'Incorrect username or password.'
                raise GameException
        except GameException:
            return render_template(
                'login.html', event=EVENT_DATA['name'],
                host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
                discuss=EVENT_DATA['discuss'], social=EVENT_DATA['social'],
                error=True, reason=reason, year=YEAR, next=redir
            )
    else:
        return render_template(
            'login.html', event=EVENT_DATA['name'],
            host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
            social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
            error=False, reason='', next=redir, year=YEAR
        )


@login_required
@app.route('/logout')
def logout():
    '''
    Log the user out of the application.
    '''
    logout_user()
    return redirect('/')


@app.route('/levels/<path:path>', methods=['GET', 'POST'])
@login_required
@csrf.include
def level(path):
    '''
    Display, the question, validate answers, hints and increment user level.
    '''
    if is_banned(get_db().cursor(), current_user.id):
        print 'here'
        return redirect('/logout')

    if not event_start(EVENT_DATA):
        if ENV_DEV:
            pass
        else:
            return redirect('/')

    level_index = routing(EVENT_DATA, path, 'index')
    user_index = get_user_level(get_db().cursor(), current_user.id)

    if level_index > user_index:
        return redirect(
            routing(EVENT_DATA, user_index, 'path')
        )

    data = get_level_data(EVENT_DATA, path)
    if data is None:
        return redirect('/')

    if request.method == 'POST':
        answer = request.form.get('answer')
        correct, hint, text = validate_answer(data, answer)
        if correct:
            if user_index == level_index:
                increment(
                    get_db(), current_user.id, (level_index + 1)
                )

            if (level_index + 1) > len(EVENT_DATA['levels']):
                return redirect('/congratulations')

            return redirect(
                routing(EVENT_DATA, (level_index + 1), 'path')
            )

        elif hint:
            return render_template(
                'level.html',
                year=YEAR, event=EVENT_DATA['name'],
                host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
                social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
                user=current_user.id, media=data['media']['type'],
                link=data['media']['url'], hint=hint, hint_text=text,
                text=data['text'], level=level_index, title=data['title'],
                source=data['source']
            )

    return render_template(
        'level.html',
        year=YEAR, event=EVENT_DATA['name'],
        host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
        social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
        user=current_user.id, media=data['media']['type'],
        link=data['media']['url'], hint=False, hint_text='',
        text=data['text'], level=level_index, title=data['title'],
        source=data['source']
    )


@app.route('/congratulations')
@login_required
@csrf.include
def finish():
    '''
    The finish page.
    '''
    user_index = get_user_level(get_db().cursor(), current_user.id)

    if user_index < len(EVENT_DATA['levels']):
        return redirect(
            routing(EVENT_DATA, user_index, 'path')
        )

    else:
        return render_template(
            'finish.html',
            year=YEAR, event=EVENT_DATA['name'],
            host=EVENT_DATA['host'], faq=EVENT_DATA['faq'],
            social=EVENT_DATA['social'], discuss=EVENT_DATA['discuss'],
            user=current_user.id, message=EVENT_DATA['finish']
        )


@app.route('/tracker', methods=['GET'])
@login_required
def tracker():
    '''
    Method to track leaderboard scores.
    '''
    if not event_start(EVENT_DATA):
        if ENV_DEV:
            pass
        else:
            return jsonify({
                'users': []
            }), 403

    data = {'users': []}
    players = trackr(get_db().cursor(), APP_CONFIG['trackr'])
    for player in players:
        data['users'].append({
            'name': player[0],
            'level': player[1]
        })

    return jsonify(data)


# Custom error handlers.
@app.errorhandler(404)
def page_not_found(error):
    return render_template(
        'error.html', error=error, code=404,
        event=EVENT_DATA['name']
    ), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template(
        'error.html', error=error, code=500,
        event=EVENT_DATA['name']
    ), 500


@app.errorhandler(403)
def forbidden(error):
    return render_template(
        'error.html', error=error, code=403,
        event=EVENT_DATA['name']
    ), 403


@app.errorhandler(401)
def unauthorized(error):
    return render_template(
        'error.html', error=error, code=401,
        event=EVENT_DATA['name']
    ), 401


@app.route('/sudo')
def sudo():
    '''
    Administrator access.
    Must pass the `X-Auth-Token` to access this route.
    Please do not check-in to the repository or expose
    the token anywhere. For the current configuration,
    `X-Auth-Token` is stored in APP_CONFIG['sudo']
    (file: ./config.json).
    '''
    header = request.headers.get('X-Auth-Token')
    table = request.args.get('table')

    if header is None or header != APP_CONFIG['sudo']:
        return jsonify({
            'error': 401,
            'message': 'Invalid credentials.'
        }), 401

    if table not in ['users', 'events']:
        return jsonify({
            'error': '404',
            'message': 'Unable fetch data from table `{}`.'.format(table)
        })

    else:
        data = admin(get_db().cursor(), table)
        result = {table: []}
        if table == 'users':
            colums = ['id', 'level', 'email', 'phone', 'timestamp', 'ban']
            for user in data:
                result[table].append(dict(itertools.izip(colums, user)))
        else:
            colums = ['id', 'data', 'current', 'timestamp']
            for event in data:
                result[table].append(dict(itertools.izip(colums, event)))

        return jsonify(result)


@app.route('/ping')
def ping():
    '''
    Server healthcheck.
    '''
    return '', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=ENV_DEV, threaded=False)
