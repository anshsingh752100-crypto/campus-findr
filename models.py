"""
models.py — SQLAlchemy ORM models for Campus Findr.

Defines the Item model representing both lost and found items.
"""

from datetime import datetime, date
from database import db


# Application-level category choices
CATEGORIES = [
    ("id_card", "ID Card"),
    ("electronics", "Electronics"),
    ("keys", "Keys"),
    ("books", "Books"),
    ("bottle", "Bottle"),
    ("other", "Other"),
]


class Item(db.Model):
    """Represents a lost or found item posted on Campus Findr."""

    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # "lost" or "found"
    item_type = db.Column(db.String(10), nullable=False)

    # "open" or "claimed"
    status = db.Column(db.String(15), nullable=False, default="open")

    # Auto-set when the item is posted
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # User-entered date when the item was lost or found
    date_occurred = db.Column(db.Date, nullable=False)

    # Suspected lost location or where the item was found
    location = db.Column(db.String(200), nullable=False)

    # Only for found items — where the item was deposited for pickup
    deposit_location = db.Column(db.String(200), nullable=True)

    # Reporter's college email
    contact_email = db.Column(db.String(120), nullable=False)

    # Photo filenames (stored in static/uploads/)
    photo_filename = db.Column(db.String(255), nullable=True)
    thumbnail_filename = db.Column(db.String(255), nullable=True)

    # Claim / verification fields
    claim_detail = db.Column(db.Text, nullable=True)
    claimed_by_email = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        """Serialize the item to a dictionary for the JSON API."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "item_type": self.item_type,
            "status": self.status,
            "date_reported": self.date_reported.isoformat(),
            "date_occurred": self.date_occurred.isoformat(),
            "location": self.location,
            "deposit_location": self.deposit_location,
            "contact_email": self.contact_email,
            "photo_filename": self.photo_filename,
            "thumbnail_filename": self.thumbnail_filename,
            "claim_detail": self.claim_detail,
            "claimed_by_email": self.claimed_by_email,
        }

    def __repr__(self):
        return f"<Item {self.id}: {self.title} ({self.item_type}/{self.status})>"
