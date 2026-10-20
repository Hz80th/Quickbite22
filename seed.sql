INSERT INTO restaurant (name, address) VALUES
  ('Maple Bistro', '1200 Rue Sainte-Catherine O, Montreal'),
  ('Saigon Express', '455 Boulevard Saint-Laurent, Montreal'),
  ('Napoli Slice', '88 Rue Sherbrooke E, Montreal');

INSERT INTO menu_item (restaurant_id, name, price_cents) VALUES
  (1, 'Poutine', 1199),
  (1, 'Club Sandwich', 1450),
  (1, 'Caesar Salad', 1095),
  (1, 'Tomato Soup', 695),
  (1, 'Maple Pie', 650),
  (2, 'Pho Tai', 1495),
  (2, 'Banh Mi', 1050),
  (2, 'Spring Rolls', 795),
  (2, 'Vermicelli Bowl', 1395),
  (2, 'Iced Coffee', 495),
  (3, 'Margherita Pizza', 1600),
  (3, 'Pepperoni Pizza', 1750),
  (3, 'Garlic Knots', 650),
  (3, 'Arancini', 895),
  (3, 'Tiramisu', 750);
