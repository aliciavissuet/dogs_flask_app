import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flask2.auth import login_required
from flask2.db import get_db

bp = Blueprint('dogs', __name__, url_prefix='/')

@bp.route('/')
def index():
    db = get_db()
    dogs = db.execute(
        'SELECT d.id, d.dogname, d.breed, d.color, d.dog_owner_id, d.photo_url, d_o.created, d_o.username'
        ' FROM dog d JOIN dog_owner d_o ON d.dog_owner_id = d_o.id'
        ' ORDER BY d_o.created DESC'
    ).fetchall()
    print(dogs)
    return render_template('index.html', dogs=dogs)

@bp.route('/create', methods=['POST'])
# @login_required
def create():
    db = get_db()
    dogname = request.form['dogname']
    breed = request.form['breed']
    color = request.form['color']
    photo_url = request.form['photo_url']
    dog_owner_id = session['user_id']
    error = None
    if not dogname or not breed or not color:
        error = 'Fill in all fields please'

    if error is not None:
            flash(error)
    else:
        db.execute(
        'INSERT into dog (dogname, breed, color, photo_url, dog_owner_id)'
        'VALUES (?,?,?, ?, ?)',
        (dogname, breed, color, photo_url, dog_owner_id)
        )
        db.commit()
        
        return redirect(url_for('index'))
    

@bp.route('/update/<dogname>', methods=['GET', 'POST'])
def update(dogname=None):
    print('here')
    print(dogname)
    
    if request.method == 'POST':
        db = get_db()
        old_dogname = request.form['old_dog_name']
        dogname = request.form['dogname']
        color = request.form['color']
        breed = request.form['breed']
        photo_url = request.form['photo_url']
        db.execute(
          'UPDATE dog set dogname=?, color=?, breed=?, photo_url = ? WHERE dogname = ?',
          (dogname, color, breed, photo_url, old_dogname)
        )
        db.commit()
        
        return redirect(url_for('index'))
    else:
        db = get_db()
        dog = db.execute(
            'SELECT * FROM dog WHERE dogname = ?', (dogname, )
        ).fetchone()
        return render_template('update.html', dog=dog)

@bp.route('/delete/<dogname>', methods=['POST'])
def delete(dogname):
    db = get_db()
    db.execute(
        'DELETE FROM dog WHERE dogname = ?', (dogname,)
    )
    db.commit()
    return redirect(url_for('index'))
