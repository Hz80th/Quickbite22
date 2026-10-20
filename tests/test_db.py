import sqlite3

import pytest

from db import get_db, init_db


def test_seed_loads_three_restaurants_with_five_items_each(app):
    with app.app_context():
        db = get_db()
        assert db.execute("SELECT COUNT(*) FROM restaurant").fetchone()[0] == 3
        counts = db.execute(
            "SELECT restaurant_id, COUNT(*) FROM menu_item GROUP BY restaurant_id"
        ).fetchall()
        assert len(counts) == 3
        assert all(row[1] >= 5 for row in counts)


def test_init_db_resets_data(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO restaurant (name, address) VALUES ('Temp', 'Nowhere')")
        db.commit()
        init_db()
        assert db.execute("SELECT COUNT(*) FROM restaurant").fetchone()[0] == 3


def test_invalid_order_status_is_rejected(app):
    with app.app_context():
        db = get_db()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO orders (restaurant_id, customer_name, pickup_time, status, total_cents) "
                "VALUES (1, 'Test', '2026-10-20 12:00', 'Lost', 1000)"
            )
