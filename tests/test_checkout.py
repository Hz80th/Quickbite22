from db import get_db
from pickup import get_pickup_slots


def add_test_cart(client):
    with client.session_transaction() as session:
        session['cart'] = {'restaurant_id': 1, 'items': {'1': 2}}


def test_checkout_requires_name(client):
    add_test_cart(client)
    slot = get_pickup_slots()[0]
    response = client.post('/checkout', data={'customer_name': ' ', 'pickup_time': slot})
    assert b'Customer name is required' in response.data


def test_checkout_rejects_invalid_pickup(client):
    add_test_cart(client)
    response = client.post('/checkout', data={'customer_name': 'Alex', 'pickup_time': '2000-01-01T12:00'})
    assert b'Select a valid future pickup time' in response.data


def test_checkout_rejects_empty_cart(client):
    response = client.post('/checkout', data={'customer_name': 'Alex', 'pickup_time': get_pickup_slots()[0]})
    assert b'Your cart is empty' in response.data


def test_checkout_saves_order_and_clears_cart(app, client):
    add_test_cart(client)
    slot = get_pickup_slots()[0]
    response = client.post('/checkout', data={'customer_name': 'Alex', 'pickup_time': slot}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Order Confirmed' in response.data
    with app.app_context():
        db = get_db()
        order = db.execute('SELECT * FROM orders WHERE customer_name = ?', ('Alex',)).fetchone()
        assert order is not None
        assert order['status'] == 'Received'
        assert order['pickup_time'] == slot
        item = db.execute('SELECT * FROM order_item WHERE order_id = ?', (order['id'],)).fetchone()
        assert item['quantity'] == 2
        assert order['total_cents'] == item['unit_price_cents'] * 2
    with client.session_transaction() as session:
        assert 'cart' not in session

