from datetime import datetime, timedelta

SLOT_MINUTES = 15
MIN_LEAD = timedelta(minutes=15)   # earliest pickup is 15 min from now
WINDOW = timedelta(hours=2)        # slots cover the next 2 hours
FORMAT = "%Y-%m-%d %H:%M"


def _first_slot(now):
    """Earliest time at least 15 minutes from now, rounded up to a quarter hour."""
    earliest = now + MIN_LEAD
    if earliest.second or earliest.microsecond:
        earliest = earliest.replace(second=0, microsecond=0) + timedelta(minutes=1)
    remainder = earliest.minute % SLOT_MINUTES
    if remainder:
        earliest += timedelta(minutes=SLOT_MINUTES - remainder)
    return earliest


def get_pickup_slots(now=None):
    """Return pickup slots as 'YYYY-MM-DD HH:MM' strings, every 15 minutes."""
    now = now or datetime.now()
    slot = _first_slot(now)
    end = now + WINDOW
    slots = []
    while slot <= end:
        slots.append(slot.strftime(FORMAT))
        slot += timedelta(minutes=SLOT_MINUTES)
    return slots


def is_valid_slot(value, now=None):
    """Server-side check for checkout: a future quarter-hour within the 2-hour window."""
    now = now or datetime.now()
    try:
        slot = datetime.strptime(value, FORMAT)
    except (ValueError, TypeError):
        return False
    return slot.minute % SLOT_MINUTES == 0 and now < slot <= now + WINDOW


def init_app(app):
    """Make get_pickup_slots available inside every template."""
    @app.context_processor
    def inject_pickup_slots():
        return {"get_pickup_slots": get_pickup_slots}
