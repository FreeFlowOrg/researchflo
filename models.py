from flask import Flask
from flask_mongoalchemy import MongoAlchemy

app = Flask(__name__)

app.config['MONGOALCHEMY_DATABASE'] = 'saiop'
app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb://admin:freeflow@ds135760.mlab.com:35760/saiop'

db = MongoAlchemy(app)

class User(db.Document):
    name = db.StringField()
    email = db.StringField()
    password = db.StringField()
    type = db.StringField()

class Journal(db.Document):
    title = db.StringField()
    user_email = db.StringField()
    domain = db.StringField()
    status = db.StringField()
    filename = db.StringField()
    date = db.DateTimeField()

class Comments(db.Document):
    user = db.StringField()
    commenter = db.StringField()
    title = db.StringField()
    desc = db.StringField()
