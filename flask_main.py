"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates:
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will
   - User input/output is in local (to the server) time.
"""

import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

from bson.objectid import ObjectId  # Added to retrieve objectID for deletion

# Date handling
import arrow    # Replacement for datetime, based on moment.js
# import datetime # But we may still need time
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient
import secrets.admin_secrets
import secrets.client_secrets
MONGO_CLIENT_URL = "mongodb://{}:{}@localhost:{}/{}".format(
    secrets.client_secrets.db_user,
    secrets.client_secrets.db_user_pw,
    secrets.admin_secrets.port,
    secrets.client_secrets.db)

###
# Globals
###
import CONFIG
app = flask.Flask(__name__)
app.secret_key = CONFIG.secret_key

####
# Database connection per server process
###

try:
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, secrets.client_secrets.db)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)


###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    g.memos = get_memos() #Returns memos in sorted order
    for memo in g.memos:
        app.logger.debug("Memo: " + str(memo))
    return flask.render_template('index.html')


@app.route("/create")
def create():
    app.logger.debug("Create")

    return flask.render_template('create.html')


@app.route("/store_data", methods=["POST"])
def store_data():
    app.logger.debug("Storing Data")
    text = request.form["text"]
    date = request.form["date"]

    if len(date) is not 0: #check for no date len() = 0 means no entry
      month, day, year = date.split('/')
      arrow_date = arrow.get(year + '-' + month + '-' + day)

      tzlocal_date = convert_to_tzlocal(arrow_date)
    else:
      tzlocal_date = convert_to_tzlocal(arrow.now())
    store_document(tzlocal_date,text)

    return flask.redirect(url_for("index"))


@app.route("/delete_data")
def delete_data():
    app.logger.debug("Deleting Data")
    boxes = request.args.get("allChecked", type=str) #Checkbox number location
    boxes = list(boxes.split(','))

    remove_document(boxes)

    return flask.jsonify(result=True)


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################


@app.template_filter('humanize')
def humanize_arrow_date(date):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case.
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else:
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except:
        human = date
    return human


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = []
    for record in collection.find({"type": "dated_memo"}):
        record['date'] = arrow.get(record['date']).isoformat()
        #del record['_id']
        records.append(record)
    return sort_memos(records)

def sort_memos(memos):
    return sorted(memos, key=lambda memo: memo['date'])

def convert_to_tzlocal(date):
    return date.replace(tzinfo=tz.tzlocal())

def store_document(date,text):
    record = {"type": "dated_memo",
              "date": date.isoformat(),
              "text": text
              }
    collection.insert(record)

def remove_document(checkboxes):

    memos = get_memos()
    for i in range(len(memos)):
        if (str(i) in checkboxes):
            collection.remove({"_id": ObjectId(memos[i]['_id'])})

if __name__ == "__main__":
    app.debug = CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT, host="0.0.0.0")
