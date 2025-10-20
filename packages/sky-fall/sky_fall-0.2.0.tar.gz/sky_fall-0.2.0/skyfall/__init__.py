"""
skyfall
=======

A tiny OpenWeatherMap client that exposes a single method: ``SkyFall.weather(city)``.
"""

from .client import SkyFall, SkyFallError, WeatherReport

__all__ = ["SkyFall", "SkyFallError", "WeatherReport"]
