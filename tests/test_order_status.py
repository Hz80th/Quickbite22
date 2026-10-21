from db import get_db
 
 
def create_test_order(app):
    # Create one order with 2 Poutine for testing
    with app.app_context():
        database = get_db()
        cursor = database.execute(
            "INSERT INTO orders (restaurant_id, customer_name, pickup_time, status, total_cents) "
            "VALUES (1, 'Alex', '2026-10-22T12:00', 'Received', 1199)"
        )
        order_id = cursor.lastrowid
        database.execute(
            "INSERT INTO order_item (order_id, menu_item_id, quantity, unit_price_cents) "
            "VALUES (?, 1, 2, 1199)",
            (order_id,),
        )
        database.commit()
        return order_id
 
 
def test_status_page_shows_order_details(client, app):
    # The status page shows status, pickup time and the items
    order_id = create_test_order(app)
    r = client.get(f"/orders/{order_id}/status")
    assert r.status_code == 200
    assert b"Received" in r.data
    assert b"Alex" in r.data
    assert b"Poutine" in r.data
    assert b"$11.99" in r.data
 
 
def test_unknown_order_shows_not_found(client):
    # An unknown order ID shows the not-found message
    r = client.get("/orders/999999/status")
    assert r.status_code == 404
    assert b"Order not found" in r.data
 
 
def test_status_updates_after_staff_change(client, app):
    # When staff changes the status, the page shows it after refresh
    order_id = create_test_order(app)
    with app.app_context():
        database = get_db()
        database.execute("UPDATE orders SET status = 'Preparing' WHERE id = ?", (order_id,))
        database.commit()
    r = client.get(f"/orders/{order_id}/status")
    assert b"Preparing" in r.data
 
 
def test_track_lookup_redirects_to_status(client, app):
    # The /track page with a valid order ID redirects to the status page
    order_id = create_test_order(app)
    r = client.get(f"/track?order_id={order_id}")
    assert r.status_code == 302
    assert f"/orders/{order_id}/status" in r.headers["Location"]
