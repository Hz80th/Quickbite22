import os

from flask import Flask, redirect, render_template, request, url_for, abort

import db
import pickup
import demo_db
from demo_auth import bp as demo_auth_bp, current_user
from cart import bp as cart_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"   # needed later for the session cart (PBI-05)
    app.config["DATABASE"] = os.path.join(app.root_path, "quickbite.db")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    demo_db.init_app(app)
    app.register_blueprint(demo_auth_bp)

    pickup.init_app(app)
    app.register_blueprint(cart_bp)

    @app.context_processor
    def inject_cart():
        from cart import cart_summary
        count, total = cart_summary()
        return {"cart_count": count, "cart_total_cents": total, "current_user": current_user()}


    from checkout import bp as checkout_bp
    from staff import bp as staff_bp
    app.register_blueprint(checkout_bp)
    app.register_blueprint(staff_bp)

    @app.route("/")
    def index():
        restaurants = db.get_db().execute(
            "SELECT * FROM restaurant ORDER BY name"
        ).fetchall()
        return render_template("index.html", restaurants=restaurants)

    @app.route("/restaurants/<int:restaurant_id>")
    def restaurant_menu(restaurant_id):
        # Load one restaurant and only its items (PBI-04)
        database = db.get_db()
        restaurant = database.execute(
            "SELECT * FROM restaurant WHERE id = ?", (restaurant_id,)
        ).fetchone()
        if restaurant is None:
            abort(404)
        items = database.execute(
            "SELECT * FROM menu_item WHERE restaurant_id = ? ORDER BY name",
            (restaurant_id,),
        ).fetchall()
        return render_template("restaurant_menu.html", restaurant=restaurant, items=items)

    @app.route("/orders/<int:order_id>/status")
    def order_status(order_id):
        # Load one order and show its current status (PBI-10)
        database = db.get_db()
        order = database.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        if order is None:
            return render_template("order_not_found.html"), 404
        items = database.execute(
            "SELECT m.name, oi.quantity, oi.unit_price_cents "
            "FROM order_item oi JOIN menu_item m ON m.id = oi.menu_item_id "
            "WHERE oi.order_id = ? ORDER BY oi.id",
            (order_id,),
        ).fetchall()
        return render_template("order_status.html", order=order, items=items)
 
    @app.route("/track")
    def track():
        # Look up an order by its ID (PBI-10)
        order_id = request.args.get("order_id", "")
        if order_id:
            if order_id.isdigit():
                return redirect(url_for("order_status", order_id=int(order_id)))
            return render_template("track.html", error="Enter a valid order ID.")
        return render_template("track.html")


    return app


if __name__ == "__main__":
    create_app().run(debug=True)
