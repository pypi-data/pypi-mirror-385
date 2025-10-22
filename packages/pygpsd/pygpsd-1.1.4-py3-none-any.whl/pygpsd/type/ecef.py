from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ECEFPosition:
    x: float  # ECEF X position in meters
    y: float  # ECEF Y position in meters
    z: float  # ECEF Z position in meters

    @staticmethod
    def from_json(data: dict) -> ECEFPosition:
        return ECEFPosition(
            x=data["ecefx"] if "ecefx" in data else 0,
            y=data["ecefy"] if "ecefy" in data else 0,
            z=data["ecefz"] if "ecefz" in data else 0,
        )


@dataclass
class ECEFVelocity:
    x: float  # ECEF X velocity in meters per second
    y: float  # ECEF Y velocity in meters per second
    z: float  # ECEF Z velocity in meters per second

    @staticmethod
    def from_json(data: dict) -> ECEFVelocity:
        return ECEFVelocity(
            x=data["ecefvx"] if "ecefvx" in data else 0,
            y=data["ecefvy"] if "ecefvy" in data else 0,
            z=data["ecefvz"] if "ecefvz" in data else 0,
        )


@dataclass
class ECEFErrors:
    position: float  # ECEF position error in meters
    velocity: float  # ECEF velocity error in meters per second

    @staticmethod
    def from_json(data: dict) -> ECEFErrors:
        return ECEFErrors(
            position=data["ecefpAcc"] if "ecefpAcc" in data else 0,
            velocity=data["ecefvAcc"] if "ecefvAcc" in data else 0,
        )


@dataclass
class ECEF:
    errors: ECEFErrors
    position: ECEFPosition
    velocity: ECEFVelocity

    @staticmethod
    def from_json(data: dict) -> ECEF:
        return ECEF(
            errors=ECEFErrors.from_json(data),
            position=ECEFPosition.from_json(data),
            velocity=ECEFVelocity.from_json(data),
        )
