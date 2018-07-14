
from collections import namedtuple
import datetime

from flask import Flask
from flask_pymongo import PyMongo
import pymongo

class WHOADatabase(PyMongo):
	
	def __init__(self, app):
		super().__init__(app, "mongodb://localhost:27017/whoa")
		self.communities = self.db.communities
	
	def add_community(self, **kwargs):
		for required_field in ("name", "admin_email", "admin_password", "invite_code"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		if self.communities.find_one({"name": kwargs["name"]}):
			raise DatabaseException("Duplicate community name")
		if self.communities.find_one({"admin_email": kwargs["admin_email"]}):
			raise DatabaseException("Duplicate admin email")
		if self.communities.find_one({"invite_code": kwargs["invite_code"]}):
			raise DatabaseException("Duplicate invite code")
		result = self.communities.insert_one(kwargs)
		community_collection = self.db.create_collection(str(result.inserted_id))
		noticeboard_collection = self.db.create_collection(f"{result.inserted_id}_nb")
		return WHOACommunity(community_collection, WHOANoticeboard(noticeboard_collection))
	
	def get_community(self, name = None, invite_code = None):
		if not (name or invite_code):
			raise DatabaseException("Name or invite code required")
		document = None
		if name:
			document = self.communities.find_one({"name": name})
		if not document and invite_code:
			document = self.communities.find_one({"invite_code": invite_code})
		if not document:
			raise DatabaseException("Community not found")
		community_collection = self.db[str(document["_id"])]
		noticeboard_collection = self.db[f"{document['_id']}_nb"]
		return WHOACommunity(community_collection, WHOANoticeboard(noticeboard_collection))
	
	def list_communities(self):
		return self.communities.distinct("name")
	
	def check_admin_password(self, admin_email, admin_password):
		document = self.communities.find_one({"admin_email": admin_email})
		if not document:
			raise DatabaseException("Admin email not found")
		return admin_password == document["admin_password"]


class WHOACommunity:
	
	def __init__(self, collection, noticeboard):
		self.collection = collection
		self.noticeboard = noticeboard
	
	def add_user(self, **kwargs):
		for required_field in ("name", "email", "password", "address", "phone_number"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		if self.collection.find_one({"email": kwargs["email"]}):
			raise DatabaseException("Duplicate email")
		self.collection.insert_one(kwargs)
	
	def check_user_password(self, email, password):
		document = self.collection.find_one({"email": email})
		if not document:
			raise DatabaseException("Email not found")
		return password == document["password"]


Notice = namedtuple("Notice", "poster, content, timestamp, other")

class WHOANoticeboard:
	
	def __init__(self, collection):
		self.collection = collection
	
	def add_notice(self, **kwargs):
		for required_field in ("poster", "content", "timestamp"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		self.collection.insert_one(kwargs)
	
	def list_notices(self):
		documents = self.collection.find(sort = [("timestamp", pymongo.DESCENDING)])
		notices = []
		for notice in documents:
			poster = notice.pop("poster")
			content = notice.pop("content")
			timestamp = notice.pop("timestamp")
			notices.append(Notice(poster = poster, content = content, timestamp = timestamp, other = notice))
		return notices


class DatabaseException(Exception):
	pass


if __name__ == "__main__":
	db = WHOADatabase(Flask(__name__))
	community = db.add_community(name = "HOA1", admin_email = "Bob@bob.com", admin_password = "badpassword", invite_code = "abc")
	community.add_user(name = "Joe", email = "Joe@joe.com", password = "goodpassword", address = "666 Sixth Street. #6", phone_number = "666-666-6666")
	community = db.get_community(invite_code = "abc")
	assert db.check_admin_password("Bob@bob.com", "badpassword")
	assert not db.check_admin_password("Bob@bob.com", "password")
	assert community.check_user_password("Joe@joe.com", "goodpassword")
	assert not community.check_user_password("Joe@joe.com", "password")
	assert db.list_communities() == ["HOA1"]
	community.noticeboard.add_notice(poster = "Joe", content = "Hello", timestamp = datetime.datetime.utcnow())
	community.noticeboard.add_notice(poster = "Joe", content = "Hello v2", timestamp = datetime.datetime.utcnow())
	assert len(community.noticeboard.list_notices()) == 2

