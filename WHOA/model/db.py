
from flask import Flask
from flask_pymongo import PyMongo

class WHOADatabase(PyMongo):
	
	def __init__(self, app):
		super().__init__(app, "mongodb://localhost:27017/whoa")
		self.communities = self.db.communities
	
	def add_community(self, **kwargs):
		for required_field in ("name", "admin_username", "admin_password"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		result = self.communities.insert_one(kwargs)
		community_collection = self.db.create_collection(str(result.inserted_id))
		return WHOACommunity(community_collection)


class WHOACommunity:
	
	def __init__(self, collection):
		self.collection = collection
	
	def add_user(self, **kwargs):
		for required_field in ("name", "email", "password", "address", "phone_number"):
			if required_field not in kwargs:
				raise DatabaseException(f"Required field: {required_field}")
		self.collection.insert_one(kwargs)


class DatabaseException:
	pass


if __name__ == "__main__":
	db = WHOADatabase(Flask(__name__))
	community = db.add_community(name = "HOA1", admin_username = "Bob", admin_password = "badpassword")
	community.add_user(name = "Joe", email = "Joe@joe.com", password = "goodpassword", address = "666 Sixth Street. #6", phone_number = "666-666-6666")

