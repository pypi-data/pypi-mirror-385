from __future__ import annotations
from dataclasses import dataclass

from pygpsd.type.health import Health


@dataclass
class Satellite:
    prn: int                 # PRN ID of the satellite
    az: float                # Azimuth, degrees from true north
    el: float                # Elevation in degrees
    gnssid: int              # The GNSS ID
    health: Health           # The health of this satellite
    ss: float                # Signal to Noise ratio in dBHz
    svid: int                # The satellite ID (PRN) within its constellation
    used: bool

    @staticmethod
    def from_json(data: dict) -> Satellite:
        return Satellite(
            prn=data['PRN'] if "PRN" in data else 0,
            az=data['az'] if "az" in data else 0,
            el=data['el'] if "el" in data else 0,
            gnssid=data['gnssid'] if "gnssid" in data else 0,
            health=Health(data["health"]) if "health" in data else Health.UNKNOWN,
            ss=data["ss"] if "ss" in data else 0,
            svid=data["svid"] if "svid" in data else 0,
            used=data["used"] if "used" in data else False,
        )
