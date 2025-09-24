from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
import db
import connect
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'svs_secret_2025'  # Set a secret key for session/flash

# Initialize database connection
db.init_db(
    app, connect.dbuser, connect.dbpass, connect.dbhost, connect.dbname, connect.dbport
)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/services", methods=["GET"])
def service_list():
    cursor = db.get_cursor()
    # Lists all services        
    qstr = "SELECT service_name, price FROM services;" 
    cursor.execute(qstr)        
    services = cursor.fetchall()
    cursor.close()
    if True:  # Example condition for a flash message
        flash("Example of a flash message. Optional, but good for error or confirmation " \
            "messages when used with an IF statement.", "info")
    return render_template("service_list.html", services=services)


@app.route("/customers")
def customer_list():
    # Add your code here to list customers
    return render_template("customer_list.html")


# Add other routes and view functions as required.

