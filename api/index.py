"""
api/index.py — Self-contained Flask app for Vercel deployment.
All models, database config, and routes in one file for Vercel compatibility.
"""

import os
import uuid
from datetime import date, datetime

from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campus-findr-dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/campus_findr.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
THUMBNAIL_SIZE = (300, 300)

db = SQLAlchemy(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ---------------------------------------------------------------------------
# Category Choices
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("id_card", "ID Card"),
    ("electronics", "Electronics"),
    ("keys", "Keys"),
    ("books", "Books"),
    ("bottle", "Bottle"),
    ("other", "Other"),
]

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    item_type = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(15), nullable=False, default="open")
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_occurred = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    deposit_location = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(120), nullable=False)
    photo_filename = db.Column(db.String(255), nullable=True)
    thumbnail_filename = db.Column(db.String(255), nullable=True)
    claim_detail = db.Column(db.Text, nullable=True)
    claimed_by_email = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "category": self.category,
            "description": self.description, "item_type": self.item_type,
            "status": self.status, "date_reported": self.date_reported.isoformat(),
            "date_occurred": self.date_occurred.isoformat(),
            "location": self.location, "deposit_location": self.deposit_location,
            "contact_email": self.contact_email,
            "photo_filename": self.photo_filename,
            "thumbnail_filename": self.thumbnail_filename,
            "claim_detail": self.claim_detail,
            "claimed_by_email": self.claimed_by_email,
        }

# ---------------------------------------------------------------------------
# Seed Data
# ---------------------------------------------------------------------------
def seed_db():
    if Item.query.first() is not None:
        return
    seeds = [
        Item(title="Blue Realme Earbuds", category="electronics",
             description="Lost my Realme Buds Air 3 (blue colour) somewhere near the reading hall. Small white case with my name scratched on the back.",
             item_type="lost", status="open", date_occurred=date(2026, 9, 8),
             location="Library 2nd Floor", contact_email="arjun.mehta@college.edu"),
        Item(title="College ID \u2014 Rahul Sharma", category="id_card",
             description="Found a student ID card for Rahul Sharma, B.Tech CSE 3rd Year, Roll No. 2024CSE1042.",
             item_type="found", status="open", date_occurred=date(2026, 9, 7),
             location="Canteen Block A", deposit_location="Left at Security Gate 1",
             contact_email="priya.singh@college.edu"),
        Item(title="Honda Bike Key with Ring", category="keys",
             description="Misplaced my Honda Activa key with a red keyring and a small Ganesha charm.",
             item_type="lost", status="open", date_occurred=date(2026, 9, 9),
             location="Parking Lot B", contact_email="vikram.joshi@college.edu"),
        Item(title="Engineering Mathematics-III (Grewal)", category="books",
             description="Found a copy of B.S. Grewal's Higher Engineering Mathematics left after the 2 PM lecture.",
             item_type="found", status="open", date_occurred=date(2026, 9, 6),
             location="CR-301, Main Building", deposit_location="Dept. Office, 2nd Floor",
             contact_email="neha.kapoor@college.edu"),
        Item(title="Black Milton Water Bottle", category="bottle",
             description="Left my black Milton Thermosteel bottle (500 ml) at the court after practice.",
             item_type="lost", status="open", date_occurred=date(2026, 9, 9),
             location="Basketball Court", contact_email="rohan.das@college.edu"),
        Item(title="USB-C Charging Cable", category="other",
             description="Found a braided grey USB-C cable plugged into the wall socket in Lab 2.",
             item_type="found", status="claimed", date_occurred=date(2026, 9, 5),
             location="Computer Lab 2", deposit_location="Lab Assistant's Desk, Lab 2",
             contact_email="ananya.rao@college.edu",
             claim_detail="Grey braided cable, about 1 meter, blue band near USB-A end.",
             claimed_by_email="karan.gupta@college.edu"),
    ]
    db.session.add_all(seeds)
    db.session.commit()

# ---------------------------------------------------------------------------
# DB init on every cold start
# ---------------------------------------------------------------------------
@app.before_request
def ensure_db():
    if not os.path.exists("/tmp/campus_findr.db"):
        with app.app_context():
            db.create_all()
            seed_db()

# Initialize on import too
try:
    with app.app_context():
        db.create_all()
        seed_db()
