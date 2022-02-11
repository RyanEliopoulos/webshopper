from typing import Tuple
import os
import requests
import sqlite3
import webshopper.db as db
import datetime
import urllib.parse

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

"""


"""


class Communicator:
    """
        Interface for Kroger API
    """
    client_id = os.getenv('kroger_app_client_id')
    client_secret = os.getenv('kroger_app_client_secret')
    redirect_uri = os.getenv('kroger_app_redirect_uri')
    api_base = "https://api.kroger.com/v1/"
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint
    token_timeout: float = 1500  # Seconds after which we are considering the token expired. Actually 1800.
    refresh_timeout: float = 60 * 60 * 24 * 7 * 4 * 5  # ~Seconds in a 5 month period (tokens last 6 months)

    @staticmethod
    def _check_ctoken(timestamp: int) -> bool:
        """ Evaluates given timestamp freshness based on client token expiry rules """
        now: datetime.datetime = datetime.datetime.now()
        then: datetime.datetime = datetime.datetime.fromtimestamp(timestamp)
        print(now)
        print(then)
        if (now - then).total_seconds() >= Communicator.token_timeout:
            val = (now - then).seconds
            print(f'nts: {val}')
            print('Token expired')
            return False
        print('Token good')
        return True

    @staticmethod
    def _check_rtoken(timestamp: int):
        """ Evaluates given timestamp freshness based on refresh token expiry rules """
        now: datetime.datetime = datetime.datetime.now()
        then: datetime.datetime = datetime.datetime.fromtimestamp(timestamp)
        if (now - then).total_seconds() >= Communicator.refresh_timeout:
            return False
        return True

    @staticmethod
    def write_tokens(user_id: int, access_token: str, access_timestamp):
        ...

    @staticmethod
    def build_auth_url() -> str:
        """ Builds Kroger user authorization URL.
        """
        # Preparing URl
        params: dict = {
            'scope': 'profile.compact cart.basic:write product.compact'
            , 'client_id': Communicator.client_id
            , 'redirect_uri': Communicator.redirect_uri
            , 'response_type': 'code'
            , 'state': 'oftheunion'
        }
        encoded_params = urllib.parse.urlencode(params)
        target_url = Communicator.api_base + Communicator.api_authorize + '?' + encoded_params
        return target_url

    @staticmethod
    def tokens_from_auth(auth_code: str) -> Tuple[int, dict]:
        """ Exchanges the auth code for customer tokens
        """
        headers: dict = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data: dict = {
            'grant_type': 'authorization_code'
            , 'redirect_uri': Communicator.redirect_uri
            , 'scope': 'profile.compact cart.basic:write product.compact'
            , 'code': auth_code
        }
        target_url: str = Communicator.api_base + Communicator.api_token
        req = requests.post(target_url, headers=headers, data=data,
                            auth=(Communicator.client_id, Communicator.client_secret))
        if req.status_code != 200:
            # Logger.Logger.log_error('Error retrieving tokens with auth code --- ' + req.text)
            print('error retrieving tokens with authorization_code')
            print(req.text)
            return -1, {'error_message': f'{req.text}'}
        req = req.json()
        access_timestamp: float = datetime.datetime.now().timestamp()
        token_dict = {
            'access_token': req['access_token'],
            'access_timestamp': access_timestamp,
            'refresh_token': req['refresh_token'],
            'refresh_timestamp': access_timestamp
        }
        print("..Tokens retrieved")
        return 0, token_dict

    @staticmethod
    def _client_token() -> Tuple[int, dict]:
        """
                Responsible for supplying caller with valid client token.
                Checks for valid token in the database first. Pulls new
                token from Kroger and updates db before returning otherwise.
            """
        print('in client token')
        conn: sqlite3.Connection = db.get_db()
        cursor: sqlite3.Cursor = conn.cursor()
        ret: Tuple = db.get_clitoken(cursor)
        if ret[0] != 0:
            return ret
        # Successful pull from db. Checking validity of timestamp
        timestamp: int = ret[1]['timestamp']
        if Communicator._check_ctoken(timestamp):
            return 0, ret[1]
        # Expired client token. Requesting new one
        # Staging request data
        id: str = os.getenv('kroger_app_client_id')
        secret: str = os.getenv('kroger_app_client_secret')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'scope': 'product.compact'
        }
        target_url: str = Communicator.api_base + Communicator.api_token
        req: requests.Response = requests.post(target_url, headers=headers, data=data,
                                               auth=(id, secret))
        if req.status_code != 200:
            return -1, {'error_message': f'Problem with client credential request: {req.text}'}
        # Call successful. Updating database
        response: dict = req.json()
        unix_now: float = datetime.datetime.now().timestamp()
        token: str = response['access_token']
        print('Updating db with credentials')
        ret = db.set_ctoken(cursor, token, int(unix_now))
        if ret[0] != 0:  # error updating database
            return ret
        print('commit db')
        print(conn.commit())
        return 0, {'client_token': token}

    @staticmethod
    def _refresh_tokens(ref_token: str) -> Tuple[int, dict]:
        """ Pulls fresh access and refresh tokens from Kroger
            using the given token. Does not return anything if successful.
        """
        # Prepping request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token'
            , 'refresh_token': ref_token
        }
        target_url: str = Communicator.api_base + Communicator.api_token
        # Evaluating response
        req = requests.post(target_url, headers=headers, data=data,
                            auth=(Communicator.client_id, Communicator.client_secret))
        if req.status_code != 200:
            # Logger.Logger.log_error('Failed to refresh tokens in token_refresh()' + req.text)
            return -1, {'error_message': f'request error: {req.text}'}
        req = req.json()
        # Updating database with new tokens
        access_timestamp: float = datetime.datetime.now().timestamp()
        access_token = req['access_token']
        refresh_token = req['refresh_token']
        user_id: int = session.get('user_id')
        ret = db.update_tokens(access_token, access_timestamp, refresh_token
                               , access_timestamp, user_id)
        if ret[0] != 0:
            return ret
        return 0, {}

    @staticmethod
    def _get_token() -> Tuple[int, dict]:
        """  Success: 0, token_dict
             db error: -1, error_dict

             Token is not check for freshness as all endpoints are wrapped in a check.
        """
        conn: sqlite3.Connection = db.get_db()
        cursor: sqlite3.Cursor = conn.cursor()
        ret: Tuple = db.get_custokens(cursor, session.get('user_id'))
        if ret[0] != 0:
            return ret
        token_dict: dict = ret[1]
        return 0, {'access_token': token_dict['access_token']}

    @staticmethod
    def token_check() -> Tuple[int, dict]:
        """
            Deals with customer tokens

            Return code 0 if there is valid access token to use.
            If the access token is expired but there is a valid refresh token,
            it will retrieve a new pair of tokens from Kroger before returning 0.

            If neither token is valid, returns false
        """
        conn: sqlite3.Connection = db.get_db()
        cursor: sqlite3.Cursor = conn.cursor()
        ret: Tuple = db.get_custokens(cursor, session.get('user_id'))
        if ret[0] != 0:
            return ret
        tokens: dict = ret[1]
        print(f"Token dict: {tokens}")
        if Communicator._check_ctoken(tokens['access_timestamp']):
            print("In token check. Returning 0 ret ")
            return 0, {'success_message': 'valid access token'}
        if Communicator._check_rtoken(tokens['refresh_timestamp']):
            print('refreshing tokens')
            return Communicator._refresh_tokens(tokens['refresh_token'])
        # No valid tokens
        return -2, {'error_message': 'No valid tokens'}

    @staticmethod
    def search_locations(zipcode: str) -> Tuple[int, dict]:
        # Token freshness is enforced by endpoint wrapper upon request.
        # No need to check here
        ret = Communicator._get_token()
        if ret[0] != 0:
            return ret
        # Building request
        access_token: str = ret[1]['access_token']
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        data = {
            'filter.zipCode.near': zipcode
        }
        print(f'lcoation searching use tokne: {access_token}')
        target_url: str = Communicator.api_base + 'locations'
        print(f'target_url: {target_url}')
        req: requests.Response = requests.get(target_url, headers=headers, data=data)
        if req.status_code != 200:
            print(f'Request status code: {req.status_code}')
            return -1, {'error_message': req.text}
        rez = req.json()
        print(req.json())
        # ASSUMING WE NEED THE CUSTOMER TOKEN BEFORE WE CAN SEARCH LOCATIONS
        return 0, {'results': rez}

    @staticmethod
    def search_product(search_term: str) -> Tuple[int, dict]:
        if len(search_term) < 4:
            return -1, {'error_message': 'String must be at least 3 characters'}
        ret = Communicator._get_token()
        if ret[0] != 0:
            return ret
        access_token: str = ret[1]['access_token']
        headers: dict = {
            'Accept': 'application/json'
            , 'Authorization': f'Bearer {access_token}'
        }

        params = {
            'filter.term': search_term,
            'filter.locationId': '70100140',
            'filter.fulfillment': 'csp',
            'filter.start': '1',
            'filter.limit': '5',
        }
        # encoded_params = urllib.parse.urlencode(params)
        # target_url: str = f'{self.api_base}products/{encoded_params}'
        target_url: str = f'{Communicator.api_base}products'

        req = requests.get(target_url, headers=headers, params=params)
        if req.status_code != 200:
            # Logger.Logger.log_error(f'Error searching for product: {req.text}')
            print(f'Status code: {req.status_code}')
            print(f'Status code: {req.text}')
            exit(1)

        return 0, req.json()