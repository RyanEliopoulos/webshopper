from typing import Tuple
import os
import requests
import sqlite3
import webshopper.db as db
import datetime

"""


"""


class Communicator:
    """
        Interface for Kroger API
    """
    api_base = "https://api.kroger.com/v1/"
    api_token: str = 'connect/oauth2/token'
    api_authorize: str = 'connect/oauth2/authorize'  # "human" consent w/ redirect endpoint
    redirect_uri: str = 'http://localhost:8000'
    token_timeout: float = 1500  # Seconds after which we are considering the token expired. Actually 1800.

    @staticmethod
    def _check_ctoken(timestamp: int) -> bool:
        """ Evaluates client token timestamp for freshness """
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
    def _client_token() -> Tuple[int, dict]:
            """
                Responsible for supplying caller with valid client token.
                Checks for valid token in the database first. Pulls new
                token from Kroger and updates db before returning otherwise.
            """
            print('in client token')
            conn: sqlite3.Connection = db.get_db()
            cursor: sqlite3.Cursor = conn.cursor()
            ret: Tuple = db.get_ctoken(cursor)
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
    def search_locations(term: str) -> Tuple[int, dict]:
        ### GET CLIENT TOKEN
        ### BUILD REQUEST TO ENDPOIN
        ### RETURN RESULTS
        # Building request
        ret = Communicator._client_token()
        if ret[0] != 0:
            return ret

        client_token: str = ret[1]['client_token']
        return 0, {'results': 'rez'}
