from datetime import datetime

from flask import render_template_string

from pickup import get_pickup_slots, is_valid_slot

NOW = datetime(2026, 10, 20, 14, 7)


def test_slots_start_15_minutes_ahead_on_quarter_hours_for_2_hours():
    slots = get_pickup_slots(NOW)
    assert slots[0] == "2026-10-20 14:30"
    assert slots[-1] == "2026-10-20 16:00"
    assert len(slots) == 7


def test_slot_exactly_15_minutes_ahead_is_included():
    assert get_pickup_slots(datetime(2026, 10, 20, 14, 0))[0] == "2026-10-20 14:15"


def test_past_and_invalid_times_are_rejected():
    assert is_valid_slot("2026-10-20 14:30", NOW)
    assert not is_valid_slot("2026-10-20 13:45", NOW)   # past
    assert not is_valid_slot("2026-10-20 14:31", NOW)   # not a 15-min slot
    assert not is_valid_slot("2026-10-20 18:00", NOW)   # beyond 2 hours
    assert not is_valid_slot("not a time", NOW)
    assert not is_valid_slot(None, NOW)


def test_dropdown_requires_a_choice(app):
    with app.test_request_context():
        html = render_template_string('{% include "_pickup_select.html" %}')
    assert 'name="pickup_time"' in html
    assert "required" in html
    assert '<option value="" disabled selected>' in html
