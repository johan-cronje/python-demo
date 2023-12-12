"""Johan Cronje 09/23/2022

Flask route definitions for API

- add and modify supported US states
  - GET,POST /api/states
  - GET, PATCH /api/states/<string:sa>
- add and modify insurance quotes
  - GET,POST /api/quotes
  - GET, PATCH /api/quotes/<int:pk>
- obtain pricing for a specific quote
  - GET /api/quotes/<int:pk>/price
"""

from application import app, db
from application.models import State, Quote
from application.schema import StateSchema, QuoteSchema, PriceSchema
from flask import request
from marshmallow import ValidationError
import decimal

## STATES ##


@app.route("/api/states", methods=['GET'])
def get_states():
    states = State.query.all()
    # Serialize the queryset
    result = StateSchema().dump(states, many=True)

    return {'states': result}

@app.route("/api/states", methods=['POST'])
def new_state():
    json_data = request.get_json()
    if not json_data:
        return {'message': "No input data provided"}, 400

    # Validate and deserialize input
    try:
        data = StateSchema().load(json_data)
    except ValidationError as err:
        return err.messages, 422
    
    # Create new state object instance
    state = State(
        abbreviation = data['abbreviation'],
        name = data['name'],
        flood_insurance_percentage = data['flood_insurance_percentage'],
        monthly_tax_percentage = data['monthly_tax_percentage'],
    )
    db.session.add(state)
    db.session.commit()
    result = StateSchema().dump(State.query.get(state.id))

    return {'message': "Created new state", 'state': result}

@app.route("/api/states/<string:sa>", methods=['GET'])
def get_state(sa):
    # get State object
    try:
        state = State.query.filter(State.abbreviation == sa).one()
    except NoResultFound:
        return {'message': f"State '{sa}' could not be found"}, 400
    result = StateSchema().dump(state)

    return {'state': result}

@app.route("/api/states/<string:sa>", methods=['PATCH'])
def modify_state(sa):
    # get State object
    try:
        state = State.query.filter(State.abbreviation == sa).one()
    except NoResultFound:
        return {'message': f"State '{sa}' could not be found"}, 400

    json_data = request.get_json()
    if not json_data:
        return {'message': "No input data provided"}, 400

    # Validate and deserialize input
    try:
        data = StateSchema(partial=True).load(json_data)
    except ValidationError as err:
        return err.messages, 422
    
    # Modify state
    if 'flood_insurance_percentage' in data:
        state.flood_insurance_percentage=data['flood_insurance_percentage']
    if 'monthly_tax_percentage' in data:
        state.monthly_tax_percentage=data['monthly_tax_percentage']

    db.session.commit()
    result = StateSchema().dump(State.query.get(state.id))

    return {'message': "Modified state", 'state': result}


## QUOTES ##


@app.route("/api/quotes", methods=['GET'])
def get_quotes():
    quotes = Quote.query.all()
    # Serialize the queryset
    result = QuoteSchema().dump(quotes, many=True)

    return {'quotes': result}

@app.route("/api/quotes", methods=['POST'])
def new_quote():
    json_data = request.get_json()
    if not json_data:
        return {'message': "No input data provided"}, 400

    # Validate and deserialize input
    try:
        data = QuoteSchema().load(json_data)
    except ValidationError as err:
        return err.messages, 422

    # get State object
    quote_state = State.query.filter(State.abbreviation == data['state_abbrev']).one()
    
    # Create new quote object instance
    quote = Quote(
        first_name = data['first_name'],
        last_name = data['last_name'],
        coverage_type = data['coverage_type'],
        state = quote_state,
        pets = data['pets'],
        flood_coverage = data['flood_coverage'],
    )
    db.session.add(quote)
    db.session.commit()
    result = QuoteSchema().dump(Quote.query.get(quote.id))

    return {'message': "Created new quote", 'quote': result}


@app.route("/api/quotes/<int:pk>", methods=['GET'])
def get_quote(pk):
    # get Quote object
    try:
        state = Quote.query.filter(Quote.id == pk).one()
    except NoResultFound:
        return {'message': f"Quote with id '{sa}' could not be found"}, 400
    result = QuoteSchema().dump(state)

    return {'quote': result}


@app.route("/api/quotes/<int:pk>", methods=['PATCH'])
def modify_quote(pk):
    # get Quote object
    try:
        quote = Quote.query.filter(Quote.id == pk).one()
    except NoResultFound:
        return {'message': f"Quote with id '{sa}' could not be found"}, 400

    json_data = request.get_json()
    if not json_data:
        return {'message': "No input data provided"}, 400

    # Validate and deserialize input
    try:
        data = QuoteSchema(partial=True).load(json_data)
    except ValidationError as err:
        return err.messages, 422
    
    # Modify quote
    if 'first_name' in data:
        quote.first_name = data['first_name']
    if 'last_name' in data:
        quote.last_name = data['last_name']
    if 'coverage_type' in data:
        quote.coverage_type = data['coverage_type']
    if 'state_abbrev' in data:
        # get State object
        quote_state = State.query.filter(State.abbreviation == data['state_abbrev']).one()
        quote.state = quote_state
    if 'pets' in data:
        quote.pets = data['pets']
    if 'flood_coverage' in data:
        quote.flood_coverage = data['flood_coverage']

    db.session.commit()
    result = QuoteSchema().dump(Quote.query.get(quote.id))

    return {'message': "Modified quote", 'quote': result}


## PRICE ##


@app.route("/api/quotes/<int:pk>/price", methods=['GET'])
def get_price(pk):
    # get Quote object
    try:
        quote = Quote.query.filter(Quote.id == pk).one()
    except NoResultFound:
        return {'message': f"Quote with id '{sa}' could not be found"}, 400

    quote_result = QuoteSchema().dump(Quote.query.get(quote.id))

    # initialize dict with Decimal types
    price_data = {
        'monthly_subtotal': decimal.Decimal(0),
        'monthly_taxes': decimal.Decimal(0),
        'monthly_total': decimal.Decimal(0),
    }

    # calculate base cost
    base_cost = 0
    
    # if the user is getting basic coverage, charge $20/month
    if quote.coverage_type == 'basic':
        base_cost = 20
    # if the user is getting premium coverage, charge $40/month
    elif quote.coverage_type == 'premium':
        base_cost = 40

    # if the user has a pet, add $20/month to the cost
    if quote.pets:
        base_cost += 20

    price_data['monthly_subtotal'] = base_cost

    # state specific coverage calculations

    # if the user is buying flood coverage, increase cost by % specified for state
    if quote.flood_coverage:
        flood_price = price_data['monthly_subtotal'] * quote.state.flood_insurance_percentage / 100
        price_data['monthly_subtotal'] += flood_price

    # calculate monthly taxes based on the % specified for the state
    price_data['monthly_taxes'] = price_data['monthly_subtotal'] * quote.state.monthly_tax_percentage / 100

    # calculate total monthly price = base + pet + flood + tax
    price_data['monthly_total'] = price_data['monthly_subtotal'] + price_data['monthly_taxes']
    
    # Validate and deserialize input
    try:
        price = PriceSchema().load(price_data)
    except ValidationError as err:
        return err.messages, 422
    result = PriceSchema().dump(price)

    return {'quote': quote_result, 'price': result}