except Exception:
    pass

# ---------------------------------------------------------------------------
# Template Context
# ---------------------------------------------------------------------------
@app.context_processor
def inject_categories():
    return dict(categories=CATEGORIES)

# ---------------------------------------------------------------------------
# Image Helpers
# ---------------------------------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_id = uuid.uuid4().hex[:10]
        safe_name = secure_filename(file.filename)
        original_name = f"{unique_id}_{safe_name}"
        thumb_name = f"thumb_{original_name}"
        original_path = os.path.join(app.config["UPLOAD_FOLDER"], original_name)
        thumb_path = os.path.join(app.config["UPLOAD_FOLDER"], thumb_name)
        file.save(original_path)
        try:
            with Image.open(original_path) as img:
                img.thumbnail(THUMBNAIL_SIZE)
                img.save(thumb_path)
        except Exception:
            thumb_name = None
        return original_name, thumb_name
    return None, None

def delete_photo(filename):
    if filename:
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(path):
            os.remove(path)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    items = Item.query.order_by(Item.date_reported.desc()).all()
    return render_template("index.html", items=items)

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template("report.html")
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "")
    description = request.form.get("description", "").strip()
    item_type = request.form.get("item_type", "lost")
    date_occurred_str = request.form.get("date_occurred", "")
    location = request.form.get("location", "").strip()
    deposit_location = request.form.get("deposit_location", "").strip() or None
    contact_email = request.form.get("contact_email", "").strip()
    if not all([title, category, description, date_occurred_str, location, contact_email]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("report"))
    try:
        date_occurred = date.fromisoformat(date_occurred_str)
    except ValueError:
        flash("Invalid date format.", "error")
        return redirect(url_for("report"))
    photo_filename, thumbnail_filename = None, None
    if "photo" in request.files:
        photo_filename, thumbnail_filename = save_photo(request.files["photo"])
    new_item = Item(
        title=title, category=category, description=description,
        item_type=item_type, date_occurred=date_occurred, location=location,
        deposit_location=deposit_location, contact_email=contact_email,
        photo_filename=photo_filename, thumbnail_filename=thumbnail_filename,
    )
    db.session.add(new_item)
    db.session.commit()
    flash("Item reported successfully!", "success")
    return redirect(url_for("index"))

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template("item_detail.html", item=item)

@app.route("/item/<int:item_id>/claim", methods=["POST"])
def claim_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.status == "claimed":
        flash("This item has already been claimed.", "info")
        return redirect(url_for("item_detail", item_id=item_id))
    claim_detail = request.form.get("claim_detail", "").strip()
    claimed_by_email = request.form.get("claimed_by_email", "").strip()
    if not claim_detail or not claimed_by_email:
        flash("Please provide your email and a verification detail.", "error")
        return redirect(url_for("item_detail", item_id=item_id))
    item.claim_detail = claim_detail
    item.claimed_by_email = claimed_by_email
    db.session.commit()
    flash("Claim submitted! The reporter will verify your details.", "success")
    return redirect(url_for("item_detail", item_id=item_id))

@app.route("/item/<int:item_id>/resolve", methods=["POST"])
def resolve_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.status = "claimed"
    db.session.commit()
    flash("Item marked as claimed/resolved.", "success")
    return redirect(url_for("item_detail", item_id=item_id))

@app.route("/admin/delete/<int:item_id>", methods=["POST"])
def admin_delete(item_id):
    item = Item.query.get_or_404(item_id)
    delete_photo(item.photo_filename)
    delete_photo(item.thumbnail_filename)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully.", "success")
    return redirect(url_for("index"))

@app.route("/api/items")
def api_items():
    query = Item.query
    q = request.args.get("q", "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(
            Item.title.ilike(like), Item.description.ilike(like), Item.location.ilike(like),
        ))
    status = request.args.get("status", "").strip()
    if status in ("open", "claimed"):
        query = query.filter(Item.status == status)
    category = request.args.get("category", "").strip()
    if category in [c[0] for c in CATEGORIES]:
        query = query.filter(Item.category == category)
    item_type = request.args.get("type", "").strip()
    if item_type in ("lost", "found"):
        query = query.filter(Item.item_type == item_type)
    items = query.order_by(Item.date_reported.desc()).all()
    return jsonify([i.to_dict() for i in items])
