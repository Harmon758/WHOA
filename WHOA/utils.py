# -*- coding: utf-8 -*-

from model import db

def validate_login_form(form, db_connector, community_name):
	errors = []

	if "@" not in form["email"][0]:
		errors.append("Please enter a valid email.")
		return errors
	
	try:
		if form["is_admin"][0]:
			valid = db_connector.check_admin_password(form["email"][0], form["password"][0])
		else:
			community = db_connector.get_community(name = community_name)
			valid = community.check_user_password(form["email"][0], form["password"][0])
	except db.DatabaseException as e:
		errors.append(str(e))
	else:
		if not valid:
			errors.append("Password incorrect.")
	return errors
		

def validate_register_form(form, db_connector):
	errors = []
	
	is_admin = "admin_submit" in form
	if is_admin:
		prefix = "admin_"
	else:
		prefix = "user_"
	
	if form[prefix + "email_confirm"][0] != form[prefix + "email"][0]:
		errors.append("Emails must match.")
	if form[prefix + "password_confirm"][0] != form[prefix + "password"][0]:
		errors.append("Passwords must much.")
	if "@" not in form[prefix + "email"][0]:
		errors.append("Please enter a valid email.")
	
	if errors:
		return errors
	
	try:
		if is_admin:
			db_connector.add_community(
				name=form["community_name"][0],
				admin_email=form["admin_email"][0],
				admin_password=form["admin_password"][0],
				invite_code=form["referral"][0]
			)
		else:
			community = db_connector.get_community(invite_code = form["invite_code"][0])
			community.add_user(
				name=f"{form['first_name'][0]} {form['last_name'][0]}",
				email=form["user_email"][0],
				password=form["user_password"][0],
				address=form["address"][0],
				phone_number=form["phone_number"][0]
			)
	except db.DatabaseException as e:
		errors.append(str(e))
	return errors