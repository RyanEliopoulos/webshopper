import functools
import sqlite3
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


from webshopper.db import get_db


bp = Blueprint('home', __name__)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        session['user_id'] = None
    else:
        user_row: sqlite3.Row = get_db().execute(
            """ SELECT *
                FROM user
                WHERE id = ?
            """, (user_id,)
        ).fetchone()
        session['user_id'] = user_row['id']


@bp.route('/')
def homepage():
    # Checking if user is logged in
    if session.get('user_id') is None:
        return redirect(url_for('auth.login'))

    # Successful login.
    # Check if the user has selected a location yet
    if session.get('location_id') is None:
        print('location_id is none')
        return redirect(url_for('settings.set_location'))
    # Location id is set
    return render_template('homepage.html')