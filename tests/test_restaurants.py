from db import get_db
 
 
def test_home_shows_all_restaurants(client):
    # The home page lists every restaurant with name and address
    r = client.get("/")
    assert r.status_code == 200
    assert b"Maple Bistro" in r.data
    assert b"1200 Rue Sainte-Catherine O, Montreal" in r.data
    assert b"Saigon Express" in r.data
 
 
def test_empty_restaurants_shows_message(client, app):
    # With no restaurants, the page shows the empty message
    with app.app_context():
        database = get_db()
        database.execute("DELETE FROM menu_item")
        database.execute("DELETE FROM restaurant")
        database.commit()
    r = client.get("/")
    assert b"No restaurants available." in r.data
