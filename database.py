"""
database.py — Database engine initialization and seed data for Campus Findr.

Uses Flask-SQLAlchemy for ORM integration. The SQLite database file
(campus_findr.db) is created automatically in the project root.
"""

from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy

# Shared SQLAlchemy instance — imported by models.py and app.py
db = SQLAlchemy()


def init_db(app):
    """Initialize the database: create all tables if they don't exist."""
    with app.app_context():
        db.create_all()


def seed_db(app):
    """
    Insert 6 realistic campus items into the database.
    Only runs if the items table is empty (first launch).
    """
    from models import Item

    with app.app_context():
        if Item.query.first() is not None:
            return  # Already seeded

        seed_items = [
            Item(
                title="Blue Realme Earbuds",
                category="electronics",
                description="Lost my Realme Buds Air 3 (blue colour) somewhere near the "
                            "reading hall. They were in a small white case with my name "
                            "scratched on the back.",
                item_type="lost",
                status="open",
                date_occurred=date(2026, 9, 8),
                location="Library 2nd Floor",
                contact_email="arjun.mehta@college.edu",
            ),
            Item(
                title="College ID — Rahul Sharma",
                category="id_card",
                description="Found a student ID card for Rahul Sharma, B.Tech CSE "
                            "3rd Year, Roll No. 2024CSE1042. Card was lying on a table "
                            "near the billing counter.",
                item_type="found",
                status="open",
                date_occurred=date(2026, 9, 7),
                location="Canteen Block A",
                deposit_location="Left at Security Gate 1",
                contact_email="priya.singh@college.edu",
            ),
            Item(
                title="Honda Bike Key with Ring",
                category="keys",
                description="Misplaced my Honda Activa key with a red keyring and a "
                            "small Ganesha charm. Last had it while parking my scooter "
                            "in the morning.",
                item_type="lost",
                status="open",
                date_occurred=date(2026, 9, 9),
                location="Parking Lot B",
                contact_email="vikram.joshi@college.edu",
            ),
            Item(
                title="Engineering Mathematics-III (Grewal)",
                category="books",
                description="Found a copy of B.S. Grewal's Higher Engineering Mathematics "
                            "book left behind after the 2 PM lecture. Has some sticky notes "
                            "and yellow highlighting inside.",
                item_type="found",
                status="open",
                date_occurred=date(2026, 9, 6),
                location="CR-301, Main Building",
                deposit_location="Dept. Office, 2nd Floor",
                contact_email="neha.kapoor@college.edu",
            ),
            Item(
                title="Black Milton Water Bottle",
                category="bottle",
                description="Left my black Milton Thermosteel bottle (500 ml) at the "
                            "court after a practice match. Has a faded sticker of the "
                            "college logo on it.",
                item_type="lost",
                status="open",
                date_occurred=date(2026, 9, 9),
                location="Basketball Court",
                contact_email="rohan.das@college.edu",
            ),
            Item(
                title="USB-C Charging Cable",
                category="other",
                description="Found a braided grey USB-C cable plugged into the wall "
                            "socket in Lab 2. It was left behind after the evening "
                            "batch. Has been handed over to the lab assistant.",
                item_type="found",
                status="claimed",
                date_occurred=date(2026, 9, 5),
                location="Computer Lab 2",
                deposit_location="Lab Assistant's Desk, Lab 2",
                contact_email="ananya.rao@college.edu",
                claim_detail="Grey braided cable, about 1 meter long, "
                             "with a small blue band near the USB-A end.",
                claimed_by_email="karan.gupta@college.edu",
            ),
        ]

        db.session.add_all(seed_items)
        db.session.commit()
        print(f"[OK] Seeded {len(seed_items)} items into the database.")
