from flask import Blueprint, session, jsonify, render_template
from db import get_db
 
bp = Blueprint("cart", __name__)
 
 
def get_cart():
    # Read the cart from the browser session
    return session.get("cart", {})
 
 
def save_cart(cart):
    # Save the cart back to the session
    session["cart"] = cart
 
 
@bp.route("/cart/add/<int:item_id>", methods=["POST"])
def add(item_id):
    # Find the item in the database
    db = get_db()
    item = db.execute(
        "SELECT id, price_cents, restaurant_id FROM menu_item WHERE id = ?",
        (item_id,),
    ).fetchone()
    if item is None:
        return jsonify({"ok": False, "error": "item_not_found"})
 
    cart = get_cart()
    # Only one restaurant is allowed in one cart
    if cart and cart["restaurant_id"] != item["restaurant_id"]:
        return jsonify({"ok": False, "error": "different_restaurant"})
 
    # Start a new cart when it is empty
    if not cart:
        cart = {"restaurant_id": item["restaurant_id"], "items": {}}
 
    # Add one to the quantity
    item_id = str(item_id)
    if item_id in cart["items"]:
        cart["items"][item_id] += 1
    else:
        cart["items"][item_id] = 1
    save_cart(cart)
    return jsonify({"ok": True})
 
 
@bp.route("/cart/clear", methods=["POST"])
def clear():
    # Empty the cart
    session.pop("cart", None)
    return jsonify({"ok": True})
 
 
def cart_summary():
    # Count and total price for the top indicator
    cart = get_cart()
    db = get_db()
    count = 0
    total = 0
    for item_id, qty in cart.get("items", {}).items():
        row = db.execute(
            "SELECT price_cents FROM menu_item WHERE id = ?", (int(item_id),)
        ).fetchone()
        if row:
            count += qty
            total += row["price_cents"] * qty
    return count, total


@bp.route("/cart/summary")
def summary():
    # Return the count and total price for the top indicator
    count, total = cart_summary()
    return jsonify({"count": count, "total_cents": total})
 
 
@bp.route("/menu")
def menu():
    # Temporary menu page (teammate B builds the real one in PBI-03/04)
    db = get_db()
    restaurants = db.execute("SELECT * FROM restaurant").fetchall()
    items = db.execute("SELECT * FROM menu_item ORDER BY restaurant_id, id").fetchall()
    return render_template("menu.html", restaurants=restaurants, items=items)
