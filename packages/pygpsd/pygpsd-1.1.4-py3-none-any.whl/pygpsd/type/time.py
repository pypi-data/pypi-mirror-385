from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Time:
    time: datetime
    leap_seconds: int

    @staticmethod
    def from_json(data: dict) -> Time:
        return Time(
            time=datetime.fromisoformat(data["time"]),
            leap_seconds=data["leap_seconds"] if "leap_seconds" in data else 0,
        )
