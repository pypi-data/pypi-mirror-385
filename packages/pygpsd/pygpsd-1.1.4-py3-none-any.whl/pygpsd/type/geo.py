from __future__ import annotations
from dataclasses import dataclass


@dataclass
class GeoPosition:
    longitude: float
    latitude: float
    altitude: float

    @staticmethod
    def from_json(data: dict) -> GeoPosition:
        return GeoPosition(
            longitude=data["lon"] if "lon" in data else 0,
            latitude=data["lat"] if "lat" in data else 0,
            altitude=data["alt"] if "alt" in data else 0,
        )


@dataclass
class GeoTrajectory:
    track: float
    speed: float
    climb: float

    @staticmethod
    def from_json(data: dict) -> GeoTrajectory:
        return GeoTrajectory(
            data["track"] if "track" in data else 0,
            data["speed"] if "speed" in data else 0,
            data["climb"] if "climb" in data else 0,
        )


@dataclass
class GeoErrors:
    epc: float  # Estimated climb error in meters per second
    epd: float  # Estimated track (direction) error in degrees
    eph: float  # Estimated horizontal Position (2D) Error in meters
    eps: float  # Estimated speed error in meters per second
    ept: float  # Estimated time stamp error in seconds
    epv: float  # Estimated vertical error in meters
    epx: float  # Longitude error estimate in meters
    epy: float  # Latitude error estimate in meters

    @staticmethod
    def from_json(data: dict) -> GeoErrors:
        return GeoErrors(
            epc=data["epc"] if "epc" in data else 0,
            epd=data["epd"] if "epd" in data else 0,
            eph=data["eph"] if "eph" in data else 0,
            eps=data["eps"] if "eps" in data else 0,
            ept=data["ept"] if "ept" in data else 0,
            epx=data["epx"] if "epx" in data else 0,
            epy=data["epy"] if "epy" in data else 0,
            epv=data["epv"] if "epv" in data else 0,
        )


@dataclass
class Geo:
    errors: GeoErrors
    position: GeoPosition
    trajectory: GeoTrajectory

    @staticmethod
    def from_json(data: dict) -> Geo:
        return Geo(
            errors=GeoErrors.from_json(data),
            position=GeoPosition.from_json(data),
            trajectory=GeoTrajectory.from_json(data),
        )
