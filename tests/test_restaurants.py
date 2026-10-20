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

def test_menu_shows_only_that_restaurants_items(client):
    # Restaurant 1's menu has its items, not restaurant 2's
    r = client.get("/restaurants/1")
    assert r.status_code == 200
    assert b"Maple Bistro" in r.data
    assert b"Poutine" in r.data
    assert b"$11.99" in r.data
    assert b"Pho Tai" not in r.data
 
 
def test_menu_has_back_link(client):
    # The menu page links back to the restaurant list
    r = client.get("/restaurants/1")
    assert b"Back to restaurants" in r.data
