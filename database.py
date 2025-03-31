import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext import compiler
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()

#locationrel table
locationrel = db.Table(
    'locationrel',
    db.Column('tool_id', db.Integer, db.ForeignKey('tool.id', ondelete="CASCADE")),
    db.Column('loc_id', db.Integer, db.ForeignKey('location.id', ondelete="CASCADE"))
)

#Tool class
class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    type = db.Column(db.String(120))
    location = db.relationship('Location', secondary = locationrel, primaryjoin=id == locationrel.c.tool_id,
        secondaryjoin=id == locationrel.c.loc_id, backref = 'locationrel', lazy = 'dynamic')

#Location class
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    tools = db.relationship('Tools', secondary = locationrel, primaryjoin=id == locationrel.c.loc_id,
        secondaryjoin=id == locationrel.c.tool_id, backref = 'locationrel', lazy = 'dynamic')
    