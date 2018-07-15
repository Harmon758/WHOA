# -*- coding: utf-8 -*-

import datetime
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

app = Flask("angelhack")
app.config["SECRET_KEY"] = "3871897312"
app.url_map.strict_slashes = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db_connector = db.WHOADatabase(app)


@login_manager.user_loader
def load_user(email):
	try:
		return db_connector.get_user(email)
	except db.DatabaseException:
		return

"""
@app.route("/logout")
def logout():
	logout_user()
	return render_template("logout.html")
"""

@app.route("/")
def index():
	return render_template("index.html")


@app.route("/login", methods=("GET", "POST"))
def login():
	if request.method == "POST":
		return redirect(f"/communities/{request.form['community']}/login")
	return render_template("login.html", communities=db_connector.list_communities())
	

@app.route("/register", methods=("GET", "POST"))
def register():
	if request.method == "GET":
		return render_template("register.html")
	
	is_admin = "admin_submit" in request.form
	if is_admin:
		prefix = "admin_"
	else:
		prefix = "user_"
	
	errors = False
	if request.form[prefix + "email_confirm"] != request.form[prefix + "email"]:
		errors = True
		flash("Emails must match.")
	if request.form[prefix + "password_confirm"] != request.form[prefix + "password"]:
		errors = True
		flash("Passwords must much.")
	if "@" not in request.form[prefix + "email"]:
		errors = True
		flash("Please enter a valid email.")
	if errors:
		return redirect(url_for("register"))
	
	try:
		if is_admin:
			db_connector.add_community(
				name=request.form["community_name"],
				admin_email=request.form["admin_email"],
				admin_password=request.form["admin_password"],
				invite_code=request.form["referral"]
			)
			return redirect(f"/communities/{request.form['community_name']}/admin")
		else:
			community = db_connector.get_community(invite_code = request.form["invite_code"])
			db_connector.add_user(
				name=f"{request.form['first_name']} {request.form['last_name']}",
				email=request.form["user_email"],
				password=request.form["user_password"],
				address=request.form["address"],
				phone_number=request.form["phone_number"],
				community=community["name"]
			)
			return redirect(f"/communities/{community['name']}")
	except db.DatabaseException as e:
		flash(str(e))
		return redirect(url_for("register"))


@app.route('/communities/<string:community_name>')
@login_required
def community_dashboard(community_name):
	try:
		community = db_connector.get_community(community_name)
	except db.DatabaseException as e:
		return error(f"Unable to find community {community_name}")
	return render_template("overview.html", community_data=community)


@app.route("/communities/<string:community_name>/noticeboard", methods=("GET", "POST"))
@login_required
def community_noticeboard(community_name):
	if request.method == "GET":
		try:
			community = db_connector.get_community(community_name)
		except db.DatabaseException as e:
			return error(f"Unable to find community {community_name}")
		noticeboard = db_connector.get_noticeboard(community_name)
		return render_template("noticeboard.html", community_data=community, noticeboard=noticeboard)
	
	noticeboard = db_connector.get_noticeboard(community_name)
	noticeboard.add_notice(poster=current_user.name, content=request.form["notice"], timestamp = datetime.datetime.utcnow())
	return redirect(f"/communities/{community_name}/noticeboard")


@app.route("/communities/<string:community_name>/login", methods=("GET", "POST"))
def community_login(community_name):
	if request.method == "GET":
		return render_template("community-login.html", community_name=community_name)
	
	is_admin = "admin_submit" in request.form
	if (is_admin and "@" not in request.form["admin_email"]) or (not is_admin and "@" not in request.form["user_email"]):
		flash("Please enter a valid email.")
		return redirect(f"/communities/{community_name}/login")
	
	try:
		if is_admin:
			valid = db_connector.check_admin_password(request.form["admin_email"], request.form["admin_password"])
		else:
			user = db_connector.get_user(request.form["user_email"])
			valid = user.check_password(request.form["user_password"])
	except db.DatabaseException as e:
		flash(str(e))
		return redirect(f"/communities/{community_name}/login")
	
	if not valid:
		flash("Password incorrect.")
		return redirect(f"/communities/{community_name}/login")
	
	if is_admin:
		return redirect(f"/communities/{community_name}/admin")
	else:
		login_user(user)
		return redirect(f"/communities/{community_name}")
	

@app.route("/error")
def error(error_message):
	return render_template("error.html", error=error_message)

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)