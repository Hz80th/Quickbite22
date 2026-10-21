"""Create/update demo users without deleting existing orders."""
import click
from flask import current_app
from db import get_db

USERS = [
    (101, 'Alex Chen', 'customer', None),
    (102, 'Jamie Lee', 'customer', None),
    (103, 'Mengqi', 'customer', None),
    (104, 'Tetant', 'customer', None),
    (105, 'Shenhuan', 'customer', None),
    (201, 'Sam', 'staff', 1),
    (202, 'Linh', 'staff', 2),
    (203, 'Marco', 'staff', 3),
]


def ensure_demo_users():
    db = get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS demo_user (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL CHECK (role IN ('customer','staff')),
        restaurant_id INTEGER REFERENCES restaurant(id),
        CHECK ((role = 'customer' AND restaurant_id IS NULL) OR
               (role = 'staff' AND restaurant_id IS NOT NULL))
    )""")
    for id_, name, role, restaurant_id in USERS:
        db.execute("""INSERT INTO demo_user (id, name, role, restaurant_id)
             VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET
             name=excluded.name, role=excluded.role, restaurant_id=excluded.restaurant_id""",
             (id_, name, role, restaurant_id))
    db.commit()


@click.command('init-demo-users')
def init_demo_users_command():
    ensure_demo_users()
    click.echo('Demo users ready (existing orders preserved).')


def init_app(app):
    app.cli.add_command(init_demo_users_command)
