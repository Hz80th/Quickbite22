"""Demo-only identity selection (no passwords; not production authentication)."""
from functools import wraps
from flask import Blueprint, abort, g, redirect, render_template, request, session, url_for
from db import get_db

bp = Blueprint('demo_auth', __name__)


def current_user():
    if not hasattr(g, 'demo_user'):
        user_id = session.get('demo_user_id')
        g.demo_user = (get_db().execute('SELECT * FROM demo_user WHERE id = ?', (user_id,)).fetchone()
                       if user_id is not None else None)
    return g.demo_user


def customer_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for('demo_auth.login', next=request.path))
        if user['role'] != 'customer':
            abort(403)
        return view(*args, **kwargs)
    return wrapper


def staff_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return redirect(url_for('demo_auth.login', next=request.path))
        if user['role'] != 'staff':
            abort(403)
        return view(*args, **kwargs)
    return wrapper


@bp.route('/login', methods=['GET', 'POST'])
def login():
    users = get_db().execute("""SELECT u.id, u.name, u.role, r.name AS restaurant_name
      FROM demo_user u LEFT JOIN restaurant r ON r.id = u.restaurant_id ORDER BY u.id""").fetchall()
    error = None
    if request.method == 'POST':
        raw_id = request.form.get('user_id', '').strip()
        user = get_db().execute('SELECT * FROM demo_user WHERE id = ?', (int(raw_id),)).fetchone() if raw_id.isdigit() else None
        if user is None:
            error = 'Choose a valid demo user ID.'
        else:
            # Switching identity also clears the previous user's cart.
            session.clear()
            session['demo_user_id'] = user['id']
            if user['role'] == 'staff':
                return redirect(url_for('staff.orders'))
            return redirect(url_for('index'))
    return render_template('login.html', users=users, error=error)


@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))
