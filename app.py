from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
from loguru import logger
import json
from sqlalchemy import create_engine, text
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter('app_request_count', 'Total HTTP requests', ['method','endpoint'])

logger.add("app.log", rotation="1 MB", level="INFO", backtrace=True, diagnose=True)

load_dotenv()

app = Flask(__name__)

DB_URL = os.getenv('DATABASE_URL', 'postgresql://dev:devpass@db:5432/jobsight')
engine = create_engine(DB_URL)

ADZUNA_ID = os.getenv('ADZUNA_ID')
ADZUNA_KEY = os.getenv('ADZUNA_KEY')
FOUNDRY_ENDPOINT = os.getenv('FOUNDRY_ENDPOINT')
FOUNDRY_KEY = os.getenv('FOUNDRY_KEY')

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.before_request
def before_request():
    REQUEST_COUNT.labels(request.method, request.path).inc()

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    insights = {}
    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        logger.info("Received search request: title=%s, location=%s", title, location)
        jobs = fetch_jobs(title, location)
        if jobs:
            insights = analyze_market(jobs)
        else:
            insights = { 'trend': 'No data', 'average_salary': 'No data' }
    return render_template('index.html', jobs=jobs, insights=insights)

if __name__ == '__main__':
    app.run(debug=True)

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
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        logger.info("Fetched %d jobs for '%s' in %s", len(data.get('results', [])), keyword, location)
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        logger.error("Adzuna API call failed: {}", e)
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
        logger.info("Azure Foundry insights received: {}", insights)
        return insights
   
    except requests.exceptions.RequestException as e:
        logger.error("Azure Foundry API call failed: {}", e)
        return { 'trend': 'N/A', 'average_salary': 'N/A' }