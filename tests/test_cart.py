def test_add_item_increases_quantity(client):
    client.post("/cart/add/1")
    client.post("/cart/add/1")
    assert client.get("/cart/summary").get_json()["count"] == 2
 
 
def test_one_restaurant_rule(client):
    client.post("/cart/add/1")
    r = client.post("/cart/add/6")
    assert r.get_json()["ok"] is False
 
 
def test_clear_cart(client):
    client.post("/cart/add/1")
    client.post("/cart/clear")
    assert client.get("/cart/summary").get_json()["count"] == 0
 
 
def test_cart_persists_across_pages(client):
    # Add an item, visit the home page, the cart is still there
    client.post("/cart/add/1")
    client.get("/")
    assert client.get("/cart/summary").get_json()["count"] == 1
