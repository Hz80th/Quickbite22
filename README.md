# QuickBite

Web app for ordering food from local restaurants for pickup.

## Setup
1. Clone the repo and open the folder
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r requirements.txt`
5. `flask --app app init-db` (creates the database with sample data)

## Run
`python app.py`, then open http://127.0.0.1:5000

## Reset the database
`flask --app app init-db` drops all data and reloads the sample restaurants and menus.

## Test
`python -m pytest`

## Database
Use `get_db()` from `db.py`; do not open SQLite directly.
Tables: `restaurant`, `menu_item`, `orders`, `order_item`. Prices are stored in cents.
Order statuses: Received, Preparing, Ready for Pickup, Completed, Cancelled.

## Team workflow
- One branch per PBI, e.g. `feature/pbi-05-cart`
- Open a pull request with `Closes #N` in the description
- At least 1 approving review before merging into `main`
