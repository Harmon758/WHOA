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
			community.add_user(
				name=f"{request.form['first_name']} {request.form['last_name']}",
				email=request.form["user_email"],
				password=request.form["user_password"],
				address=request.form["address"],
				phone_number=request.form["phone_number"]
			)
			return redirect(f"/communities/{community.name}")
	except db.DatabaseException as e:
		flash(str(e))
		return redirect(url_for("register"))


@app.route('/communities/<string:community_name>')
def community_dashboard(community_name):
	try:
		community = db_connector.get_community(community_name)
	except db.DatabaseException as e:
		return error(f"Unable to find community {community_name}")
	return render_template("communities.html", community_data=community)


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
			community = db_connector.get_community(name=community_name)
			valid = community.check_user_password(request.form["user_email"], request.form["user_password"])
	except db.DatabaseException as e:
		flash(str(e))
		return redirect(f"/communities/{community_name}/login")
	
	if not valid:
		flash("Password incorrect.")
		return redirect(f"/communities/{community_name}/login")
	
	login_user()
	return redirect(f"/communities/{community_name}")
	

@app.route("/error")
def error(error_message):
	return render_template("error.html", error=error_message)

if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)