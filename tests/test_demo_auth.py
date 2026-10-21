from db import get_db


def login(client, id):
    return client.post('/login', data={'user_id': str(id)})


def test_login_and_checkout_name(client):
    assert b'Demo only, no passwords' in client.get('/login').data
    response = login(client, 101)
    assert response.status_code == 302
    with client.session_transaction() as s:
        assert s['demo_user_id'] == 101
    with client.session_transaction() as s:
        s['cart'] = {'restaurant_id': 1, 'items': {'1': 1}}
    html = client.get('/checkout').get_data(as_text=True)
    assert 'Alex Chen' in html
    assert 'readonly' in html


def test_staff_redirect_and_isolation(client, app):
    assert login(client, 201).headers['Location'].endswith('/staff/orders')
    assert client.get('/staff/orders?restaurant_id=2').status_code == 200
    with app.app_context():
        db = get_db()
        cur = db.execute("INSERT INTO orders (restaurant_id, customer_name, pickup_time, status, total_cents) VALUES (2,'SECRET','2026-10-25 17:00','Received',100)")
        order_id = cur.lastrowid
        db.commit()
    assert 'SECRET' not in client.get('/staff/orders?restaurant_id=2').get_data(as_text=True)
    assert client.post(f'/staff/orders/{order_id}/advance', data={'next_status':'Preparing'}).status_code == 403


def test_guest_and_customer_forbidden_from_staff(client):
    assert client.get('/staff/orders').status_code == 302
    assert client.post('/staff/orders/1/advance', data={'next_status':'Preparing'}).status_code == 302
    login(client, 102)
    assert client.get('/staff/orders').status_code == 403
    assert client.post('/staff/orders/1/advance', data={'next_status':'Preparing'}).status_code == 403


def test_switch_user_clears_cart(client):
    login(client, 101)
    with client.session_transaction() as s:
        s['cart'] = {'restaurant_id': 1, 'items': {'1': 2}}
    client.post('/logout')
    with client.session_transaction() as s:
        assert 'demo_user_id' not in s
        assert 'cart' not in s
    assert login(client, 'nope').status_code == 200
