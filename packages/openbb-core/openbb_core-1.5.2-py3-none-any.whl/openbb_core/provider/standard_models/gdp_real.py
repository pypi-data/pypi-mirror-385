"""Real GDP Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class GdpRealQueryParams(QueryParams):
    """Real GDP Query."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class GdpRealData(Data):
    """Real GDP Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(
        default=None, description="The country represented by the Real GDP value."
    )
    value: int | float = Field(
        description="Real GDP value for the country and date.",
    )
