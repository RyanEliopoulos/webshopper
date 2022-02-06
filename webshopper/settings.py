import functools
from webshopper.communicator import Communicator

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


bp = Blueprint('settings', __name__)


@bp.route('/location', methods=('GET', 'POST'))
def set_location():

    # Ask user to enter in their area code
    # Have the client submit a request to our API endpoint that
    # in turn makes a request to the Kroger API.

    if request.method == 'GET':
        return render_template('select_store.html')

    if request.method == 'POST':
        # User has submitted their ZIP code

        # Submit API call to through Communicator methods
        # Communicator.search_stores(request.ZipCode)  # Communicator does the messing with the database stuff.
        zip_code: str = request.form['ZipBox']
        print(f'This is the zip code: {zip_code}')
        stores = Communicator.search_locations(zip_code)
        print(f"Stores: {stores}")
        return 'Here is the list of nearby stores'