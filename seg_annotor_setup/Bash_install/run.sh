#!/bin/bash
set -e
apt-get install python3-dev
apt-get install python3-pip
#apt-get install python-flask
#apt-get install python-bson
pip install datatables
pip3 install -U flask-cors
pip3 install bson flask flask-login pandas pymongo webcolors pyopenssl flask_socketio

