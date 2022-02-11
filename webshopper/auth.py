import functools
from webshopper.communicator import Communicator
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from webshopper.db import (get_db, update_tokens)



bp = Blueprint('auth', __name__)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            user = db.execute(
                    """ SELECT *
                        FROM user
                        WHERE 
                            username = ?
                    """,
                    (username,)
                ).fetchone()
            if user is None:
                error = "Invalid username"
                flash(error)
            elif not check_password_hash(user['password_hash'], password):
                error = "Incorrect password"
            else:
                # Successful login
                session.clear()
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['location_id'] = user['location_id']
                return redirect(url_for('home.homepage'))

        flash(error)
        return render_template('auth/login.html')
        # return redirect(url_for('homehmepagedict


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    if request.method == 'POST':
        # Need to check the username against the database
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"

        if error is None:
            try:
                db.execute(
                    """ INSERT INTO user (username, password_hash)
                        VALUES (?, ?) 
                    """,
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"Username already taken"
            else:
                return redirect(url_for("auth.login"))

        flash(error)

        return render_template('auth/register.html')


@bp.route('/get_authcode')
def get_authcode():
    """ Called by the token_required decorator
        in the absence of valid API tokens
    """
    print('Redirect to Kroger auth')
    target_url: str = Communicator.build_auth_url()
    return redirect(target_url)


@bp.route('/get_tokens')
def trade_authcode():
    """ Kroger redirects here with an auth code after user authorizes use of our app.
        Turn the given auth code into
    """
    auth_code: str = request.args.get('code')
    # Utilize Communicator now to get the tokens.
    ret = Communicator.tokens_from_auth(auth_code)
    if ret[0] != 0:
        return f'tokens from auth error: {ret[1]}'
    token_dict: dict = ret[1]
    user_id = session.get('user_id')
    print(f"User id is {user_id}")
    ret = update_tokens(token_dict['access_token'],
                        token_dict['access_timestamp'],
                        token_dict['refresh_token'],
                        token_dict['refresh_timestamp'],
                        session.get('user_id'))
    if ret[0] != 0:
        return f'error updating tokens in db: {ret[1]}'

    return redirect(url_for('home.homepage'))


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


#
#
# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error ((= None
#
#         if not username:
#             error = 'Username is required'
#         elif not password:
#             error = 'Password is required'
#
#         if error is None:
#             try:
#                 db.execute(
#                     """INSERT INTO user (username, password)
#                         VALUES (?, ?)
#                     """,
#                     (username, generate_password_hash(password)),
#                 )o
#                 db.commit()
#             except db.IntegrityError:
#                 error = f"User {username} is already registered."
#             else:
#                 return redirect(url_for("auth.login"))
#
#         flash(error)
#
#     return render_template('auth/register.html')
#
#
# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None
#         user = db.execute(
#             'SELECT * FROM user WHERE username = ?', (username,)
#         ).fetchone()
#
#         if user is None:
#             error = 'Incorrect username.'
#         elif not check_password_hash(user['password'], password):
#             error = 'Incorrect password'
#
#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('index'))
#
#         flash(error)
#
#     return render_template('auth/login.html')
#
#
# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')
#
#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()
#
#
# @bp.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))
#
#
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


def token_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        ret = Communicator.token_check()
        return_code = ret[0]
        if return_code == -1:
            # DB or request error to Kroger API
            return render_template(f'{ret}')
        if return_code == -2:
            print('No valid tokens')
            return redirect(url_for('auth.get_authcode'))
        return view(**kwargs)

    return wrapped_view