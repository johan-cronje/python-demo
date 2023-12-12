"""Johan Cronje 09/23/2022

Package level definitions
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI') or 'sqlite:///data.db'
app.config['SECRET_KEY'] = getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db = SQLAlchemy(app)

from application import routes