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
