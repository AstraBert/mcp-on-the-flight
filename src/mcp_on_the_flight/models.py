"""Pydantic models."""

from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, List
from datetime import datetime
from typing_extensions import Self


class PlaneTicket(BaseModel):
    flight_number: str = Field(
        description="Number of the flight, as reported on the ticket",
        default_factory=str,
    )
    depature_time: str = Field(
        description="Date and time of departure, as reported in the ticket.",
        examples=["2025-02-14T01:15", "2025-05-26T04:25", "2025-07-29T14:30"],
        default_factory=str,
    )
    landing_time: str = Field(
        description="Date and time of landing, as reported in the ticket.",
        examples=["2025-02-14T03:15", "2025-05-26T05:55", "2025-07-29T17:45"],
        default_factory=str,
    )
    seat_number: str = Field(
        description="Seat number as reported on the ticket.",
        examples=["17A", "32C", "4F"],
        default_factory=str,
    )
    operated_by: str = Field(
        description="Company that operates the flight.",
        examples=["Ryanair", "EasyJet", "Austrian Airlines", "Lufthansa"],
        default_factory=str,
    )
    extra_information: Dict[str, Any] = Field(
        description="Optional extra information, in the form of a dictionary that maps the information key (e.g.: 'bags') to the value (e.g. ['small cabin bag', '23kg hand off bag'])",
        examples=[
            {"queue": "priority", "entrance": "back"},
            {
                "bags": ["small cabin bag", "23kg handoff bag"],
                "queue": "non-priority",
                "entrance": "back",
            },
        ],
        default_factory=dict,
    )

    @model_validator(mode="after")
    def validate_plane_ticket(self) -> Self:
        now = datetime.now()
        if self.depature_time:
            try:
                dt_dep = datetime.strptime(self.depature_time, "%Y-%m-%dT%H:%M")
            except ValueError:
                raise ValueError(
                    "The provided date and time for departure is not formatted correctly"
                )
            if dt_dep < now:
                raise ValueError("The departure time is in the past")
        if self.landing_time:
            try:
                dt_land = datetime.strptime(self.landing_time, "%Y-%m-%dT%H:%M")
            except ValueError:
                raise ValueError(
                    "The provided date and time for departure is not formatted correctly"
                )
            if dt_land < now:
                raise ValueError("The landing time is in the past")
        if self.landing_time and self.depature_time:
            if dt_dep > dt_land:
                raise ValueError("The landing time is before the departure time")
        return self


class LiquidsRules(BaseModel):
    volume_limits_ml: int = Field(
        description="Maximum volumetric limit for liquids, expressed in mL. Use 0 for when no liquids are allowed, use -1 for no limit.",
        ge=-1,
        default=100,
    )
    in_a_bag: bool = Field(
        description="Whether or not liquids must be put in a plastic bag before security checks.",
        default=True,
    )
    alcoholic_beverages_allowed: bool = Field(
        description="Whether or not alcoholic beverages are allowed.",
        default=False,
    )


class CompanyPolicies(BaseModel):
    luggage: str = Field(
        description="Rules about luggage.",
        default_factory=str,
    )
    forbidden_items: List[str] = Field(
        description="Items that you are forbidden from bringing on the plane.",
        default_factory=list,
    )
    liquids: LiquidsRules = Field(
        description="Rules about liquids, concerning limits in volume and in alcoholic beverages.",
        default_factory=LiquidsRules,
    )
    pharmaceuticals: str = Field(
        description="Rules about pharmaceuticals, if any.",
        default_factory=str,
    )
    smoking_allowed: bool = Field(
        description="Whether or not the company allows smoking on the flight.",
        default=False,
    )
