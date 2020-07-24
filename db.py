from flask import Flask
from flask_pymongo  import pymongo

CONNECTION_STRING = "mongodb+srv://admin:Password1!@gisdata-test1.3hzb3.mongodb.net/<dbname>?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('GISData-Test1')
user_collection = pymongo.collection.Collection(db, 'GISData-Test1')