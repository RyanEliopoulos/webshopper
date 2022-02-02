import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from webshopper.db import get_db


bp = Blueprint('home', __name__)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            """ SELECT *
                FROM user
                WHERE id = ?
            """, (user_id,)
        ).fetchone()


@bp.route('/')
def homepage():
    # Checking if user is logged in
    if g.user is None:
        return redirect(url_for('auth.login'))

    return render_template('homepage.html')