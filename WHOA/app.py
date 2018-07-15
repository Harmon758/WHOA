# -*- coding: utf-8 -*-

import os
import sys

from flask import (
	Flask,
	flash,
	redirect,
	render_template,
	request,
	send_from_directory,
	session,
	url_for,
)

from flask_login import (
	LoginManager,
	login_required,
	current_user,
	login_user,
	logout_user,
)

from flask_pymongo import PyMongo

from model import db
from utils import validate_login_form, validate_register_form

app = Flask("angelhack")
app.config["SECRET_KEY"] = "3871897312"

login_manager = LoginManager()
login_manager.init_app(app)

db_connector = db.WHOADatabase(app)

"""
@login_manager.user_loader
def user_loader(email):
	if email not in users:
		return

	user = Manager()
	user.id = email  # SamAccountName
	user.name = users[user.id]  # Real name
	return user

@login_manager.request_loader
def request_loader(request):
	email = request.form.get("email")
	if email is not None:
		email = email.split("@")[0]
		if email not in users:
			if os.environ["FLASK_ENV"] == "development":
				print("In request_loader...")
				print(email)
			return

		user = Manager()
		user.id = email  # SamAccountName
		user.name = users[user.id]  # Real name
		if _users_manager.is_valid:
			return user

@login_manager.unauthorized_handler
def unauthorized_handler():
	flash("Please login first.")
	return redirect(url_for("login"))
"""

@app.route("/")
def index():
	return render_template("index.html")


"""
@app.route("/logout")
def logout():
	logout_user()
	return render_template("logout.html")
"""

@app.route("/login")
def login():
	return render_template("login.html")
	

@app.route("/register", methods=("GET", "POST"))
def register():
	if request.method == "POST":
		errors = validate_register_form(dict(request.form), db_connector)
		if errors:
			for error in errors:
				flash(error)
			return redirect(url_for("register"))
		if "admin_submit" in request.form:
			return redirect(f"/communities/{request.form['community_name']}/admin")
		else:
			return redirect(f"/communities/{request.form['community_name']}")
	return render_template("register.html")


@app.route('/communities/<string:community_name>')
def community_dashboard(community_name):
	try:
		community = db_connector.get_community(community_name)
	except db.DatabaseException as e:
		return error(f"Unable to find community {community_name}")
	return render_template("communities.html", community_data=community)


@app.route("/communities/<string:community_name>/login", methods=("GET", "POST"))
def community_login(community_name):
	if request.method == "POST":
		errors = validate_login_form(dict(request.form), db_connector, community_name)
		if errors:
			for error in errors:
				flash(error)
			return redirect(url_for(f"/communities/{community_name}/login"))
		else:
			login_user()
			return redirect(f"/communities/{community_name}")
	return render_template("login.html")
	

@app.route("/error")
def error(error_message):
	return render_template("error.html", error=error_message)

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)