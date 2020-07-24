from flask import Flask
from flask_pymongo  import pymongo
import os
import json
dir_path = os.path.dirname(os.path.realpath(__file__))
from app1 import app # Import Flask Object from app1.py

CONNECTION_STRING = app.config["DB_NAME"]
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('GISData-Test1')
user_collection = pymongo.collection.Collection(db, 'GISData-Test1')