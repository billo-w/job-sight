from app import app, fetch_jobs, analyze_market
import os
import pytest

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