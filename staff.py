"""PBI-08: Restaurant staff active order display."""
from flask import Blueprint, render_template, request
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
