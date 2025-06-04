from app import app, fetch_jobs, analyze_market
import os
import pytest
import json
import requests
from app import app, fetch_jobs, analyze_market

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv('ADZUNA_ID', 'dummy_id')
    monkeypatch.setenv('ADZUNA_KEY', 'dummy_key')

class DummyResponse:
    def raise_for_status(self): pass
    def json(self): return {'results': [{'title': 'DevOps Engineer', 'location':'London'}]}

@pytest.fixture
def mock_requests(monkeypatch):
    monkeypatch.setattr('app.requests.get', lambda *args, **kwargs: DummyResponse())

def test_fetch_jobs(mock_requests):
    jobs = fetch_jobs('devops', 'gb')
    assert isinstance(jobs, list)
    assert jobs[0]['title'] == 'DevOps Engineer'

def test_analyze_market():
    insights = analyze_market([{'title':'a'}])
    assert 'trend' in insights and 'average_salary' in insights

def test_homepage():
    client = app.test_client()
    res = client.get('/')
    assert res.status_code == 200

class DummyPostResponse:
    def raise_for_status(self): pass
    def json(self): return {'trend': 'test trend', 'average_salary': '£100'}

@pytest.fixture
def mock_post(monkeypatch):
    monkeypatch.setattr('app.requests.post', lambda *args, **kwargs: DummyPostResponse())

def test_analyze_market_real(mock_post):
    insights = analyze_market([{'title':'devops'}])
    assert insights['trend'] == 'test trend'
    assert insights['average_salary'] == '£100'

def test_fetch_jobs_error(monkeypatch):
    class ErrResp:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("404 Not Found")
    monkeypatch.setattr('app.requests.get', lambda *args, **kwargs: ErrResp())
    jobs = fetch_jobs('devops', 'gb')
    assert jobs == []

def test_fetch_jobs_parsing(monkeypatch):
    class Resp:
        def raise_for_status(self): pass
        def json(self): return {'results': [{'title': 'Test', 'location': 'X'}]}
    monkeypatch.setattr('app.requests.get', lambda *args, **kwargs: Resp())
    jobs = fetch_jobs('x', 'y')
    assert jobs[0]['location'] == 'X'

def test_analyze_market_error(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("timeout")
    monkeypatch.setattr('app.requests.post', raise_timeout)
    insights = analyze_market([{'title':'a'}])
    assert insights['trend'] == 'N/A'