from __future__ import annotations

from typing import ClassVar

from pydantic import StrictInt, StrictStr

from royal_mail_click_and_drop.models.order_field_response import OrderFieldResponse
from royal_mail_click_and_drop.models.base import RMBaseModel


class CreateOrderErrorResponse(RMBaseModel):
    """
    CreateOrderErrorResponse
    """

    error_code: StrictInt | None = None
    error_message: StrictStr | None = None
    fields: list[OrderFieldResponse] | None = None
    __properties: ClassVar[list[str]] = ['errorCode', 'errorMessage', 'fields']
