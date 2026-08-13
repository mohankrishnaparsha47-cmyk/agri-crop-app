"""
Smart Farmer Assistant - Flask Backend
========================================
Diploma Final Year Project

Modules:
  - Auth (Register/Login/Logout)
  - Dashboard
  - Crop Suggestions (ML model - RandomForest)
  - Fertilizer Recommendations (dataset lookup)
  - Irrigation Alerts (dataset lookup)
  - Field Records (CRUD)
  - Farmer Subsidy & Schemes  <-- NEW FEATURE
  - Weather (mock/demo - plug in real API key to go live)
"""

import os
import pickle
import functools
from datetime import datetime

import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from database import get_connection, init_db, create_default_admin
from schemes_data import get_all_schemes, check_eligibility, get_scheme_by_id
from market_data import get_market_prices, get_price_trend, get_all_crops as get_market_crops
from translations import t, set_language, current_language
from pest_detection import detect_pest_disease
from profit_calculator import calculate_profit, TYPICAL_YIELD_PER_ACRE
from sms_alerts import send_irrigation_sms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "smart-farmer-assistant-secret-key-change-in-production"

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------------------------------------------------------
# Load datasets & ML model at startup
# ---------------------------------------------------------------
crop_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "crop_recommendation_dataset.csv"))
fert_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "fertilizer_recommendation_dataset.csv"))
irrigation_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "irrigation_schedule_dataset.csv"))
soil_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "india_soil_types_dataset.csv"))
statewise_soil_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "india_statewise_soil_dataset.csv"))
telangana_season_df = pd.read_csv(os.path.join(BASE_DIR, "datasets", "telangana_crop_season_dataset.csv"))

MODEL_PATH = os.path.join(BASE_DIR, "ml_model", "crop_model.pkl")
with open(MODEL_PATH, "rb") as f:
    crop_model = pickle.load(f)

ALL_CROPS = sorted(crop_df["label"].unique().tolist())
ALL_SOILS = sorted(fert_df["Soil_Type"].unique().tolist())
GROWTH_STAGES = irrigation_df["Growth_Stage"].unique().tolist()


# ---------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


def current_user():
    if "user_id" not in session:
        return None
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    conn.close()
    return user


@app.context_processor
def inject_user():
    return {"logged_in_user": current_user(), "t": t, "current_lang": current_language()}


def admin_required(view_func):
    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user["is_admin"]:
            flash("Admin access required.", "danger")
            return redirect(url_for("dashboard"))
        return view_func(*args, **kwargs)
    return wrapper


@app.route("/set-language/<lang_code>")
def set_language_route(lang_code):
    set_language(lang_code)
    return redirect(request.referrer or url_for("dashboard"))


