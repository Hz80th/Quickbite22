"""PBI-08: Restaurant staff active order display."""
from flask import Blueprint, render_template, request, redirect, url_for, abort
from db import get_db

bp = Blueprint('staff', __name__)


@bp.route('/staff/orders')
def orders():
    db = get_db()
    restaurants = db.execute('SELECT id, name FROM restaurant ORDER BY name').fetchall()
    chosen = request.args.get('restaurant_id', type=int)
    orders_with_items = []
    if chosen is not None:
        active_orders = db.execute(
            '''SELECT id, customer_name, pickup_time, status
               FROM orders
               WHERE restaurant_id = ? AND status IN
                 ('Received', 'Preparing', 'Ready for Pickup')
               ORDER BY pickup_time ASC, id ASC''',
            (chosen,),
        ).fetchall()
        for order in active_orders:
            items = db.execute(
                '''SELECT m.name, oi.quantity FROM order_item oi
                   JOIN menu_item m ON m.id = oi.menu_item_id
                   WHERE oi.order_id = ? ORDER BY oi.id''',
                (order['id'],),
            ).fetchall()
            orders_with_items.append({'order': order, 'items': items})
    return render_template('staff_orders.html', restaurants=restaurants,
                           restaurant_id=chosen, orders=orders_with_items)


# The allowed workflow, in order. Completed/Cancelled cannot advance.
STATUS_FLOW = ('Received', 'Preparing', 'Ready for Pickup', 'Completed')


@bp.route('/staff/orders/<int:order_id>/advance', methods=['POST'])
def advance_order(order_id):
    db = get_db()
    order = db.execute(
        'SELECT id, restaurant_id, status FROM orders WHERE id = ?',
        (order_id,),
    ).fetchone()
    if order is None:
        abort(404)

    current = order['status']
    if current not in STATUS_FLOW[:-1]:
        abort(409, description='This order cannot be advanced.')

    # The client must request exactly the next state; never trust UI controls.
    expected_next = STATUS_FLOW[STATUS_FLOW.index(current) + 1]
    requested_next = request.form.get('next_status')
    if requested_next != expected_next:
        abort(400, description='Only the next status is allowed.')

    # Atomic conditional update prevents stale concurrent submissions.
    updated = db.execute(
        'UPDATE orders SET status = ? WHERE id = ? AND status = ?',
        (expected_next, order_id, current),
    )
    if updated.rowcount != 1:
        db.rollback()
        abort(409, description='Order status changed. Refresh and retry.')
    db.commit()
    return redirect(url_for('staff.orders', restaurant_id=order['restaurant_id']))
