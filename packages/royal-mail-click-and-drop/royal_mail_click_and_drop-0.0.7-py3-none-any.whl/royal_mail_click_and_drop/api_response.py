"""API response object."""

from __future__ import annotations
from typing import TypeVar
from collections.abc import Mapping
from pydantic import Field, StrictInt, StrictBytes, BaseModel

T = TypeVar('T')


class ApiResponse[T](BaseModel):
    """
    API response object
    """

    status_code: StrictInt = Field(description='HTTP status code')
    headers: Mapping[str, str] | None = Field(None, description='HTTP headers')
    data: T = Field(description='Deserialized data given the data type')
    raw_data: StrictBytes = Field(description='Raw data (HTTP response body)')

    model_config = {'arbitrary_types_allowed': True}
