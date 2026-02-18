"""Job description schema as Pydantic models.

Based on the job schema JSON schema definition.
Provides parser helpers mirroring domain/json_resume.py.
"""

from __future__ import annotations

from enum import Enum

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel, constr


class Location(BaseModel):
    model_config = ConfigDict(extra="allow")

    address: str | None = Field(
        None,
        description="To add multiple address lines, use \\n. For example, 1234 Glücklichkeit Straße\\nHinterhaus 5. Etage li.",
    )
    postalCode: str | None = None
    city: str | None = None
    countryCode: str | None = Field(
        None, description="code as per ISO-3166-1 ALPHA-2, e.g. US, AU, IN"
    )
    region: str | None = Field(
        None,
        description="The general region where you live. Can be a US state, or a province, for instance.",
    )


class Remote(Enum):
    Full = "Full"
    Hybrid = "Hybrid"
    None_ = "None"


class Skill(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(None, description="e.g. Web Development")
    level: str | None = Field(None, description="e.g. Master")
    keywords: list[str] | None = Field(
        None, description="List some keywords pertaining to this skill"
    )


class Meta(BaseModel):
    model_config = ConfigDict(extra="allow")

    canonical: AnyUrl | None = Field(
        None, description="URL (as per RFC 3986) to latest version of this document"
    )
    version: str | None = Field(
        None, description="A version field which follows semver - e.g. v1.0.0"
    )
    lastModified: str | None = Field(
        None, description="Using ISO 8601 with YYYY-MM-DDThh:mm:ss"
    )


class Iso8601(
    RootModel[
        constr(
            pattern=r"^([1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]|[1-2][0-9]{3}-[0-1][0-9]|[1-2][0-9]{3})$"
        )
    ]
):
    root: constr(
        pattern=r"^([1-2][0-9]{3}-[0-1][0-9]-[0-3][0-9]|[1-2][0-9]{3}-[0-1][0-9]|[1-2][0-9]{3})$"
    ) = Field(
        ...,
        description="Similar to the standard date type, but each section after the year is optional. e.g. 2014-06-29 or 2023-04",
    )


class JobDescriptionSchema(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str | None = Field(None, description="e.g. Web Developer")
    company: str | None = Field(None, description="Microsoft")
    type: str | None = Field(None, description="Full-time, part-time, contract, etc.")
    date: Iso8601 | None = None
    description: str | None = Field(
        None, description="Write a short description about the job"
    )
    location: Location | None = None
    remote: Remote | None = Field(
        None, description="the level of remote work available"
    )
    salary: str | None = Field(None, description="100000")
    experience: str | None = Field(None, description="Senior or Junior or Mid-level")
    responsibilities: list[str] | None = Field(None, description="what the job entails")
    qualifications: list[str] | None = Field(
        None, description="List out your qualifications"
    )
    skills: list[Skill] | None = Field(
        None, description="List out your professional skill-set"
    )
    meta: Meta | None = Field(
        None,
        description="The schema version and any other tooling configuration lives here",
    )


def get_job_schema_parser():
    """Return a LangChain PydanticOutputParser for JobDescriptionSchema."""
    from langchain_core.output_parsers import \
        PydanticOutputParser  # pylint: disable=import-outside-toplevel

    return PydanticOutputParser(pydantic_object=JobDescriptionSchema)


def get_job_schema_format_instructions() -> str:
    """Return LLM format instructions for generating a valid JobDescriptionSchema."""
    return get_job_schema_parser().get_format_instructions()
