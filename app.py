"""
app.py — Flask entry point and route handlers for Campus Findr.

Handles page rendering, form submissions, image uploads, claim/resolve
workflow, admin deletion, and the JSON search API.
"""

import os
import uuid
from datetime import date

from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, abort,
)
from PIL import Image
from werkzeug.utils import secure_filename

from database import db, init_db, seed_db
from models import Item, CATEGORIES

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
IS_VERCEL = os.environ.get("VERCEL", False)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "campus-findr-dev-secret-key")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if IS_VERCEL:
    # Vercel serverless: only /tmp is writable
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/campus_findr.db"
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "campus_findr.db")
    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
THUMBNAIL_SIZE = (300, 300)

db.init_app(app)

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ---------------------------------------------------------------------------
# Template Context — make CATEGORIES available in all templates
# ---------------------------------------------------------------------------
@app.context_processor
def inject_categories():
    return dict(categories=CATEGORIES)


# ---------------------------------------------------------------------------
# Image Upload Helpers
# ---------------------------------------------------------------------------
def allowed_file(filename):
    """Check if the file extension is allowed (JPEG/PNG)."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_photo(file):
    """
    Save an uploaded photo and generate a thumbnail.

    Returns:
        tuple: (original_filename, thumbnail_filename) or (None, None).
    """
    if file and file.filename and allowed_file(file.filename):
        # Create a unique filename to avoid collisions
        ext = file.filename.rsplit(".", 1)[1].lower()
        unique_id = uuid.uuid4().hex[:10]
        safe_name = secure_filename(file.filename)
        original_name = f"{unique_id}_{safe_name}"
        thumb_name = f"thumb_{original_name}"

        original_path = os.path.join(app.config["UPLOAD_FOLDER"], original_name)
        thumb_path = os.path.join(app.config["UPLOAD_FOLDER"], thumb_name)

        # Save the original file
        file.save(original_path)

        # Generate thumbnail with Pillow
        try:
            with Image.open(original_path) as img:
                img.thumbnail(THUMBNAIL_SIZE)
                img.save(thumb_path)
        except Exception:
            # If thumbnail generation fails, still keep the original
            thumb_name = None

        return original_name, thumb_name

    return None, None


def delete_photo(filename):
    """Delete a photo file from the uploads directory if it exists."""
    if filename:
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(path):
            os.remove(path)


# ---------------------------------------------------------------------------
# Page Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Home page — item feed with all open items, newest first."""
    items = Item.query.order_by(Item.date_reported.desc()).all()
    return render_template("index.html", items=items)


@app.route("/report", methods=["GET", "POST"])
def report():
    """Report a lost or found item."""
    if request.method == "GET":
        return render_template("report.html")

    # --- Handle POST: create new item ---
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "")
    description = request.form.get("description", "").strip()
    item_type = request.form.get("item_type", "lost")
    date_occurred_str = request.form.get("date_occurred", "")
    location = request.form.get("location", "").strip()
    deposit_location = request.form.get("deposit_location", "").strip() or None
    contact_email = request.form.get("contact_email", "").strip()

    # Basic server-side validation
    if not all([title, category, description, date_occurred_str, location, contact_email]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("report"))

    try:
        date_occurred = date.fromisoformat(date_occurred_str)
    except ValueError:
        flash("Invalid date format.", "error")
        return redirect(url_for("report"))

    # Handle optional photo upload
    photo_filename, thumbnail_filename = None, None
    if "photo" in request.files:
        photo_filename, thumbnail_filename = save_photo(request.files["photo"])

    new_item = Item(
        title=title,
        category=category,
        description=description,
        item_type=item_type,
        date_occurred=date_occurred,
        location=location,
        deposit_location=deposit_location,
        contact_email=contact_email,
        photo_filename=photo_filename,
        thumbnail_filename=thumbnail_filename,
    )

    db.session.add(new_item)
    db.session.commit()
    flash("Item reported successfully! 🎉", "success")
    return redirect(url_for("index"))


@app.route("/item/<int:item_id>")
def item_detail(item_id):
    """View a single item's details."""
    item = Item.query.get_or_404(item_id)
    return render_template("item_detail.html", item=item)


@app.route("/item/<int:item_id>/claim", methods=["POST"])
def claim_item(item_id):
    """Submit a claim with a verification detail."""
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

    flash("Claim submitted! The reporter will verify your details. 🔍", "success")
    return redirect(url_for("item_detail", item_id=item_id))


@app.route("/item/<int:item_id>/resolve", methods=["POST"])
def resolve_item(item_id):
    """Mark the item as claimed/resolved."""
    item = Item.query.get_or_404(item_id)
    item.status = "claimed"
    db.session.commit()
    flash("Item marked as claimed/resolved. ✅", "success")
    return redirect(url_for("item_detail", item_id=item_id))


@app.route("/admin/delete/<int:item_id>", methods=["POST"])
def admin_delete(item_id):
    """Delete an item (admin/moderator clean-up)."""
    item = Item.query.get_or_404(item_id)

    # Clean up associated photo files
    delete_photo(item.photo_filename)
    delete_photo(item.thumbnail_filename)

    db.session.delete(item)
    db.session.commit()
    flash("Item deleted successfully.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# JSON API — Search & Filter
# ---------------------------------------------------------------------------
@app.route("/api/items")
def api_items():
    """
    Return a JSON list of items, filtered by query parameters.

    Query params:
        q        — keyword search (matches title, description, location)
        status   — "open" or "claimed"
        category — one of the CATEGORIES keys
        type     — "lost" or "found"
    """
    query = Item.query

    # Keyword search
    q = request.args.get("q", "").strip()
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(
            db.or_(
                Item.title.ilike(like_pattern),
                Item.description.ilike(like_pattern),
                Item.location.ilike(like_pattern),
            )
        )

    # Status filter
    status = request.args.get("status", "").strip()
    if status in ("open", "claimed"):
        query = query.filter(Item.status == status)

    # Category filter
    category = request.args.get("category", "").strip()
    valid_categories = [c[0] for c in CATEGORIES]
    if category in valid_categories:
        query = query.filter(Item.category == category)

    # Type filter (lost / found)
    item_type = request.args.get("type", "").strip()
    if item_type in ("lost", "found"):
        query = query.filter(Item.item_type == item_type)

    items = query.order_by(Item.date_reported.desc()).all()
    return jsonify([item.to_dict() for item in items])


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

# Auto-init DB + seed (works both locally and on Vercel import)
init_db(app)
seed_db(app)

if __name__ == "__main__":
    import socket
    # Get the machine's LAN IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print(">>> Campus Findr is running!")
    print(f"    Local:   http://127.0.0.1:5000")
    print(f"    Network: http://{local_ip}:5000  (share this with your campus)")
    app.run(host="0.0.0.0", port=5000, debug=True)
