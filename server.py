#!/usr/bin/env python
##################################################
#
# Code by Jioh L. Jung <ziozzang@gmail.com>
#
##################################################

# Import Flask Restful API library
from flask import Flask, request, abort, jsonify, make_response

# Import API
from conf import *
import clairdb

# Import OS
import os

# Process JSON
import json

####################################################
# Environment Override
if "DB_IP" in os.environ:
  DB_IP = os.environ["DB_IP"]

if "DB_PORT" in os.environ:
  DB_PORT = os.environ["DB_PORT"]

if "DB_ID" in os.environ:
  DB_ID = os.environ["DB_ID"]

if "DB_PW" in os.environ:
  DB_PW = os.environ["DB_PW"]

if "DEBUG" in os.environ:
  if os.environ["DEBUG"].lower()[0] == "y" or \
     os.environ["DEBUG"].lower()[0] == "t":
    DEBUG = True
  elif os.environ["DEBUG"].lower()[0] == "n" or \
       os.environ["DEBUG"].lower()[0] == "f":
    DEBUG = False

if "BIND_ADDR" in os.environ:
  BIND_ADDR = os.environ["BIND_ADDR"]
    
app = Flask(__name__)
conn = clairdb.conn_db(DB_IP,DB_PORT,DB_ID,DB_PW)

####################################################
# Security Scanning
@app.route('/', methods=['PUT', 'POST'])
def check_security():
    global conn
    body = request.get_json()#silent=True)
    print body["osver"]
    print body["packages"]
    if conn.closed != 0:
        conn = clairdb.conn_db(DB_IP,DB_PORT,DB_ID,DB_PW)
    res = clairdb.check(conn, body["osver"],body["packages"])
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

####################################################
if __name__ == '__main__':
	app.run(host=BIND_ADDR, debug=DEBUG)
