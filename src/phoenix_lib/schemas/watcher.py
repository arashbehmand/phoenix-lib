"""Inter-service contract DTOs for the job-assistant ↔ watcher API boundary.

Both services import these models from this single source of truth to prevent
silent schema drift between independently maintained copies.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict


class JobAlertCreate(BaseModel):
    """Request payload for creating a new job alert."""

    alert_name: Optional[str] = None
    keywords: Union[str, List[str]]
    sources: Optional[List[str]] = None
    location: Optional[str] = None
    check_interval_minutes: int = 5
    filters: Optional[Dict[str, Any]] = None


class JobAlertUpdate(BaseModel):
    """Request payload for updating an existing job alert."""

    alert_name: Optional[str] = None
    keywords: Optional[Union[str, List[str]]] = None
    sources: Optional[List[str]] = None
    location: Optional[str] = None
    check_interval_minutes: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class LinkedInCookieCreate(BaseModel):
    """Request payload for creating or updating LinkedIn session cookies."""

    li_at: str
    jsession_id: Optional[str] = None
    additional_cookies: Optional[Dict[str, str]] = None


class JobListingResponse(BaseModel):
    """Response schema for a scraped job listing."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str
    source: str
    source_job_id: str
    url: str
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    snippet: Optional[str]
    posted_at: Optional[datetime]
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]
    employment_type: Optional[str]
    remote_type: Optional[str]
    content_hash: str
    embedding_model: Optional[str] = None
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime


class JobMatchResponse(BaseModel):
    """Response schema for a job match record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_alert_id: uuid.UUID
    job_listing_id: uuid.UUID
    user_id: uuid.UUID
    relevance_score: int
    key_strengths: List[str]
    potential_concerns: List[str]
    strategic_value: Optional[str]
    recommended_action: Optional[str]
    reasoning: Optional[str]
    is_notified: bool
    created_at: datetime


class JobMatchWithListing(JobMatchResponse):
    """Job match record with embedded listing details."""

    job_listing: JobListingResponse


class ProcessAlertRequest(BaseModel):
    """Request to process a specific alert."""

    alert_id: uuid.UUID
    min_relevance_score: int = 60


class ProcessAlertResponse(BaseModel):
    """Response from processing an alert."""

    alert_id: str
    alert_name: str
    scraped_jobs: int
    new_jobs: int
    matches: int
    notifications_sent: int
    errors: List[str]


class MarkNotifiedRequest(BaseModel):
    """Request to mark a match as notified."""

    match_id: uuid.UUID
