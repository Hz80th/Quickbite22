"""PBI-07: Checkout. Uses PBI-05's session['cart'] data contract."""
from flask import Blueprint, abort, redirect, render_template, request, session, url_for
from db import get_db
from pickup import is_valid_slot

bp = Blueprint('checkout', __name__)


def cart_details():
    cart = session.get('cart', {})
    raw_items = cart.get('items', {})
    restaurant_id = cart.get('restaurant_id')
    if not restaurant_id or not isinstance(raw_items, dict) or not raw_items:
        return [], 0, None

    db = get_db()
    items, total = [], 0
    for raw_id, raw_quantity in raw_items.items():
        try:
            item_id, quantity = int(raw_id), int(raw_quantity)
        except (ValueError, TypeError):
            return [], 0, None
        if quantity <= 0:
            return [], 0, None
        item = db.execute(
            'SELECT id, name, price_cents, restaurant_id FROM menu_item WHERE id = ?',
            (item_id,),
        ).fetchone()
        if item is None or item['restaurant_id'] != restaurant_id:
            return [], 0, None
        subtotal = item['price_cents'] * quantity
        items.append({'id': item['id'], 'name': item['name'], 'quantity': quantity,
                      'price_cents': item['price_cents'], 'subtotal_cents': subtotal})
        total += subtotal
    return items, total, restaurant_id


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout_page():
    items, total, restaurant_id = cart_details()
    errors = []
    customer_name = ''
    pickup_time = ''

    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        pickup_time = request.form.get('pickup_time', '')
        if not customer_name:
            errors.append('Customer name is required.')
        if not is_valid_slot(pickup_time):
            errors.append('Select a valid future pickup time.')
        if not items:
            errors.append('Your cart is empty or invalid.')
        if not errors:
            db = get_db()
            try:
                cursor = db.execute(
                    '''INSERT INTO orders
                       (restaurant_id, customer_name, pickup_time, status, total_cents)
                       VALUES (?, ?, ?, 'Received', ?)''',
                    (restaurant_id, customer_name, pickup_time, total),
                )
                order_id = cursor.lastrowid
                for item in items:
                    db.execute(
                        '''INSERT INTO order_item
                           (order_id, menu_item_id, quantity, unit_price_cents)
                           VALUES (?, ?, ?, ?)''',
                        (order_id, item['id'], item['quantity'], item['price_cents']),
                    )
                db.commit()
            except Exception:
                db.rollback()
                raise
            session.pop('cart', None)
            return redirect(url_for('checkout.confirmation', order_id=order_id))

    return render_template('checkout.html', items=items, total_cents=total,
                           errors=errors, customer_name=customer_name,
                           pickup_time=pickup_time)


@bp.route('/orders/<int:order_id>/confirmation')
def confirmation(order_id):
    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order is None:
        abort(404)
    items = db.execute(
        '''SELECT m.name, oi.quantity, oi.unit_price_cents
           FROM order_item oi JOIN menu_item m ON m.id = oi.menu_item_id
           WHERE oi.order_id = ? ORDER BY oi.id''',
        (order_id,),
    ).fetchall()
    return render_template('confirmation.html', order=order, items=items)
