"""Johan Cronje 09/23/2022

Marshmallow schema definitions to validate & (de)serialize objects
"""

from marshmallow import Schema, fields, validate, pre_load

''' State configuration for policy pricing
'''
class StateSchema(Schema):
    id = fields.Int(dump_only=True)
    abbreviation = fields.Str(required=True)
    name = fields.Str(required=True)
    flood_insurance_percentage = fields.Decimal(1, validate=validate.Range(0, 100), load_default=0)
    monthly_tax_percentage = fields.Decimal(1, validate=validate.Range(0, 100), load_default=0)
    created = fields.DateTime(dump_only=True)

''' Quote information
'''
class QuoteSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    name = fields.Method('full_name', dump_only=True)
    coverage_type = fields.Str(required=True, validate=validate.OneOf(['basic', 'premium']))
    state_abbrev = fields.Str(required=True)
    state = fields.Nested(StateSchema)
    pets = fields.Boolean(load_default=False)
    flood_coverage = fields.Boolean(load_default=False)
    created = fields.DateTime(dump_only=True)

    # combine first & last names into full name
    def full_name(self, quote):
        return f"{quote.first_name} {quote.last_name}"

    # allow policy holder's full name in request body
    @pre_load
    def process_name(self, data, **kwargs):
        name = data.get('name')
        if name:
            # extract first & last names and add to data
            first_name, last_name = name.split(" ")
            data['first_name'] = first_name
            data['last_name'] = last_name
            # remove name element to avoid validation error
            data.pop('name', None)

        return data

''' Deserialization schema for price information
'''
class PriceSchema(Schema):
    monthly_subtotal = fields.Decimal(2)
    monthly_taxes = fields.Decimal(2)
    monthly_total = fields.Decimal(2)
