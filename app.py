from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"          # needed later for the session cart (PBI-05)
    app.config["DATABASE"] = "quickbite.db"   # SQLite file (PBI-02)

    if test_config:
        app.config.update(test_config)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
