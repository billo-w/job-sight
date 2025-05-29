# Job Sight

A simple Flask-based job insights dashboard that allows users to search for jobs and view AI-powered analysis of job listings. Data is pulled from the Adzuna API and analyzed using Azure Foundry AI.

## Features
- Job search by title/location
- AI summary and analysis of job data
- CI/CD pipeline
- Terraform IaC

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
pytest

#### Must Have:
```markdown
As a job seeker,
I want to search for jobs by title and location,
So that I can view relevant job listings.

AC1: The user can enter a job title and location.
AC2: Job listings are fetched using the Adzuna API.
AC3: Listings appear on the same page.
AC4: AI analysis appears below the listings.