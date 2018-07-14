# -*- coding: utf-8 -*-

from model import db

def validate_form(form, operation, db_connector):
	errors = []

	if operation == "login":
		pass
		
	elif operation == "register":
		if form["email_confirm"][0] != form["email"][0]:
			errors.append("Emails must match.")
		if form["password_confirm"][0] != form["password"][0]:
			errors.append("Passwords must much.")
		if "@" not in form["email"][0]:
			errors.append("Please enter a valid email.")
		if errors:
			return errors
		
		try:
			community = db_connector.get_community(form["invite_code"])
			community.add_user(
				name=f"{form['first_name'][0]} {form['last_name'][0]}",
				email=form["email"][0],
				password=form["password"][0],
				address=form["address"][0],
				phone_number=form["phone_number"][0]
			)
		except db.DatabaseException as e:
			errors.append(e)
	else:
		if form["email_confirm"][0] != form["email"][0]:
			errors.append("Emails must match.")
		if form["password_confirm"][0] != form["password"][0]:
			errors.append("Passwords must much.")
		if "@" not in form["email"][0]:
			errors.append("Please enter a valid email.")
		if form["community_name"][0] in db_connector.list_communities():
			errors.append("This community name is already in use.")
		
		if errors:
			return errors
		
		try:
			db_connector.add_community(
				name=form["community_name"][0],
				admin_email=form["email"][0],
				admin_password=form["password"][0],
				invite_code=form["referral"][0],
			)
		except db.DatabaseException as e:
			errors.append(e)
	return errors