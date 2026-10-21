DROP TABLE IF EXISTS demo_user;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS menu_item;
DROP TABLE IF EXISTS restaurant;

CREATE TABLE restaurant (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  address TEXT NOT NULL
);

CREATE TABLE menu_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  restaurant_id INTEGER NOT NULL REFERENCES restaurant(id),
  name TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents > 0)
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  restaurant_id INTEGER NOT NULL REFERENCES restaurant(id),
  customer_name TEXT NOT NULL,
  pickup_time TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Received'
    CHECK (status IN ('Received', 'Preparing', 'Ready for Pickup', 'Completed', 'Cancelled')),
  total_cents INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_item (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL REFERENCES orders(id),
  menu_item_id INTEGER NOT NULL REFERENCES menu_item(id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price_cents INTEGER NOT NULL
);

CREATE TABLE demo_user (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('customer','staff')),
  restaurant_id INTEGER REFERENCES restaurant(id),
  CHECK ((role='customer' AND restaurant_id IS NULL) OR (role='staff' AND restaurant_id IS NOT NULL))
);
