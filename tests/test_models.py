import pytest

from src.mcp_on_the_flight.models import (
    PlaneTicket,
    CompanyPolicies,
    LiquidsRules,
)
from pydantic_core import ValidationError


def test_plane_ticket() -> None:
    t1 = PlaneTicket()
    t1_dct = t1.model_dump()
    for v in t1_dct.values():
        assert v == type(v)()
    t2 = PlaneTicket(
        flight_number="FR251",
        depature_time="2025-07-14T01:15",
        landing_time="2025-07-14T03:15",
        seat_number="14A",
        operated_by="Ryanair",
        extra_information={"queue": "non-priority", "entrance": "back"},
    )
    assert t2.flight_number == "FR251"
    assert t2.depature_time == "2025-07-14T01:15"
    assert t2.landing_time == "2025-07-14T03:15"
    assert t2.seat_number == "14A"
    assert t2.operated_by == "Ryanair"
    assert t2.extra_information == {
        "queue": "non-priority",
        "entrance": "back",
    }
    with pytest.raises(ValidationError):
        PlaneTicket(
            flight_number="FR251",
            depature_time="2025-02-14T01:15",
            landing_time="2025-02-14T03:15",
            seat_number="14A",
            operated_by="Ryanair",
            extra_information={"queue": "non-priority", "entrance": "back"},
        )
    with pytest.raises(ValidationError):
        PlaneTicket(
            flight_number="FR251",
            depature_time="2025-13-14T01:15",
            landing_time="2025-13-14T03:15",
            seat_number="14A",
            operated_by="Ryanair",
            extra_information={"queue": "non-priority", "entrance": "back"},
        )
    with pytest.raises(ValidationError):
        PlaneTicket(
            flight_number="FR251",
            depature_time="2025-07-14T03:15",
            landing_time="2025-07-14T01:15",
            seat_number="14A",
            operated_by="Ryanair",
            extra_information={"queue": "non-priority", "entrance": "back"},
        )


def test_liquid_rules():
    l1 = LiquidsRules()
    assert l1.volume_limits_ml == 100
    assert not l1.alcoholic_beverages_allowed
    assert l1.in_a_bag
    with pytest.raises(ValidationError):
        LiquidsRules(volume_limits_ml=-2)


def test_company_policies():
    c1 = CompanyPolicies()
    assert c1.luggage == ""
    assert c1.forbidden_items == []
    assert c1.liquids == LiquidsRules()
    assert not c1.smoking_allowed
    assert c1.pharmaceuticals == ""
    with pytest.raises(ValidationError):
        CompanyPolicies(forbidden_items="knife")
