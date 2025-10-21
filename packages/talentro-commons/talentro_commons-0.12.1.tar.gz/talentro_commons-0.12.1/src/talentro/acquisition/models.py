import enum

from uuid import UUID

from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column, JSON, Enum
from sqlmodel import Field, Relationship

from ..general.models import BaseModel


class ChannelType(StrEnum):
    JOB_BOARD = 'job-board'
    SOCIAL = 'social'


class CampaignGoal(enum.Enum):
    REACH = 'reach'
    TRAFFIC = 'traffic'
    CONVERSION = 'conversion'
    LEADS = 'leads'


class CampaignsModel(BaseModel):
    pass


class CampaignsOrganizationModel(CampaignsModel):
    organization: UUID = Field(index=True)


class Campaign(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    status: str = Field(index=True)
    last_sync_date: Optional[datetime] = Field()
    ad_count: int = Field(default=0)
    channel_id: UUID = Field(index=True)
    channel_type: ChannelType = Field(sa_column=Column(Enum(ChannelType)))
    campaign_goal: Optional[CampaignGoal] = Field(sa_column=Column(Enum(CampaignGoal)))
    feed_id: UUID = Field(index=True)
    selection_criteria: dict = Field(sa_column=Column(JSON))

    ad_sets: list["AdSet"] = Relationship(back_populates="campaign")
    ads: list["Ad"] = Relationship(back_populates="campaign")


class AdSet(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    platforms: list = Field(sa_column=Column(JSON))
    ad_types: list = Field(sa_column=Column(JSON))
    settings: dict = Field(sa_column=Column(JSON))

    campaign_id: UUID = Field(foreign_key="campaign.id", ondelete="CASCADE", index=True)
    campaign: "Campaign" = Relationship(back_populates="ad_sets")

    ads: list["Ad"] = Relationship(back_populates="ad_set")


class TargetLocation(CampaignsOrganizationModel, table=True):
    ad_set: UUID = Field(foreign_key="adset.id")
    address: str = Field(index=True)
    distance: int = Field(index=True)


class TargetAudience(CampaignsOrganizationModel, table=True):
    ad_set: UUID = Field(foreign_key="adset.id")
    age_min: int = Field(index=True, default=18)
    age_max: int = Field(index=True, default=150)
    interests: list = Field(sa_column=Column(JSON))
    languages: list = Field(sa_column=Column(JSON))


class Ad(CampaignsOrganizationModel, table=True):
    name: str = Field(index=True)
    external_id: Optional[str] = Field(index=True)
    vacancy_id: Optional[UUID] = Field()
    lead_form: Optional[UUID] = Field(foreign_key="leadform.id")
    primary_text: str = Field()
    title: str = Field()
    description: Optional[str] = Field()
    conversion_goal: Optional[str] = Field()

    campaign_id: UUID = Field(foreign_key="campaign.id", ondelete="CASCADE", index=True)
    campaign: "Campaign" = Relationship(back_populates="ads")

    ad_set_id: Optional[UUID] = Field(foreign_key="adset.id", ondelete="CASCADE", index=True, nullable=True)
    ad_set: Optional["AdSet"] = Relationship(back_populates="ads")


class LeadForm(CampaignsOrganizationModel, table=True):
    title: str = Field()
