import functools
from webshopper.communicator import Communicator
from webshopper.auth import (login_required, token_required)

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,
    jsonify, Response
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


@bp.route('/location/get')
def get_locations():
    """ API endpoint
        Retrieves locations based on the submitted zip code.
        Zip code submitted as a query parameter
        @TODO input validation on the zipcode string

    """
    user_id: int = session.get("user_id")
    if user_id is None:
        return Response("{'error': 'no user id'}", status=403, mimetype="application/json")
    # Getting zip code
    zipcode: str = request.args.get('zipcode')
    if zipcode is None:
        return Response("{'error': 'no zipcode provided'}", status=400, mimetype="application/json")

    # Sending zip code to Kroger for store locations
    ret = Communicator.search_locations(zipcode)
    if ret[0] != 0:  # Error returned from Kroger
        return Response(ret[1], status=400, mimetype="application/json")
    # Got our results list.. Now what?
    stores: dict = ret[1]['results']['data']  # list of dicts, each representing a store
    results: list = []
    for element in stores:
        location_id: str = element['locationId']
        address: str = element['address']
        chain: str = element['chain']
        if chain not in ('SHELL COMPANY', 'JEWELRY'):
            tmp: dict = {
                'locationId': location_id,
                'address': address,
                'chain': chain
            }
            results.append(tmp)
    return jsonify(results=results)

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



