import os

from flask import Flask, render_template

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
        return render_template("index.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
