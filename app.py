from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import requests
from loguru import logger

load_dotenv()

app = Flask(__name__)

ADZUNA_ID = os.getenv('ADZUNA_ID')
ADZUNA_KEY = os.getenv('ADZUNA_KEY')
FOUNDRY_ENDPOINT = os.getenv('FOUNDRY_ENDPOINT')
FOUNDRY_KEY = os.getenv('FOUNDRY_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    insights = {}
    if request.method == 'POST':
        title = request.form.get('title')
        location = request.form.get('location')
        jobs = fetch_jobs(title, location)
        insights = analyze_market(jobs)
    return render_template('index.html', jobs=jobs, insights=insights)

if __name__ == '__main__':
    app.run(debug=True)

def fetch_jobs(keyword, location='gb'):
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
    return data.get('results', [])

def analyze_market(jobs):
    return {
        'trend': 'Rising demand for roles requiring Python & DevOps skills',
        'average_salary': '£50k–£60k',
    }