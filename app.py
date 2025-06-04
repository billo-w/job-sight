from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
from loguru import logger
import json
from sqlalchemy import create_engine, text
from logtail import LogtailHandler
import logging

ADZUNA_ID        = os.getenv('ADZUNA_ID')
ADZUNA_KEY       = os.getenv('ADZUNA_KEY')
FOUNDRY_ENDPOINT = os.getenv('FOUNDRY_ENDPOINT')
FOUNDRY_KEY      = os.getenv('FOUNDRY_KEY')
GRAFANA_PUSH_URL = os.getenv('GRAFANA_PUSHGATEWAY_URL')
GRAFANA_API_KEY  = os.getenv('GRAFANA_API_KEY')

DB_URL = os.getenv('DATABASE_URL', 'postgresql://dev:devpass@db:5432/jobsight')
engine = create_engine(DB_URL)

logger.add("app.log", rotation="1 MB", level="INFO", backtrace=True, diagnose=True)

handler = LogtailHandler(source_token=os.getenv("LOGTAIL_SOURCE_TOKEN"))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
load_dotenv()

logger.info("Flask app has started")

app = Flask(__name__)

@app.before_request
def log_request():
    logger.info(f"Incoming {request.method} request to {request.path} from {request.remote_addr}")

# Log a sample route
@app.route('/')
def home():
    logger.info("Home page accessed")
    return "Hello, world!"

# Log errors
@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal Server Error: {str(e)}")
    return "Something went wrong", 500

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    insights = {}
    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        logger.info("Received search request: title=%s, location=%s", title, location)
        jobs = fetch_jobs(title, location)
        insights = analyze_market(jobs)
        

    return render_template('index.html', jobs=jobs, insights=insights)

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode)

def save_jobs(jobs):
    with engine.connect() as conn:
        for job in jobs:
            conn.execute(text(
                "INSERT INTO jobs (title, company, location) VALUES (:title, :company, :location)"
            ), **{ 'title': job.get('title'), 'company': job.get('company', ''), 'location': job.get('location', '') })

def fetch_jobs(keyword, location='gb'):
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
        params = {
            'app_id': ADZUNA_ID,
            'app_key': ADZUNA_KEY,
            'what': keyword,
            'results_per_page': 10,
        }
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        logger.info("Fetched %d jobs for '%s' in %s", len(data.get('results', [])), keyword, location)
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Adzuna API call failed: {e}")
        return []

def analyze_market(jobs):
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