# ---------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        state = request.form.get("state", "").strip()
        district = request.form.get("district", "").strip()
        land_holding = request.form.get("land_holding_acres", "0")
        category = request.form.get("category", "General")

        if not name or not phone or not password:
            flash("Name, phone and password are required.", "danger")
            return redirect(url_for("register"))

        conn = get_connection()
        existing = conn.execute("SELECT id FROM users WHERE phone = ?", (phone,)).fetchone()
        if existing:
            flash("Phone number already registered. Please login.", "danger")
            conn.close()
            return redirect(url_for("login"))

        password_hash = generate_password_hash(password)
        conn.execute(
            """INSERT INTO users (name, phone, password_hash, state, district, land_holding_acres, category)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, phone, password_hash, state, district, float(land_holding or 0), category)
        )
        conn.commit()
        conn.close()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE phone = ?", (phone,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid phone number or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


# ---------------------------------------------------------------
# 1. Crop Suggestions (ML)
# ---------------------------------------------------------------
@app.route("/crop-suggestion", methods=["GET", "POST"])
@login_required
def crop_suggestion():
    prediction = None
    top3 = None
    if request.method == "POST":
        try:
            N = float(request.form["N"])
            P = float(request.form["P"])
            K = float(request.form["K"])
            temperature = float(request.form["temperature"])
            humidity = float(request.form["humidity"])
            ph = float(request.form["ph"])
            rainfall = float(request.form["rainfall"])

            input_df = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]],
                                     columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
            prediction = crop_model.predict(input_df)[0]

            proba = crop_model.predict_proba(input_df)[0]
            classes = crop_model.classes_
            top3_idx = proba.argsort()[-3:][::-1]
            top3 = [(classes[i], round(proba[i] * 100, 1)) for i in top3_idx]

        except Exception as e:
            flash(f"Error processing input: {e}", "danger")

    return render_template("crop_suggestion.html", prediction=prediction, top3=top3)


# ---------------------------------------------------------------
# 2. Fertilizer Recommendations
# ---------------------------------------------------------------
@app.route("/fertilizer", methods=["GET", "POST"])
@login_required
def fertilizer():
    result = None
    if request.method == "POST":
        crop = request.form.get("crop")
        soil = request.form.get("soil")
        matches = fert_df[(fert_df["Crop"] == crop) & (fert_df["Soil_Type"] == soil)]
        if not matches.empty:
            row = matches.iloc[0]
            result = {
                "crop": crop,
                "soil": soil,
                "nitrogen_level": row["Nitrogen_Level"],
                "phosphorus_level": row["Phosphorus_Level"],
                "potassium_level": row["Potassium_Level"],
                "fertilizer": row["Recommended_Fertilizer"],
            }
        else:
            flash("No matching record found for this crop/soil combination.", "warning")

    return render_template("fertilizer.html", crops=ALL_CROPS, soils=ALL_SOILS, result=result)


# ---------------------------------------------------------------
# 3. Irrigation Alerts
# ---------------------------------------------------------------
@app.route("/irrigation", methods=["GET", "POST"])
@login_required
def irrigation():
    schedule = None
    sms_result = None
    if request.method == "POST":
        crop = request.form.get("crop")
        send_sms = request.form.get("send_sms") == "on"
        matches = irrigation_df[irrigation_df["Crop"] == crop]
        if not matches.empty:
            schedule = matches.to_dict(orient="records")
            if send_sms:
                user = current_user()
                first_stage = schedule[0]
                sms_result = send_irrigation_sms(
                    user["phone"], crop, first_stage["Growth_Stage"], first_stage["Water_Requirement_mm"]
                )
                if sms_result.get("demo"):
                    flash("SMS demo mode: Twilio not configured, alert logged to console only.", "info")
                elif sms_result.get("sent"):
                    flash("Irrigation SMS alert sent to your phone!", "success")
                else:
                    flash("Could not send SMS alert. Check Twilio configuration.", "danger")
        else:
            flash("No irrigation data found for this crop.", "warning")

    return render_template("irrigation.html", crops=ALL_CROPS, schedule=schedule)


# ---------------------------------------------------------------
# 4. Field Records (CRUD)
# ---------------------------------------------------------------
@app.route("/field-records", methods=["GET", "POST"])
@login_required
def field_records():
    conn = get_connection()
    if request.method == "POST":
        crop_name = request.form.get("crop_name")
        activity = request.form.get("activity")
        notes = request.form.get("notes", "")
        activity_date = request.form.get("activity_date")

        conn.execute(
            """INSERT INTO field_records (user_id, crop_name, activity, notes, activity_date)
               VALUES (?, ?, ?, ?, ?)""",
            (session["user_id"], crop_name, activity, notes, activity_date)
        )
        conn.commit()
        flash("Field record added.", "success")

    records = conn.execute(
        "SELECT * FROM field_records WHERE user_id = ? ORDER BY activity_date DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("field_records.html", records=records, crops=ALL_CROPS)


@app.route("/field-records/delete/<int:record_id>")
@login_required
def delete_field_record(record_id):
    conn = get_connection()
    conn.execute("DELETE FROM field_records WHERE id = ? AND user_id = ?", (record_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Record deleted.", "info")
    return redirect(url_for("field_records"))


# ---------------------------------------------------------------
# 5. FARMER SUBSIDY & SCHEMES  (NEW FEATURE)
# ---------------------------------------------------------------
@app.route("/schemes")
@login_required
def schemes():
    all_schemes = get_all_schemes()
    return render_template("schemes.html", schemes=all_schemes)


@app.route("/schemes/check-eligibility", methods=["GET", "POST"])
@login_required
def check_scheme_eligibility():
    eligible_schemes = None
    user = current_user()

    if request.method == "POST":
        land_holding = float(request.form.get("land_holding_acres", 0) or 0)
        category = request.form.get("category", "General")
        state = request.form.get("state", "")
        age = request.form.get("age")
        age = int(age) if age else None

        eligible_schemes = check_eligibility(
            land_holding_acres=land_holding,
            category=category,
            state=state,
            age=age
        )

    return render_template(
        "scheme_eligibility.html",
        eligible_schemes=eligible_schemes,
        user=user
    )


@app.route("/schemes/apply/<scheme_id>", methods=["POST"])
@login_required
def apply_scheme(scheme_id):
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        flash("Scheme not found.", "danger")
        return redirect(url_for("schemes"))

    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM scheme_applications WHERE user_id = ? AND scheme_name = ?",
        (session["user_id"], scheme["name"])
    ).fetchone()

    if existing:
        flash(f"You have already applied for {scheme['name']}.", "info")
    else:
        conn.execute(
            "INSERT INTO scheme_applications (user_id, scheme_name, status) VALUES (?, ?, 'Applied')",
            (session["user_id"], scheme["name"])
        )
        conn.commit()
        flash(f"Applied for {scheme['name']} successfully! Track status in 'My Applications'.", "success")

    conn.close()
    return redirect(url_for("my_applications"))


@app.route("/schemes/my-applications")
@login_required
def my_applications():
    conn = get_connection()
    applications = conn.execute(
        "SELECT * FROM scheme_applications WHERE user_id = ? ORDER BY applied_on DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("my_applications.html", applications=applications)


# ---------------------------------------------------------------
# 6. Weather (demo/mock - replace with real API call using your API key)
# ---------------------------------------------------------------
@app.route("/weather")
@login_required
def weather():
    # Set OPENWEATHER_API_KEY as an environment variable to go live.
    # Falls back to demo data automatically if no key is set or API call fails.
    api_key = os.environ.get("OPENWEATHER_API_KEY", "")
    user = current_user()
    city = (user["district"] if user and user["district"] else "Hyderabad")

    weather_data = None
    if api_key:
        try:
            import requests
            resp = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": f"{city},IN", "appid": api_key, "units": "metric"},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                weather_data = {
                    "location": f"{data['name']}, India",
                    "temperature": round(data["main"]["temp"]),
                    "condition": data["weather"][0]["description"].title(),
                    "humidity": data["main"]["humidity"],
                    "rainfall_chance": "N/A",
                    "wind_speed": f"{data['wind']['speed']} m/s",
                    "forecast": []  # Extend using the 5-day forecast endpoint if needed
                }
        except Exception:
            weather_data = None  # fall through to demo data below

    if not weather_data:
        # DEMO DATA (used when no API key configured or API call fails)
        weather_data = {
            "location": f"{city}, Telangana",
            "temperature": 31,
            "condition": "Partly Cloudy",
            "humidity": 68,
            "rainfall_chance": "20%",
            "wind_speed": "12 km/h",
            "forecast": [
                {"day": "Today", "temp": 31, "condition": "Partly Cloudy"},
                {"day": "Tomorrow", "temp": 29, "condition": "Light Rain"},
                {"day": "Day 3", "temp": 30, "condition": "Sunny"},
            ]
        }
    return render_template("weather.html", weather=weather_data, is_live=bool(api_key))


# ---------------------------------------------------------------
# Soil info page (uses india_soil_types dataset)
# ---------------------------------------------------------------
@app.route("/soil-info")
@login_required
def soil_info():
    soils = soil_df.to_dict(orient="records")
    return render_template("soil_info.html", soils=soils)


# ---------------------------------------------------------------
# 7. MARKET / MANDI PRICE CHECKER (NEW FEATURE)
# ---------------------------------------------------------------
@app.route("/market-prices", methods=["GET", "POST"])
@login_required
def market_prices():
    prices = None
    trend = None
    selected_crop = None
    if request.method == "POST":
        selected_crop = request.form.get("crop")
        prices = get_market_prices(selected_crop)
        trend = get_price_trend(selected_crop)
        if not prices:
            flash("No market data found for this crop.", "warning")

    return render_template(
        "market_prices.html",
        crops=get_market_crops(),
        prices=prices,
        trend=trend,
        selected_crop=selected_crop
    )


# ---------------------------------------------------------------
# 8. CROP PROFIT CALCULATOR (NEW FEATURE)
# ---------------------------------------------------------------
@app.route("/profit-calculator", methods=["GET", "POST"])
@login_required
def profit_calculator_route():
    result = None
    if request.method == "POST":
        try:
            crop = request.form.get("crop")
            land_acres = float(request.form.get("land_acres", 1))
            investment_per_acre = float(request.form.get("investment_per_acre", 0))
            market_price = float(request.form.get("market_price", 0))
            custom_yield = request.form.get("custom_yield")
            custom_yield = float(custom_yield) if custom_yield else None

            result = calculate_profit(crop, land_acres, investment_per_acre, market_price, custom_yield)
        except Exception as e:
            flash(f"Error calculating profit: {e}", "danger")

    return render_template(
        "profit_calculator.html",
        crops=sorted(TYPICAL_YIELD_PER_ACRE.keys()),
        result=result
    )


# ---------------------------------------------------------------
# 9. PEST & DISEASE DETECTION (NEW FEATURE - demo classifier)
# ---------------------------------------------------------------
@app.route("/pest-detection", methods=["GET", "POST"])
@login_required
def pest_detection_route():
    result = None
    uploaded_image_url = None

    if request.method == "POST":
        file = request.files.get("leaf_image")
        if file and file.filename:
            filename = secure_filename(file.filename)
            unique_name = f"{session['user_id']}_{int(datetime.now().timestamp())}_{filename}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            file.save(save_path)

            result = detect_pest_disease(save_path)
            uploaded_image_url = url_for("static", filename=f"uploads/{unique_name}")
        else:
            flash("Please upload a leaf image.", "warning")

    return render_template("pest_detection.html", result=result, uploaded_image_url=uploaded_image_url)


# ---------------------------------------------------------------
# 10. ADMIN DASHBOARD (NEW FEATURE)
# ---------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_connection()
    total_users = conn.execute("SELECT COUNT(*) c FROM users WHERE is_admin = 0").fetchone()["c"]
    total_records = conn.execute("SELECT COUNT(*) c FROM field_records").fetchone()["c"]
    total_applications = conn.execute("SELECT COUNT(*) c FROM scheme_applications").fetchone()["c"]

    recent_users = conn.execute(
        "SELECT * FROM users WHERE is_admin = 0 ORDER BY created_at DESC LIMIT 10"
    ).fetchall()

    applications = conn.execute("""
        SELECT sa.*, u.name as user_name, u.phone as user_phone
        FROM scheme_applications sa
        JOIN users u ON sa.user_id = u.id
        ORDER BY sa.applied_on DESC
        LIMIT 20
    """).fetchall()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_records=total_records,
        total_applications=total_applications,
        recent_users=recent_users,
        applications=applications
    )


@app.route("/admin/application/<int:app_id>/update-status", methods=["POST"])
@admin_required
def update_application_status(app_id):
    new_status = request.form.get("status")
    conn = get_connection()
    conn.execute("UPDATE scheme_applications SET status = ? WHERE id = ?", (new_status, app_id))
    conn.commit()
    conn.close()
    flash("Application status updated.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    if not os.path.exists(os.path.join(BASE_DIR, "farmer_assistant.db")):
        init_db()
        create_default_admin()
    app.run(debug=True, host="0.0.0.0", port=5000)
