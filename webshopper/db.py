import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from typing import Tuple


def _execute_query(db_cursor: sqlite3.Cursor
                   , sql_string: str
                   , parameters: tuple = None) -> Tuple[int, dict]:
    """ Wrapper for cursor.execute. """
    try:
        if parameters is None:
            db_cursor.execute(sql_string)
        else:
            db_cursor.execute(sql_string, parameters)
        return 0, {}

    except sqlite3.Error as e:
        return -1, {'error_message': str(e)}


def get_clitoken(db_cursor: sqlite3.Cursor) -> Tuple[int, dict]:
    """ Retrieves client token and timestamp from database """
    query: str = """    SELECT *
                        FROM tokens 
                 """
    ret = _execute_query(db_cursor, query)
    if ret[0] != 0:  # Error executing query
        return ret
    results: dict = db_cursor.fetchone()
    return_dict = {
        'client_token': results['token'],
        'timestamp': results['timestamp']
    }
    return 0, return_dict


def get_custokens(db_cursor: sqlite3.Cursor, user_id: int) -> Tuple[int, dict]:
    """ Retrieves customer access token, refresh token and their timestamps """
    query: str = """ SELECT  access_token
                            , access_timestamp
                            , refresh_token
                            , refresh_timestamp
                     FROM user
                     WHERE id = ? 
                """
    ret = _execute_query(db_cursor, query, (user_id,))
    if ret[0] != 0:
        return ret
    results: dict = db_cursor.fetchone()
    return_dict = {
        'access_token': results['access_token'],
        'access_timestamp': results['access_timestamp'],
        'refresh_token': results['refresh_token'],
        'refresh_timestamp': results['refresh_timestamp']
    }
    return 0, return_dict


def set_ctoken(db_cursor: sqlite3.Cursor
               , token: str
               , timestamp: int) -> Tuple[int, dict]:
    """ Updates client token db entry """
    query: str = """ UPDATE tokens 
                     SET token = ?, timestamp = ?
                     WHERE tokens.token_type = 'client'
                 """
    ret = _execute_query(db_cursor, query, (token, timestamp))
    return ret


def update_tokens(access_token: str, access_timestamp: float, refresh_token: str
                  , refresh_timestamp: float, user_id: int) -> Tuple[int, dict]:
    print('Updating tokens')
    query = """ UPDATE user
                SET    
                    access_token = ? 
                    , access_timestamp = ?
                    , refresh_token = ?
                    , refresh_timestamp = ?
                WHERE id = ?
            """
    db: sqlite3.Connection = get_db()
    curs = db.cursor()
    ret = _execute_query(curs, query, (access_token,
                                       access_timestamp,
                                       refresh_token,
                                       refresh_timestamp,
                                       user_id))
    if ret[0] == 0:
        db.commit()
    return ret


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """ Unsure what 'e' is doing here"""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """ If the database already exists, drops all tables and resets """
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """ Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)  # instructions followed after requesting concludes
    app.cli.add_command(init_db_command)  # Command line option
