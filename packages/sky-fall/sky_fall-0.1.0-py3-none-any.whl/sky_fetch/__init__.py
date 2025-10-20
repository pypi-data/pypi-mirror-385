"""
sky_fetch
=========

A tiny OpenWeatherMap client that exposes a single method: ``SkyFetch.weather(city)``.
"""

from .client import SkyFetch, SkyFetchError, WeatherReport

__all__ = ["SkyFetch", "SkyFetchError", "WeatherReport"]
