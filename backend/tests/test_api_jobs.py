import threading

from sqlalchemy.orm import sessionmaker

from app.models import Company
from app.routers.jobs import _get_or_create_company


def test_create_job_creates_new_company(client, db_session):
    response = client.post(
        "/jobs", json={"company_name": "Brand New Co", "title": "Engineer", "location": "Remote"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Engineer"
    assert body["location"] == "Remote"
    assert body["company_name"] == "Brand New Co"

    companies = db_session.query(Company).filter(Company.name == "Brand New Co").all()
    assert len(companies) == 1


def test_create_job_reuses_existing_company(client, db_session):
    company = Company(name="Existing Co")
    db_session.add(company)
    db_session.commit()

    response = client.post("/jobs", json={"company_name": "Existing Co", "title": "Role"})

    assert response.status_code == 201
    assert response.json()["company_id"] == company.company_id
    assert db_session.query(Company).filter(Company.name == "Existing Co").count() == 1


def test_create_job_company_match_is_case_and_whitespace_insensitive(client, db_session):
    company = Company(name="Acme Corp")
    db_session.add(company)
    db_session.commit()

    response = client.post("/jobs", json={"company_name": "  acme CORP  ", "title": "Role"})

    assert response.status_code == 201
    assert response.json()["company_id"] == company.company_id
    assert db_session.query(Company).count() == 1


def test_get_or_create_company_concurrent_same_name_no_duplicate(test_engine, db_session):
    barrier = threading.Barrier(2)
    company_ids = []
    errors = []

    def worker():
        session_factory = sessionmaker(bind=test_engine)
        session = session_factory()
        try:
            barrier.wait()
            company = _get_or_create_company(session, "Concurrent Co")
            session.commit()
            company_ids.append(company.company_id)
        except Exception as exc:  # noqa: BLE001 - surfaced via assertion below, not silently swallowed
            errors.append(exc)
        finally:
            session.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    assert len(company_ids) == 2
    assert company_ids[0] == company_ids[1]


# --- GET /jobs/{id} ---


def test_get_job_returns_job_with_company_name(client, db_session):
    created = client.post(
        "/jobs", json={"company_name": "Acme Corp", "title": "Engineer", "description": "Build things"}
    ).json()

    response = client.get(f"/jobs/{created['job_id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Engineer"
    assert body["description"] == "Build things"
    assert body["company_name"] == "Acme Corp"


def test_get_job_unknown_id_returns_404(client):
    response = client.get("/jobs/999999")

    assert response.status_code == 404
