# python-demo

## OVERVIEW

This is a simple implementation of a quote REST API for a fictional insurance company, using the following:

* Python 3.8.11
* Flask web framework for URL routing
* SQLAlchemy with a SQLite backend for data persistence
* Marshmallow to validate input data and (de)serialize data

The **Quote** entity allows for new quotes to be added, existing attributes to be updated and pricing to be obtained by calling the applicable Quote API endpoint.

The **State** entity allows for new states to be added or pricing variables to be updated calling the applicable State API endpoints.

Adding a new pricing variable, e.g. hurricane coverage, would involve:
* adding a `hurricane_coverage` attribute to the Quote model & schema scripts
* adding a `hurricane_coverage_percentage` attribute to the State model & schema scripts
* Updating the pricing calculation `get_price` in the routes script

## INSTALLATION

Follow these manual steps to set up the virtual environment:
```bash
# create the virtual environment
python3 -m venv env
# activate the virtual environment
source env/bin/activate
# upgrade pip
python3 -m pip install --upgrade pip
# installed all required packages
pip3 install -r requirements.txt
```

At this point the environment should be ready to proceed
```bash
# run the unit tests
pytest -W ignore -s

# start the API
python3 app.py

# when done deactivate the virtual environment
deactivate
```

## TESTING

A basic unit test exists in `tests/test_app.py`. The test setup preloads data for 3 states (CA,TX,NY). Data is persisted to a temporary SQLite instance, so main database is not touched.

The following test are performed (by no means exhaustive):
* a total of 3 states can be retrieved via the API
* confirms whether a quote can be created via the API
* confirms that the pricing calculation matches expected results for the 4 provided quote examples

The test can be executed as follows:
```bash
pytest -W ignore -s
```

I have provided a utility script `preload_data.py` which will create the 3 state configurations and optionally the 4 quotes for the test cases. The code to create the quotes will have to be uncommented.

Alternatively the **HTTPie** commands listed below can be used to achieve the same result when starting with an empty database:
```bash
# create the 3 state configurations
http -b POST :5000/api/states abbreviation="CA" name="California" flood_insurance_percentage=2 monthly_tax_percentage=1
http -b POST :5000/api/states abbreviation="TX" name="Texas" flood_insurance_percentage=50 monthly_tax_percentage=0.5
http -b POST :5000/api/states abbreviation="NY" name="New York" flood_insurance_percentage=10 monthly_tax_percentage=2

# list all the states
http -b :5000/api/states

# list a the configuration for California
http -b :5000/api/states/CA

# update the flood insurance % for California
http -b PATCH :5000/api/states/CA flood_insurance_percentage=1.5

# create the 4 quote test cases
http -b POST :5000/api/quotes name="Quote 1" coverage_type="basic" state_abbrev="CA" pets:=true flood_coverage:=true
http -b POST :5000/api/quotes name="Quote 2" coverage_type="premium" state_abbrev="CA" pets:=true flood_coverage:=true
http -b POST :5000/api/quotes name="Quote 3" coverage_type="premium" state_abbrev="NY" pets:=true flood_coverage:=false
http -b POST :5000/api/quotes name="Quote 4" coverage_type="basic" state_abbrev="TX" pets:=false flood_coverage:=true

# list all the quotes
http -b :5000/api/quotes

# list the first quote (id=1)
http -b :5000/api/quotes/1

# update the pets value for Quote 1 (id=1)
http -b PATCH :5000/api/quotes/1 pets:=false

# obtain pricing for quote 1
http -b :5000/api/quotes/1/price

# shortcut to display pricing for all 4 quotes
for id in {1..4}; do http -b :5000/api/quotes/$id/price; done
```

`curl` can also be used, e.g.
```bash
curl \
  -X POST \
  -H "Content-Type: application/json" \
  http://localhost:5000/api/states \
  -d '{"abbreviation":"CA","name":"California","flood_insurance_percentage":2,"monthly_tax_percentage":1}'
```

## API DOCUMENTATION

API access is over HTTP, accessed from http://localhost:5000. Data is sent and received as JSON.

### States

#### Path parameters
> **state_abbreviation**  string(2) Standard USPS state abbreviation, e.g. CA, TX, NY

#### Body parameters

> **id**  integer  Automatically created read-only identifier
> **abbreviation**  string(2)  Standard USPS state abbreviation, e.g. CA, TX, NY
> **name**  string  Full name of state, e.g. California
> **flood_insurance_percentage**  decimal(1)
> **monthly_tax_percentage**  decimal(1)
> **created**  datetime  Automatically created read-only timestamp when object is created

#### HTTP response status codes

> **200**  Success
> **400**  No input data provided
> **400**  State with {id} could not be found
> **422**  Data validation error

#### **GET**  /api/states
> Get a list of all State objects
#### **POST**  /api/states
> Add a new State object
#### **GET**  /api/states/{state_abbreviation}
> Get a specific State object
#### **PATCH**  /api/states/{state_abbreviation}
> Update one or more attributes on an existing State object

---
### Quotes

#### Path parameters
> **quote_id**  integer The id for a quote

#### Body parameters

> **id**  integer  Automatically created read-only identifier
> **first_name**  string  First name of policy holder
> **last_name**  string  Last name of policy holder
> **name**  string  Full name of policyholder. If supplied, first_name and last_name will be automatically populated.
> **coverage_type**  string Type of coverage required by the buyer, one of (basic,premium)
> **state_abbrev**  string  The state of the buyer - standard USPS state abbreviation, e.g. CA, TX, NY
> **state**  <State>  State object
> **pets**  boolean  Does the buyer have a pet?
> **flood_coverage**  boolean  Does the buyer want flood coverage?
> **created**  datetime  Automatically created read-only timestamp when object is created

#### HTTP response status codes

> **200**  Success
> **400**  No input data provided
> **400**  Quote with {id} could not be found
> **422**  Data validation error

#### **GET**  /api/quotes
> Get a list of all Quote objects
#### **POST**  /api/quotes
> Create a new Quote object
#### **GET**  /api/quotes/{quote_id}
> Get a specific Quote object
#### **PATCH**  /api/quotes/{quote_id}
> Update one or more atributes on an existing Quote object

---
### Price

#### Path parameters
> **quote_id**  integer The id for a quote

#### HTTP response status codes

> **200**  Success
> **400**  Quote with {id} could not be found
> **422**  Internal validation error

#### **GET** /api/quotes/{quote_id}/price
> Get pricing for a specific Quote object

## CODE STRUCTURE

* `app.py` - API launch point
* `preload_data.py` - Script to load database with states (and 4 quotes optionally)
* `requirements.txt` - Required packages for application
  * **application**
    * `__init__.py`
    * `data.db` - SQLite database. Will be created on first execution
    * `models.py` - SQLAlchemy model definition
    * `routes.py` - Flask route definition
    * `schema.py` - Marshmallow schema definition
  * **tests**
    * `__init__.py`
    * `test_app.py` - Basic unit tests for API. Creates an in memory SQLite instance.
