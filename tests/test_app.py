"""Johan Cronje 09/23/2022

Tests for the API app. Uses a temporary database.
"""

from application import app, db
from application.models import State, Quote
from flask import url_for, json
from flask_testing import TestCase
from application.schema import StateSchema, QuoteSchema, PriceSchema
from marshmallow import ValidationError
from pprint import pprint

'''
Base test class that performs setup & teardown for every test
'''
class TestBase(TestCase):
    def create_app(self):
        # Testing configuration - use sqlite without a persistent database
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"
        app.config['DEBUG'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True

        return app
    
    def setUp(self):
        # will be called before every test
        db.create_all()

        # Add initial three states for every test
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
                assert False, f"'test_add_states' raised an exception {err.messages}"

            response = self.client.post(
                url_for('new_state'),
                data=json.dumps(json_data),
                content_type='application/json',
                follow_redirects=True
            )

    def tearDown(self):
        # will be called after every test
        db.session.remove()
        db.drop_all()

'''
Test that the 3 states are loaded in the db
'''
class TestGetStates(TestBase):
    def test_get_states(self):
        response = self.client.get(url_for('get_states'))
        state_json = json.loads(response.data)
        self.assertEqual(len(state_json['states']), 3)

'''
Test that a quote can be created
'''
class TestAddQuote(TestBase):
    def test_add_quote(self):
        json_data = {'name': "Quote 1", 'coverage_type': "basic", 'state_abbrev': "CA", 'pets': True, 'flood_coverage': True}

        # Validate and deserialize input
        try:
            data = QuoteSchema().load(json_data)
        except ValidationError as err:
            assert False, f"'test_add_quote' raised an exception {err.messages}"

        response = self.client.post(
            url_for('new_quote'),
            data=json.dumps(json_data),
            content_type='application/json',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

        quote_json = json.loads(response.data)
        self.assertEqual(quote_json['quote']['coverage_type'], 'basic')
        self.assertEqual(quote_json['quote']['state']['abbreviation'], 'CA')
        self.assertEqual(quote_json['quote']['flood_coverage'], True)
        self.assertEqual(quote_json['quote']['pets'], True)


'''
Test that the quote pricing is correct
'''
class TestQuotePricing(TestBase):
    def test_quote_all_pricing(self):
        quotes_data = {
            '1': {'name': "Quote 1", 'coverage_type': "basic",   'state_abbrev': "CA", 'pets': True,  'flood_coverage': True},
            '2': {'name': "Quote 2", 'coverage_type': "premium", 'state_abbrev': "CA", 'pets': True,  'flood_coverage': True},
            '3': {'name': "Quote 3", 'coverage_type': "premium", 'state_abbrev': "NY", 'pets': True,  'flood_coverage': False},
            '4': {'name': "Quote 4", 'coverage_type': "basic",   'state_abbrev': "TX", 'pets': False, 'flood_coverage': True}
        }
        price_validations = {
            '1': {'monthly_subtotal': 40.8,  'monthly_taxes': 0.41, 'monthly_total': 41.21},
            '2': {'monthly_subtotal': 61.20, 'monthly_taxes': 0.61, 'monthly_total': 61.81},
            '3': {'monthly_subtotal': 60,    'monthly_taxes': 1.20, 'monthly_total': 61.20},
            '4': {'monthly_subtotal': 30,    'monthly_taxes': 0.15, 'monthly_total': 30.15}
        }

        for seq, json_data in quotes_data.items():

            # Validate and deserialize input
            try:
                data = QuoteSchema().load(json_data)
            except ValidationError as err:
                assert False, f"'test_quote_all_pricing' ({seq})raised an exception {err.messages}"

            # call the quote endpoint to create a new quote
            response = self.client.post(
                url_for('new_quote'),
                data=json.dumps(json_data),
                content_type='application/json',
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)

            # get id of quote we just added
            quote_json = json.loads(response.data)
            quote_id = quote_json['quote']['id']
            self.assertEqual(quote_id, int(seq))

            # call the pricing endpoint for the created quote
            response = self.client.get(
                f'/api/quotes/{quote_id}/price',
                content_type='application/json',
                follow_redirects=True
            )
            price_json = json.loads(response.data)

            # finally validate the pricing calculations
            price_validation = price_validations[seq]
            self.assertAlmostEqual(float(price_json['price']['monthly_subtotal']), price_validation['monthly_subtotal'], places=2)
            self.assertAlmostEqual(float(price_json['price']['monthly_taxes']), price_validation['monthly_taxes'], places=2)
            self.assertAlmostEqual(float(price_json['price']['monthly_total']), price_validation['monthly_total'], places=2)
