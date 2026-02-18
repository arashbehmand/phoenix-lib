"""Tests for phoenix_lib.schemas.job (JobDescriptionSchema)."""

import pytest
from pydantic import ValidationError

from phoenix_lib.schemas.job import (Iso8601, JobDescriptionSchema, Location,
                                     Meta, Remote, Skill)


class TestRemoteEnum:
    def test_full(self):
        assert Remote.Full.value == "Full"

    def test_hybrid(self):
        assert Remote.Hybrid.value == "Hybrid"

    def test_none(self):
        assert Remote.None_.value == "None"


class TestLocation:
    def test_all_optional(self):
        loc = Location()
        assert loc.address is None
        assert loc.city is None

    def test_with_fields(self):
        loc = Location(city="New York", countryCode="US", region="NY")
        assert loc.city == "New York"
        assert loc.countryCode == "US"

    def test_extra_fields_allowed(self):
        loc = Location(city="Berlin", timezone="CET")
        assert loc.city == "Berlin"


class TestSkill:
    def test_all_optional(self):
        skill = Skill()
        assert skill.name is None
        assert skill.level is None
        assert skill.keywords is None

    def test_with_fields(self):
        skill = Skill(name="Python", level="Expert", keywords=["FastAPI", "asyncio"])
        assert skill.name == "Python"
        assert len(skill.keywords) == 2


class TestIso8601:
    def test_valid_full_date(self):
        obj = Iso8601("2024-06-29")
        assert obj.root == "2024-06-29"

    def test_valid_year_month(self):
        obj = Iso8601("2023-04")
        assert obj.root == "2023-04"

    def test_valid_year_only(self):
        obj = Iso8601("2024")
        assert obj.root == "2024"

    def test_invalid_format_raises(self):
        with pytest.raises(ValidationError):
            Iso8601("June 2024")

    def test_invalid_format_string_raises(self):
        with pytest.raises(ValidationError):
            Iso8601("not-a-date")


class TestJobDescriptionSchema:
    def test_all_optional(self):
        job = JobDescriptionSchema()
        assert job.title is None
        assert job.company is None
        assert job.skills is None

    def test_with_basic_fields(self):
        job = JobDescriptionSchema(
            title="Software Engineer",
            company="Acme Corp",
            type="Full-time",
        )
        assert job.title == "Software Engineer"
        assert job.company == "Acme Corp"

    def test_with_location(self):
        job = JobDescriptionSchema(
            title="Dev",
            location=Location(city="London", countryCode="GB"),
        )
        assert job.location.city == "London"

    def test_with_remote_enum(self):
        job = JobDescriptionSchema(title="Dev", remote=Remote.Full)
        assert job.remote == Remote.Full

    def test_remote_from_string(self):
        job = JobDescriptionSchema(title="Dev", remote="Hybrid")
        assert job.remote == Remote.Hybrid

    def test_with_skills_list(self):
        job = JobDescriptionSchema(
            title="Engineer",
            skills=[
                Skill(name="Python", level="Senior"),
                Skill(name="Docker"),
            ],
        )
        assert len(job.skills) == 2
        assert job.skills[0].name == "Python"

    def test_with_responsibilities(self):
        job = JobDescriptionSchema(
            title="Dev",
            responsibilities=["Write code", "Review PRs"],
        )
        assert len(job.responsibilities) == 2

    def test_with_qualifications(self):
        job = JobDescriptionSchema(
            title="Dev",
            qualifications=["5 years experience", "CS degree"],
        )
        assert len(job.qualifications) == 2

    def test_with_date(self):
        job = JobDescriptionSchema(title="Dev", date="2024-01")
        assert job.date.root == "2024-01"

    def test_with_meta(self):
        job = JobDescriptionSchema(
            title="Dev",
            meta=Meta(version="v1.0.0", lastModified="2024-01-01T00:00:00"),
        )
        assert job.meta.version == "v1.0.0"

    def test_extra_fields_allowed(self):
        job = JobDescriptionSchema(title="Dev", custom_field="custom_value")
        assert job.title == "Dev"

    def test_serialization(self):
        job = JobDescriptionSchema(title="Dev", company="Corp")
        d = job.model_dump()
        assert d["title"] == "Dev"
        assert d["company"] == "Corp"


class TestGetJobSchemaParser:
    def test_returns_parser(self):
        from phoenix_lib.schemas.job import get_job_schema_parser

        parser = get_job_schema_parser()
        assert parser is not None

    def test_parser_has_pydantic_object(self):
        from phoenix_lib.schemas.job import get_job_schema_parser

        parser = get_job_schema_parser()
        assert parser.pydantic_object is JobDescriptionSchema


class TestGetJobSchemaFormatInstructions:
    def test_returns_string(self):
        from phoenix_lib.schemas.job import get_job_schema_format_instructions

        instructions = get_job_schema_format_instructions()
        assert isinstance(instructions, str)
        assert len(instructions) > 0
