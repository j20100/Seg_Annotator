#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import base64
from bson import ObjectId
import datetime
from flask import Flask, Markup, Response, abort, escape, flash, redirect, \
                  render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, \
                        login_user, logout_user
from werkzeug import secure_filename
from functools import wraps
from gridfs import GridFS
from jinja2 import evalcontextfilter
from binascii import a2b_base64
from OpenSSL import SSL

from flask import session
from flask_socketio import SocketIO, emit

import json
import hashlib
import pandas as pd
import pymongo
import re
import subprocess
import threading
import time
import uuid
import urllib.parse
import webcolors
import os
import time
import glob

from flask_cors import CORS

curr_annotated_img = []

def hash_password(password):
    """This function hashes the password with SHA256 and a random salt"""
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    """This function checks a password against a SHA256:salt entry"""
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def admin_required(func):
    """Function wrapper to allow only logged in admins to access the page."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return redirect(url_for('bad_permissions'))
        return func(*args, **kwargs)
    return decorated_function

# Load default configuration from local file
with open('config.json') as config:
    conf = argparse.Namespace(**json.load(config))

# Argument parser strings
app_description = "annotator Website Application\n\n" \
        "All information can be found at https://github.com/annotatorus.\n" \
        "Modify file 'config.json' to edit the application's configuration.\n" \
        "There are other command line arguments that can be used:"

help_host = "Hostname of the Flask app. Default: {0}".format(conf.app_host)
help_port = "Port of the Flask app. Default: {0}".format(conf.app_port)
help_debug = "Start Flask app in debug mode. Default: {0}".format(conf.debug)


# Set up the command-line arguments
parser = argparse.ArgumentParser(description=app_description,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-H', '--app_host', help=help_host, default=conf.app_host)
parser.add_argument('-P', '--app_port', help=help_port, default=conf.app_port)
parser.add_argument('-D', '--debug', dest='debug', action='store_true', help=help_debug)
parser.set_defaults(debug=conf.debug)

# Update default configs with command line args
args = parser.parse_args()
conf.__dict__.update(args.__dict__)

# Get MongoDB Database Client
client = pymongo.MongoClient()
annotator = client['annotator']
fs = GridFS(annotator)

# Validate MongoDB is started, else exit
try:
    client.server_info()
except pymongo.errors.ServerSelectionTimeoutError:
    print('MongoDB is not started. Restart it before launching the web app again.')
    quit()

# Create Flask Application
app = Flask(__name__)
CORS(app)
app.secret_key = uuid.uuid4().hex  # Required to use log in and session manager
login_manager = LoginManager()
login_manager.init_app(app)

# ROS variable
ros_pid = None

socketio = SocketIO(app)

@socketio.on('disconnect')
def disconnect_user():
    print('DISCONNECTING USER')
#    user_logs = list(annotator.logs.find().skip((annotator.logs).count() - 1))
#    user = user_logs[-1]
#    annotator.logs.update_one(user, {'$set' : { 'stop_time' : time.time()}})
    logout_user()
#    session.pop(app.secret_key, None)

# User class
class User(UserMixin):
    """User Class making DB-stored parameters accessible from HTML templates."""
    def __init__(self, username):
        self.username = username
        user = annotator.credentials.find_one({'username': username})
        self.admin = user['admin']
        self.nb_images = user['nb_images']

    def get_id(self):
        return self.username

    def is_admin(self):
        return self.admin

# Login Manager Configuration
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

# Application routes
@app.route('/')
def go_home():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        next_page = request.args.get('next')
        username = request.form['username']
        password = request.form['password']
        user = annotator.credentials.find_one({'username': username})
        if user and check_password(user['password'], password):
            if user['active']:  # Inactived users should not be able to log in
                login_user(User(username))
                annotator.credentials.update_one(user, {'$set':
                                              {'last_login' : time.time()}})

                # If an admin logs in and there is at least one inactived user, show it
                if user['admin'] and annotator.credentials.find_one({'active': False}):
                    flash('At least one user account has to be activated', 'info')
                    return redirect(url_for('manage_users'))
                annotator.logs.insert_one({'start_time' : time.time(),
                                        'username' : username,
                                        'stop_time' : 0,
                                        'nb_images' : 0})
                return redirect(next_page or url_for('home'))
            else:
                flash('Account not yet activated by an administrator', 'warning')
        else:
            flash('Invalid credentials', 'danger')
        return render_template('login.html')

    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():

    user_logs = list(annotator.logs.find().skip((annotator.logs).count() - 1))

    user = user_logs[-1]

    annotator.logs.update_one(user, {'$set' : { 'stop_time' : time.time()}})
    logout_user()
    return redirect(url_for('home'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        next = request.args.get('next')
        username = request.form['username'].strip()
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if not password:
            flash('Password cannot be empty', 'danger')
            return render_template('create_account.html')

        if password != password_confirm:
            flash('Both password entries do not match', 'danger')
            return render_template('create_account.html')

        if not username.replace('_', '').isalnum():
            # Only allow letters, numbers and underscore characters in usernames
            flash('Invalid username (letters, numbers and underscores only)', 'danger')
            return render_template('create_account.html')

        user = annotator.credentials.find_one({'username': username})
        if user or not username:  # Check if username is not empty or already taken
            flash('Username not available', 'danger')
            return render_template('create_account.html')

        active = False
        admin = False

        # If this is the first user to register, make it active and admin
        if not annotator.credentials.find_one():
            active = True
            admin = True
            flash('First account created, activated and is administrator, congratulations!', 'success')

        # Create a new user account
        annotator.credentials.insert_one({'username': username,
                                     'password': hash_password(password),
                                     'active': active,
                                     'nb_images' : 0,
                                     'admin': admin})
        flash('Account created successfully', 'success')
        return redirect(url_for('login'))

    else:
        return render_template('create_account.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        user = annotator.credentials.find_one({'username': username})
        if user and check_password(user['password'], old_password):
            if not new_password:
                flash('Password cannot be empty', 'danger')
                return render_template('change_password.html')

            # Modify password
            annotator.credentials.update_one(user, {'$set': {
                                          'password': hash_password(new_password)}})
            flash('Password changed successfully', 'success')
            return redirect(url_for('login'))

        else:
            flash('Invalid credentials', 'danger')
            return render_template('change_password.html')

    else:
        return render_template('change_password.html')

@app.route('/home')
def home():
    return render_template('index.html')

def sortKeyFunc(s):
    t = s.split('/')
    k=t[3].split('.')
    s=k[0].split('_')
    return int(s[2])

@app.route('/load_new_img', methods = ['POST'])
def uploader_new_img():
   if request.method == 'POST':

        global curr_annotated_img
        directory = "static/data/annotations/"

        searchlabel = os.path.join(directory, "*.png" )
        fileslabel = glob.glob(searchlabel)
        fileslabel.sort(key=sortKeyFunc)

        i = 0
        #print("Doin the currently annotated img now")
        #print(curr_annotated_img)
        #print(fileslabel[i])
        while fileslabel[i] in curr_annotated_img :
            i=i+1

        #print("THIS ONE PASED")
        #print(fileslabel[i])

        newImgAnnot = fileslabel[i]



        t = fileslabel[i].split('/')
        #print(t)
        newImg=t[0]+"/"+t[1]+"/"+"images"+"/"+t[3]

        #print("Sending new img")
        #print(newImg)
        #print("Sending new img annot")
        #print(newImgAnnot)
        send = newImg+":"+newImgAnnot
        #print(send)

        curr_annotated_img.append(newImgAnnot)

        return send

@app.route('/uploader', methods = ['POST'])
def uploader_file():
   if request.method == 'POST':
        pic = request.form['file']
        username = request.form['username']
        filename = request.form['filename']
        #f.save(secure_filename(f.filename))

        up = urllib.parse.urlparse(pic)
        head, data = up.path.split(',', 1)
        bits = head.split(';')
        mime_type = bits[0] if bits[0] else 'text/plain'
        charset, b64 = 'ASCII', False
        for bit in bits:
            if bit.startswith('charset='):
                charset = bit[8:]
            elif bit == 'base64':
                b64 = True

        binary_data = a2b_base64(data)
        directory = "static/data/annotations/"
        test = os.listdir( directory )

        for item in test:
            if item.startswith(filename):
                os.remove( os.path.join( directory, item ) )

        timestr = time.strftime("%Y%m%d-%H%M%S")

        with open("static/data/annotations/" + filename + "_corrected_" + timestr, 'wb') as f:
            f.write(binary_data)

        user = annotator.credentials.find_one({'username': username})
        user_logs = list(annotator.logs.find().skip((annotator.logs).count() - 1))

        user_stats = user_logs[-1]
        nb_images = user['nb_images']
        nb_images = nb_images + 1
        nb_images_stats = user_stats['nb_images']
        nb_images_stats = nb_images_stats + 1
        annotator.logs.update_one(user_stats, {'$set': {'nb_images': nb_images_stats}})
        annotator.credentials.update_one(user, {'$set': {'nb_images': nb_images}})

        searchlabel = os.path.join(directory, "*.png" )
        fileslabel = glob.glob(searchlabel)
        fileslabel.sort()

        return "Done sending imges"

@app.route('/updater', methods = ['POST'])
def updater_URL():
   if request.method == 'POST':
        annotURL = request.form["URL"]

        directory = "static/data/annotations/"
        test = os.listdir(directory)
        realURL = "NONE"
        for item in test:
            if item.startswith(annotURL[25:]):
                realURL = item

        return "static/data/annotations/" + realURL

@app.route('/annotator')
@login_required
def annotator_edit():
    username = current_user.get_id()
    return render_template('annotator.html', username=username)

@app.route('/dataset')
@login_required
def dataset():
    username = current_user.get_id()
    return render_template('dataset.html', username=username)

@app.route('/logs')
@admin_required
def logs():
    logs = list(annotator.logs.find())
    return render_template('logs.html', logs=logs)

@app.route('/logs/<start_time>')
def log_highlights(start_time):
    if not valid_protocol(start_time):
        return redirect(url_for('logs'))

    # Get database of current protocol
    db = client[protocol]
    started = db.steps.count()
    done = db.steps.count({'end': {'$exists': True}})
    info = db.protocol.find_one()
    json_protocol = {}
    if info:
        # Pretty print the raw protocol
        json_protocol = json.dumps(info['protocol'], indent=4, sort_keys=True)

    return render_template('log_highlights.html', active='Highlights', \
                           protocol=protocol, json_protocol=json_protocol, \
                           started=started, done=done, db=db)

@app.route('/logs/delete/<id>')
@login_required
@admin_required
def delete_logs(id):

    # Delete all data from current protocol
    print('DELETING THE LOG')
    test = annotator.logs.find()
    print(test)
    test_list = list(annotator.logs.find())
    print(test_list)
    one = annotator.test_list.find({'_id' : id})
    print(one)
    annotator.logs.remove({})

    flash("Entry {0} deleted successfully".format(id), 'info')
    return redirect(url_for('logs'))

@app.route('/manage_users')
@login_required
@admin_required
def manage_users():
    user_list = list(annotator.credentials.find())
    return render_template('manage_users.html', users=user_list)

@app.route('/manage_users/activate/<username>')
@login_required
@admin_required
def activate_user(username):
    """Activate a user account."""
    user = annotator.credentials.find_one({'username': username})
    if not user['active']:
        annotator.credentials.update_one(user, {'$set': {'active': True}})
        flash("User {0} activated successfully".format(username), 'success')
    else:
        flash("User {0} is already active".format(username), 'warning')

    return redirect(url_for('manage_users'))

@app.route('/manage_users/demote/<username>')
@login_required
@admin_required
def demote_user(username):
    """Remove admin privileges of another administrator."""
    user = annotator.credentials.find_one({'username': username})
    if current_user.get_id() == username:
        flash('Cannot revert yourself to standard user', 'danger')
    elif user:
        if user['admin']:
            annotator.credentials.update_one(user, {'$set': {'admin': False}})
            flash("User {0} reverted to standard user successfully".format(username), 'info')
        else:
            flash("User {0} is already a standard user".format(username), 'warning')
    else:
        flash("Cannot revert unknown user {0} to standard user".format(username), 'warning')

    return redirect(url_for('manage_users'))

@app.route('/manage_users/promote/<username>')
@login_required
@admin_required
def promote_user(username):
    """Give admin privileges from a normal user."""
    user = annotator.credentials.find_one({'username': username})
    if user:
        if user['admin']:
            flash("User {0} is already an administrator".format(username), 'warning')
        else:
            annotator.credentials.update_one(user, {'$set': {'admin': True}})
            flash("User {0} promoted to administrator successfully".format(username), 'info')
    else:
        flash("Cannot promote unknown user {0} to administrator".format(username), 'warning')

    return redirect(url_for('manage_users'))

@app.route('/manage_users/delete/<username>')
@login_required
@admin_required
def delete_user(username):
    """Delete a user account that is not yours."""
    user = annotator.credentials.find_one({'username': username})
    if current_user.get_id() == username:
        flash('Cannot delete yourself', 'danger')
    elif user:
        annotator.credentials.delete_one(user)
        flash("User {0} deleted successfully".format(username), 'info')
    else:
        flash("Cannot delete unknown user {0}".format(username), 'warning')

    return redirect(url_for('manage_users'))

@app.route('/bad_permissions')
def bad_permissions():
    """Function called if a normal user tries to get to an admin reserved page."""
    return render_template('bad_permissions.html')

@app.errorhandler(404)
def page_not_found(error):
    """This method handles all unexisting route requests."""
    return render_template('404.html'), 404

# Add objects that can be called from the Jinja2 HTML templates
@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    """Converts new lines to paragraph breaks in HTML."""
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
    result = '\n\n'.join('<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    result = result.replace(' ', '&nbsp;')
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def convert_ts(ts):
    """Convert timestamp to human-readable string"""
    return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

def format_sidebar(name, icon, url):
    """
    Used to generate HTML line for sidebar in layout.html.
        - name is the name of the tab
        - icon is the glyphicon name
    """

    current_url = request.path.split('/')[1]
    active = ' class="active"' if url == current_url else ''
    html = '<li{0}><a href="/{1}"><i style="float:left; margin-right: 14px;">' \
           '<span class="glyphicon glyphicon-{2}"></span></i>{3}' \
           '</a></li>'.format(active, url, icon, name)

    return Markup(html)

# Make some variables and functions available from Jinja2 HTML templates
app.jinja_env.globals.update(conf=conf,
                             force_type = Markup('onselect="return false" ' \
                                          'onpaste="return false" ' \
                                          'oncopy="return false" ' \
                                          'oncut="return false" ' \
                                          'ondrag="return false" ' \
                                          'ondrop="return false" ' \
                                          'autocomplete=off'),
                             format_sidebar=format_sidebar,
                             convert_ts=convert_ts)

# Start the application
if __name__ == '__main__':

    #context = SSL.Context(SSL.TLSv1_2_METHOD)
    #context.use_privatekey_file('host.key')
    #context.use_certificate_file('host.cert')

    socketio.run(app, host=conf.app_host, port=int(conf.app_port), ssl_context=('cert.pem', 'key.pem'))
