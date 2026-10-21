from db import get_db


def test_staff_hides_finished_and_sorts(app, client):
    with app.app_context():
        db = get_db()
        for name, pickup, status in [
            ('Late', '2026-10-25T19:00', 'Received'),
            ('Early', '2026-10-25T17:00', 'Preparing'),
            ('CompletedName', '2026-10-25T16:00', 'Completed'),
            ('CancelledName', '2026-10-25T15:00', 'Cancelled'),
        ]:
            db.execute('INSERT INTO orders (restaurant_id, customer_name, pickup_time, status, total_cents) VALUES (?, ?, ?, ?, ?)',
                       (1, name, pickup, status, 100))
        db.execute('INSERT INTO orders (restaurant_id, customer_name, pickup_time, status, total_cents) VALUES (?, ?, ?, ?, ?)',
                   (2, 'OtherRestaurant', '2026-10-25T18:00', 'Received', 100))
        db.commit()
    response = client.get('/staff/orders?restaurant_id=1')
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Early' in html and 'Late' in html
    assert html.index('Early') < html.index('Late')
    assert 'CompletedName' not in html
    assert 'CancelledName' not in html
    assert 'OtherRestaurant' not in html


def test_staff_empty_orders(client):
    response = client.get('/staff/orders?restaurant_id=999999')
    assert b'No active orders' in response.data



def _create_order(app, status='Received'):
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            'INSERT INTO orders (restaurant_id, customer_name, pickup_time, status, total_cents) '
            'VALUES (?, ?, ?, ?, ?)',
            (1, 'StatusTest', '2026-10-25 17:00', status, 100),
        )
        db.commit()
        return cursor.lastrowid


def _status(app, order_id):
    with app.app_context():
        row = get_db().execute('SELECT status FROM orders WHERE id = ?', (order_id,)).fetchone()
        return row['status']


def test_advance_order_one_step_and_persists(app, client):
    order_id = _create_order(app)
    response = client.post(
        f'/staff/orders/{order_id}/advance',
        data={'next_status': 'Preparing'},
    )
    assert response.status_code == 302
    assert _status(app, order_id) == 'Preparing'
    html = client.get('/staff/orders?restaurant_id=1').get_data(as_text=True)
    assert 'Preparing' in html
    assert 'StatusTest' in html


def test_reject_skip_and_backward(app, client):
    order_id = _create_order(app, 'Received')
    response = client.post(
        f'/staff/orders/{order_id}/advance', data={'next_status': 'Completed'}
    )
    assert response.status_code == 400
    assert _status(app, order_id) == 'Received'

    client.post(f'/staff/orders/{order_id}/advance', data={'next_status': 'Preparing'})
    response = client.post(
        f'/staff/orders/{order_id}/advance', data={'next_status': 'Received'}
    )
    assert response.status_code == 400
    assert _status(app, order_id) == 'Preparing'


def test_completed_order_disappears_from_active_list(app, client):
    order_id = _create_order(app, 'Ready for Pickup')
    response = client.post(
        f'/staff/orders/{order_id}/advance', data={'next_status': 'Completed'}
    )
    assert response.status_code == 302
    assert _status(app, order_id) == 'Completed'
    html = client.get('/staff/orders?restaurant_id=1').get_data(as_text=True)
    assert 'StatusTest' not in html
    assert client.post(
        f'/staff/orders/{order_id}/advance', data={'next_status': 'Preparing'}
    ).status_code == 409


def test_missing_and_malformed_update(app, client):
    order_id = _create_order(app)
    assert client.post(f'/staff/orders/{order_id}/advance').status_code == 400
    assert _status(app, order_id) == 'Received'
    assert client.post('/staff/orders/999999/advance',
                       data={'next_status':'Preparing'}).status_code == 404
