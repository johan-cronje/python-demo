"""Johan Cronje 09/23/2022

Flask model definitions for API
"""

from application import db 

''' State configuration for policy pricing
'''
class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(2), unique=True)
    name = db.Column(db.String(20))
    flood_insurance_percentage = db.Column(db.DECIMAL(5,1))
    monthly_tax_percentage = db.Column(db.DECIMAL(5,1))
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())


''' Quote information
'''
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    coverage_type = db.Column(db.String(10))
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    state = db.relationship('State', backref=db.backref('quotes', lazy=True))
    pets = db.Column(db.Boolean)
    flood_coverage = db.Column(db.Boolean)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())