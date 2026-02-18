"""Tests for phoenix_lib.schemas.watcher (inter-service contract DTOs)."""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from phoenix_lib.schemas.watcher import (JobAlertCreate, JobAlertUpdate,
                                         JobListingResponse, JobMatchResponse,
                                         JobMatchWithListing,
                                         LinkedInCookieCreate,
                                         MarkNotifiedRequest,
                                         ProcessAlertRequest,
                                         ProcessAlertResponse)


class TestJobAlertCreate:
    def test_minimal_with_string_keywords(self):
        obj = JobAlertCreate(keywords="python developer")
        assert obj.keywords == "python developer"

    def test_keywords_as_list(self):
        obj = JobAlertCreate(keywords=["python", "django"])
        assert obj.keywords == ["python", "django"]

    def test_default_check_interval(self):
        obj = JobAlertCreate(keywords="test")
        assert obj.check_interval_minutes == 5

    def test_all_fields(self):
        obj = JobAlertCreate(
            alert_name="My Alert",
            keywords=["python"],
            sources=["linkedin"],
            location="Remote",
            check_interval_minutes=15,
            filters={"experience_level": "senior"},
        )
        assert obj.alert_name == "My Alert"
        assert obj.sources == ["linkedin"]
        assert obj.location == "Remote"
        assert obj.filters["experience_level"] == "senior"

    def test_optional_fields_default_none(self):
        obj = JobAlertCreate(keywords="test")
        assert obj.alert_name is None
        assert obj.sources is None
        assert obj.location is None
        assert obj.filters is None


class TestJobAlertUpdate:
    def test_all_optional(self):
        obj = JobAlertUpdate()
        assert obj.alert_name is None
        assert obj.keywords is None
        assert obj.is_active is None

    def test_partial_update(self):
        obj = JobAlertUpdate(is_active=False, check_interval_minutes=30)
        assert obj.is_active is False
        assert obj.check_interval_minutes == 30

    def test_keywords_as_list_in_update(self):
        obj = JobAlertUpdate(keywords=["java", "spring"])
        assert obj.keywords == ["java", "spring"]


class TestLinkedInCookieCreate:
    def test_required_li_at(self):
        obj = LinkedInCookieCreate(li_at="abc123")
        assert obj.li_at == "abc123"

    def test_missing_li_at_raises(self):
        with pytest.raises(ValidationError):
            LinkedInCookieCreate()

    def test_optional_fields(self):
        obj = LinkedInCookieCreate(li_at="token", jsession_id="sess")
        assert obj.jsession_id == "sess"
        assert obj.additional_cookies is None

    def test_additional_cookies_dict(self):
        obj = LinkedInCookieCreate(
            li_at="token",
            additional_cookies={"lang": "en-us"},
        )
        assert obj.additional_cookies["lang"] == "en-us"


class TestJobListingResponse:
    def _make(self, **kwargs):
        now = datetime.now(timezone.utc)
        defaults = {
            "id": uuid.uuid4(),
            "external_id": "ext-001",
            "source": "linkedin",
            "source_job_id": "job-001",
            "url": "https://linkedin.com/jobs/1",
            "title": "Software Engineer",
            "company": "Acme Corp",
            "location": "Remote",
            "description": "Great job",
            "snippet": "snippet",
            "posted_at": now,
            "salary_min": None,
            "salary_max": None,
            "salary_currency": None,
            "employment_type": "full-time",
            "remote_type": "remote",
            "content_hash": "abc123",
            "first_seen_at": now,
            "last_seen_at": now,
            "created_at": now,
        }
        defaults.update(kwargs)
        return JobListingResponse(**defaults)

    def test_valid_creation(self):
        obj = self._make()
        assert obj.title == "Software Engineer"

    def test_optional_fields_none(self):
        obj = self._make(company=None, location=None, description=None)
        assert obj.company is None

    def test_embedding_model_optional(self):
        obj = self._make(embedding_model="text-embedding-3-small")
        assert obj.embedding_model == "text-embedding-3-small"

    def test_uuid_id_field(self):
        uid = uuid.uuid4()
        obj = self._make(id=uid)
        assert obj.id == uid


class TestJobMatchResponse:
    def _make(self, **kwargs):
        now = datetime.now(timezone.utc)
        defaults = {
            "id": uuid.uuid4(),
            "job_alert_id": uuid.uuid4(),
            "job_listing_id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "relevance_score": 85,
            "key_strengths": ["Python", "FastAPI"],
            "potential_concerns": [],
            "strategic_value": "High",
            "recommended_action": "Apply",
            "reasoning": "Strong match",
            "is_notified": False,
            "created_at": now,
        }
        defaults.update(kwargs)
        return JobMatchResponse(**defaults)

    def test_valid_creation(self):
        obj = self._make()
        assert obj.relevance_score == 85

    def test_key_strengths_list(self):
        obj = self._make(key_strengths=["Skill A", "Skill B"])
        assert len(obj.key_strengths) == 2

    def test_optional_fields_none(self):
        obj = self._make(strategic_value=None, recommended_action=None, reasoning=None)
        assert obj.strategic_value is None


class TestJobMatchWithListing:
    def test_inherits_from_job_match_response(self):
        assert issubclass(JobMatchWithListing, JobMatchResponse)

    def test_includes_job_listing(self):
        now = datetime.now(timezone.utc)
        listing = JobListingResponse(
            id=uuid.uuid4(),
            external_id="ext-1",
            source="linkedin",
            source_job_id="job-1",
            url="https://example.com",
            title="Dev",
            company=None,
            location=None,
            description=None,
            snippet=None,
            posted_at=None,
            salary_min=None,
            salary_max=None,
            salary_currency=None,
            employment_type=None,
            remote_type=None,
            content_hash="hash",
            first_seen_at=now,
            last_seen_at=now,
            created_at=now,
        )
        match = JobMatchWithListing(
            id=uuid.uuid4(),
            job_alert_id=uuid.uuid4(),
            job_listing_id=listing.id,
            user_id=uuid.uuid4(),
            relevance_score=90,
            key_strengths=["Python"],
            potential_concerns=[],
            strategic_value=None,
            recommended_action=None,
            reasoning=None,
            is_notified=False,
            created_at=now,
            job_listing=listing,
        )
        assert match.job_listing.title == "Dev"


class TestProcessAlertRequest:
    def test_requires_alert_id(self):
        with pytest.raises(ValidationError):
            ProcessAlertRequest()

    def test_default_min_relevance(self):
        obj = ProcessAlertRequest(alert_id=uuid.uuid4())
        assert obj.min_relevance_score == 60

    def test_custom_min_relevance(self):
        obj = ProcessAlertRequest(alert_id=uuid.uuid4(), min_relevance_score=75)
        assert obj.min_relevance_score == 75


class TestProcessAlertResponse:
    def test_all_fields(self):
        obj = ProcessAlertResponse(
            alert_id="alert-123",
            alert_name="My Alert",
            scraped_jobs=10,
            new_jobs=5,
            matches=3,
            notifications_sent=2,
            errors=[],
        )
        assert obj.scraped_jobs == 10
        assert obj.matches == 3
        assert obj.errors == []


class TestMarkNotifiedRequest:
    def test_requires_match_id(self):
        with pytest.raises(ValidationError):
            MarkNotifiedRequest()

    def test_valid_uuid(self):
        uid = uuid.uuid4()
        obj = MarkNotifiedRequest(match_id=uid)
        assert obj.match_id == uid
