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
