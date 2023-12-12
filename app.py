#!/usr/bin/env python3

"""Johan Cronje 09/23/2022

This script starts up a Flask REST API instance on port 5000
"""

from application import app, db

if __name__ == "__main__":
    db.create_all()
    app.run(debug=False, port=5000)