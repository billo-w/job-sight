from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import os
import requests
from loguru import logger
import json
from sqlalchemy import create_engine, text
from logtail import LogtailHandler
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

ADZUNA_ID        = os.getenv('ADZUNA_ID')
ADZUNA_KEY       = os.getenv('ADZUNA_KEY')
FOUNDRY_ENDPOINT = os.getenv('FOUNDRY_ENDPOINT')
FOUNDRY_KEY      = os.getenv('FOUNDRY_KEY')
# GRAFANA_PUSH_URL and GRAFANA_API_KEY removed entirely

DB_URL = os.getenv('DATABASE_URL', 'postgresql://dev:devpass@db:5432/jobsight')

# Set up Flask and SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-to-a-random-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Logging setup (Loguru + Logtail)
logger.add("app.log", rotation="1 MB", level="INFO", backtrace=True, diagnose=True)
handler = LogtailHandler(source_token=os.getenv("LOGTAIL_SOURCE_TOKEN"))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.info("Flask app has started")

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# -------------------------
# Database Models
# -------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title       = db.Column(db.String(256), nullable=False)
    company     = db.Column(db.String(256))
    location    = db.Column(db.String(256))
    description = db.Column(db.Text)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------
# Request Logging & Security
# -------------------------
@app.before_request
def log_request():
    logger.info(f"Incoming {request.method} request to {request.path} from {request.remote_addr}")

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal Server Error: {str(e)}")
    return "Something went wrong", 500

# -------------------------
# Home / Search Route
# -------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    insights = {}
    if request.method == 'POST':
        title        = request.form.get('title')
        location     = request.form.get('location')
        country_code = request.form.get('country_code')
        logger.info("Received search: title=%s, location=%s, country_code=%s", title, location, country_code)
        jobs = fetch_jobs(title, location, country_code)
        insights = analyze_market(jobs)

    return render_template('index.html', jobs=jobs, insights=insights)

# -------------------------
# Register / Login / Logout
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email').lower().strip()
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            logger.warning("Registration attempt with existing email: %s", email)
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user  = User(email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        logger.info("New user registered: %s", email)
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email').lower().strip()
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            logger.info("User logged in: %s", email)
            flash("Logged in successfully.", "success")
            return redirect(url_for('index'))
        else:
            logger.warning("Failed login attempt: %s", email)
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logger.info("User logged out: %s", current_user.email)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# -------------------------
# Save Job Route
# -------------------------
@app.route('/save_job', methods=['POST'])
@login_required
def save_job():
    job_title    = request.form.get('job_title')
    job_company  = request.form.get('job_company')
    job_loc      = request.form.get('job_location')
    job_desc     = request.form.get('job_description')

    existing = SavedJob.query.filter_by(
        user_id=current_user.id,
        title=job_title,
        company=job_company,
        location=job_loc
    ).first()

    if existing:
        flash("You have already saved this job.", "info")
        logger.info("User %s attempted to save a job already saved: %s at %s", current_user.email, job_title, job_loc)
    else:
        new_saved = SavedJob(
            user_id=current_user.id,
            title=job_title,
            company=job_company,
            location=job_loc,
            description=job_desc
        )
        db.session.add(new_saved)
        db.session.commit()
        flash("Job saved successfully!", "success")
        logger.info("User %s saved job: %s at %s", current_user.email, job_title, job_loc)

    return redirect(url_for('index'))

# -------------------------
# Utility Functions
# -------------------------
def fetch_jobs(keyword, location, country_code='gb'):
    """
    Query Adzuna’s API with:
      - base URL: country_code
      - params: what=keyword, where=location
    """
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
        params = {
            'app_id': ADZUNA_ID,
            'app_key': ADZUNA_KEY,
            'what': keyword,
            'where': location,
            'results_per_page': 10,
        }
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results', [])
        logger.info("Fetched %d jobs for '%s' in '%s' (%s)", len(results), keyword, location, country_code)
        return results
    except requests.exceptions.RequestException as e:
        logger.error(f"Adzuna API call failed: {e}")
        return []

def analyze_market(jobs):
    """
    Send the list of jobs to Azure Foundry for insight analysis.
    """
    try:
        payload = { 'jobs': jobs }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {FOUNDRY_KEY}"
        }
        resp = requests.post(
            FOUNDRY_ENDPOINT,
            headers=headers,
            data=json.dumps(payload),
            timeout=10
        )
        resp.raise_for_status()
        insights = resp.json()
        logger.info(f"Azure Foundry insights received: {insights}")
        return insights
    except requests.exceptions.RequestException as e:
        logger.error(f"Azure Foundry API call failed: {e}")
        return {'trend': 'N/A', 'average_salary': 'N/A'}

# -------------------------
# Run App
# -------------------------
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
