import functools
from webshopper.communicator import Communicator
from webshopper.auth import (login_required, token_required)

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


bp = Blueprint('settings', __name__)


@bp.route('/location')
@login_required
@token_required
def store_settings():

    # Ask user to enter in their area code
    # Have the client submit a request to our API endpoint that
    # in turn makes a request to the Kroger API.

    if request.method == 'GET':
        return render_template('store_settings.html')

    # if request.method == 'POST':
    #     # User has submitted their ZIP code
    #
    #     # Submit API call through Communicator methods
    #     # Communicator.search_stores(request.ZipCode)  # Communicator does the messing with the database stuff.
    #     zip_code: str = request.form['ZipBox']
    #     print(f'This is the zip code: {zip_code}')
    #     ret = Communicator.search_locations(zip_code)
    #     stores: dict = ret[1]
    #     results: dict = stores['results']
    #     data: list = results['data']  # a list of dictionaries, each representing a store
    #     for element in data:
    #         address: str = element['address']
    #         chain: str = element['chain']
    #         if chain not in ('SHELL COMPANY', 'JEWELRY'):
    #             print(f'{chain}: {address}')
    #
    #     return f'Here is the list of nearby stores: {stores}'


@bp.route('/products', methods=('GET', 'POST'))
@login_required
@token_required
def products():

    # Ask user to enter in their area code
    # Have the client submit a request to our API endpoint that
    # in turn makes a request to the Kroger API.

    if request.method == 'GET':
        ret = Communicator.search_product('beef')
        return f'{ret}'



