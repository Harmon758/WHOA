
from flask import Flask
from flask_pymongo import PyMongo

class WHOADatabase(PyMongo):
	
	def __init__(self, app):
		super().__init__(app, "mongodb://localhost:27017/whoa")
		self.communities = self.db.communities
	
	def add_community(self, **kwargs):
		for required_field in ("name", "admin_email", "admin_password", "invite_code"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		if self.communities.find_one({"admin_email": kwargs["admin_email"]}):
			raise DatabaseException("Duplicate admin email")
		if self.communities.find_one({"invite_code": kwargs["invite_code"]}):
			raise DatabaseException("Duplicate invite code")
		result = self.communities.insert_one(kwargs)
		community_collection = self.db.create_collection(str(result.inserted_id))
		return WHOACommunity(community_collection)
	
	def get_community(self, invite_code):
		document = self.communities.find_one({"invite_code": invite_code})
		if not document:
			raise DatabaseException(f"Invite code not found")
		community_collection = self.db[str(document["_id"])]
		return WHOACommunity(community_collection)


class WHOACommunity:
	
	def __init__(self, collection):
		self.collection = collection
	
	def add_user(self, **kwargs):
		for required_field in ("name", "email", "password", "address", "phone_number"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		if self.collection.find_one({"email": kwargs["email"]}):
			raise DatabaseException("Duplicate email")
		self.collection.insert_one(kwargs)


class DatabaseException(Exception):
	pass


if __name__ == "__main__":
	db = WHOADatabase(Flask(__name__))
	community = db.add_community(name = "HOA1", admin_email = "Bob@bob.com", admin_password = "badpassword", invite_code = "abc")
	community.add_user(name = "Joe", email = "Joe@joe.com", password = "goodpassword", address = "666 Sixth Street. #6", phone_number = "666-666-6666")
	community = db.get_community("abc")

