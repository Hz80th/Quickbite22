import os

from flask import Flask, render_template, abort

import db
import pickup
from cart import bp as cart_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"   # needed later for the session cart (PBI-05)
    app.config["DATABASE"] = os.path.join(app.root_path, "quickbite.db")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    pickup.init_app(app)
    app.register_blueprint(cart_bp)

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


    return app


if __name__ == "__main__":
    create_app().run(debug=True)
