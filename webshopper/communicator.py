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
    redirect_uri = ''
    api_base = "https://api.kroger.com/v1/"
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint
    redirect_uri: str = 'http://localhost:8000'
    token_timeout: float = 1500  # Seconds after which we are considering the token expired. Actually 1800.
    refresh_timeout: float = 60 * 60 * 24 * 7 * 4 * 5 # ~Seconds in a 5 month period (tokens last 6 months)

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
    def build_auth_url() -> str:
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


    # @staticmethod
    # def authcode_redirect() -> Tuple[int, tuple]:
    #     """
    #         Redirects to Kroger API endpoint. Prompts user to consent to
    #         giving us tokens.
    #     :return:
    #     """
    #     # preparing target URL
    #     client_id = os.getenv('client_id')
    #     redirect_uri = os.getenv('redirect_uri')
    #     params: dict = {
    #         'scope': 'profile.compact cart.basic:write product.compact'
    #         , 'client_id': client_id
    #         , 'redirect_uri': redirect_uri
    #         , 'response_type': 'code'
    #         , 'state': 'oftheunion'
    #     }
    #     encoded_params = urllib.parse.rulencode(params)
    #     target_url: str = Communicator.api_base + Communicator.api_authorize + '?' + encoded_params

    @staticmethod
    def _refresh_tokens(ref_token: str) -> Tuple[int, dict]:
        """ Pulls fresh access and refresh tokens from Kroger
            using the given token
        """
        # @TODO This

    # @staticmethod
    # def _get_token() -> Tuple[int, dict]:
    #     """  Success: 0, token_dict
    #          db error: -1, error_dict
    #          expired tokens: -2, error_dict
    #     """
    #     conn: sqlite3.Connection = db.get_db()
    #     cursor: sqlite3.Cursor = conn.cursor()
    #     ret: Tuple = db.get_custokens(cursor, session.get('user_id'))
    #     if ret[0] != 0:
    #         return ret
    #     # Checking access token freshness
    #     token_dict: dict = ret[1]
    #     if Communicator._check_ctoken(token_dict['access_timestamp']):
    #         return 0, token_dict
    #     # access token expired. Checking refresh token for freshness
    #     if Communicator._check_rtoken(token_dict['refresh_timestamp']):
    #         ### NEED A RETRIEVE TOKENS METHOD CALL HERE
    #         return 0, token_dict
    #     return -2, {'error_message': 'Both tokens expired'}

    @staticmethod
    def token_check() -> Tuple[int, dict]:
        """
            Deals with customer tokens

            Returns true if there is valid access token to use.
            If the access token is expired but there is a valid refresh token,
            it will retrieve a new pair of tokens from Kroger before returning true.

            If neither token is valid, returns false
        """
        conn: sqlite3.Connection = db.get_db()
        cursor: sqlite3.Cursor = conn.cursor()
        ret: Tuple = db.get_custokens(cursor, session.get('user_id'))
        if ret[0] != 0:
            return ret
        tokens: dict = ret[1]
        if Communicator._check_ctoken(tokens['access_timestamp']):
            return 0, {'success_message': 'valid access token'}
        if Communicator._check_rtoken(tokens['refresh_timestamp']):
            # @todo token refresh function
            ...
        # No valid tokens
        return -2, {'error_message': 'No valid tokens'}

    # @staticmethod
    # def search_locations(zipcode: str) -> Tuple[int, dict]:
    #     ###  Seems to require customer token
    #     ### BUILD REQUEST TO ENDPOIN
    #     ### RETURN RESULTS
    #     # Building request
    #     ret = Communicator._client_token()
    #     if ret[0] != 0:
    #         return ret
    #     # client_token: str = ret[1]['client_token']
    #     # headers = {
    #     #     'Accept': 'application/json',
    #     #     'Authorization': f'Bearer {client_token}'
    #     # }
    #     # data = {
    #     #     'filter.zipCode.near': zipcode
    #     # }
    #     # target_url: str = Communicator.api_base + 'locations'
    #     # req: requests.Response = requests.get(target_url, headers=headers, json=data)
    #     # if req.status_code != 200:
    #     #     return -1, {'error_message': req.text}
    #     # print(req.json())
    #
    #
    #     # ASSUMING WE NEED THE CUSTOMER TOKEN BEFORE WE CAN SEARCH LOCATIONS
    #     return 0, {'results': 'rez'}
