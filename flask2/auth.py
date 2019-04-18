import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flask2.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM dog_owner WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {username} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO dog_owner (username, pw) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM dog_owner WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['pw'], password):
            error = 'Incorrect password.'

        if error is None:
            print('no error')
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        print('error')
        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    print('logout')
    session.clear()
    return redirect(url_for('auth/login.html'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        print('here')
        print(g)
        if g is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
