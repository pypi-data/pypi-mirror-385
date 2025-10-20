from __future__ import annotations

import datetime
import typing


class BaseLinkProperties:
    link_type_api_name: str = ""

    def __init__(self, **kwargs: typing.Any):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_dict(cls, data: dict[str, typing.Any]):
        return cls(**dict(data or {}))


class WorksForLinkProperties(BaseLinkProperties):
    link_type_api_name = "works_for"
    sinceDate: datetime.date | None = None  # noqa: N815
    role: str | None = None  # noqa: N815
