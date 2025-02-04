from flask import Flask
from os import environ as env
import os
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.getenv('MONGO_URI')


client = MongoClient(MONGO_URI)

db = client['deepsolv']
main_users =  db['users']
profile = db['profile']


from files import routes
