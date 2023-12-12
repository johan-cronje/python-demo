"""Johan Cronje 09/23/2022
"""

from application import db
from application.models import State, Quote
from application.schema import StateSchema, QuoteSchema, PriceSchema
from marshmallow import ValidationError

db.create_all()

# Add initial three states
preload_states = [
    {'abbreviation': "CA", 'name': "California", 'flood_insurance_percentage': 2,  'monthly_tax_percentage': 1},
    {'abbreviation': "TX", 'name': "Texas",      'flood_insurance_percentage': 50, 'monthly_tax_percentage': 0.5},
    {'abbreviation': "NY", 'name': "New York",   'flood_insurance_percentage': 10, 'monthly_tax_percentage': 2}
]

for json_data in preload_states:

    # Validate and deserialize input
    try:
        data = StateSchema().load(json_data)
    except ValidationError as err:
        print(err.messages)
    
    # Create new state object instance
    state = State(
        abbreviation = data['abbreviation'],
        name = data['name'],
        flood_insurance_percentage = data['flood_insurance_percentage'],
        monthly_tax_percentage = data['monthly_tax_percentage'],
    )
    db.session.add(state)
    db.session.commit()

'''
# Add test quotes
preload_quotes = [
    {'name': "Quote 1", 'coverage_type': "basic",   'state_abbrev': "CA", 'pets': True,  'flood_coverage': True},
    {'name': "Quote 2", 'coverage_type': "premium", 'state_abbrev': "CA", 'pets': True,  'flood_coverage': True},
    {'name': "Quote 3", 'coverage_type': "premium", 'state_abbrev': "NY", 'pets': True,  'flood_coverage': False},
    {'name': "Quote 4", 'coverage_type': "basic",   'state_abbrev': "TX", 'pets': False, 'flood_coverage': True}
]

for json_data in preload_quotes:

    # Validate and deserialize input
    try:
        data = QuoteSchema().load(json_data)
    except ValidationError as err:
        print(err.messages)
    
    # get State object
    quote_state = State.query.filter(State.abbreviation == data['state_abbrev']).one()

    # Create new quote object instance
    state = Quote(
        first_name = data['first_name'],
        last_name = data['last_name'],
        coverage_type = data['coverage_type'],
        state = quote_state,
        pets = data['pets'],
        flood_coverage = data['flood_coverage'],
    )
    db.session.add(state)
    db.session.commit()
'''