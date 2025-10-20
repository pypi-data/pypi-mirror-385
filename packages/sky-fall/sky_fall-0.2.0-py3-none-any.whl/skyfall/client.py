"""Minimal OpenWeatherMap client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import requests


class SkyFallError(Exception):
    """Raised when the weather lookup fails."""


@dataclass
class WeatherReport:
    """Structured representation of weather data returned by OpenWeatherMap."""

    city: str
    description: str
    temperature_c: float
    feels_like_c: float
    humidity: int
    raw: Dict[str, Any]


class SkyFall:
    """
    Tiny wrapper around the OpenWeatherMap current weather API.

    Parameters
    ----------
    api_key:
        Your OpenWeatherMap API key. Sign up at https://openweathermap.org/api.
    timeout:
        Optional request timeout in seconds (defaults to 10).
    units:
        Unit system understood by OpenWeatherMap. Defaults to ``metric``.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str, *, timeout: float = 10.0, units: str = "metric") -> None:
        if not api_key or not api_key.strip():
            raise ValueError("An OpenWeatherMap API key is required.")
        if units not in {"standard", "metric", "imperial"}:
            raise ValueError("Units must be one of 'standard', 'metric', or 'imperial'.")

        self._api_key = api_key.strip()
        self._timeout = timeout
        self._units = units

    def weather(self, city: str) -> WeatherReport:
        """
        Fetch the current weather for a city.

        Parameters
        ----------
        city:
            City name, e.g. ``\"London\"`` or ``\"New York\"``.

        Returns
        -------
        WeatherReport
            A simple dataclass with the key data points plus the raw JSON response.

        Raises
        ------
        ValueError
            If the city value is empty.
        SkyFallError
            If OpenWeatherMap rejects the request or the request fails.
        """

        if not city or not city.strip():
            raise ValueError("City must be a non-empty string.")

        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "q": city.strip(),
                    "appid": self._api_key,
                    "units": self._units,
                },
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise SkyFallError("Could not reach OpenWeatherMap.") from exc

        if response.status_code != 200:
            error_detail = _extract_error(response)
            raise SkyFallError(error_detail)

        payload = _parse_json(response)

        weather = payload.get("weather", [])
        main = payload.get("main", {})
        description = weather[0].get("description", "Unavailable") if weather else "Unavailable"

        try:
            report = WeatherReport(
                city=payload.get("name", city.strip()),
                description=description,
                temperature_c=float(main.get("temp")),
                feels_like_c=float(main.get("feels_like")),
                humidity=int(main.get("humidity")),
                raw=payload,
            )
        except (TypeError, ValueError) as exc:
            raise SkyFallError("Received malformed data from OpenWeatherMap.") from exc

        return report


def _extract_error(response: requests.Response) -> str:
    """Return the error message supplied by the API, or a fallback string."""

    try:
        payload = response.json()
    except ValueError:
        return f"OpenWeatherMap error {response.status_code}: {response.text.strip() or 'Unknown error'}"

    message = payload.get("message")
    cod = payload.get("cod")
    if message and cod:
        return f"OpenWeatherMap error {cod}: {message}"
    if message:
        return f"OpenWeatherMap error: {message}"
    return f"OpenWeatherMap error {response.status_code}"


def _parse_json(response: requests.Response) -> Dict[str, Any]:
    """Parse JSON payload with a helpful error message."""

    try:
        return response.json()
    except ValueError as exc:
        snippet = response.text[:200]
        raise SkyFallError(f"Failed to parse response JSON: {snippet}") from exc
