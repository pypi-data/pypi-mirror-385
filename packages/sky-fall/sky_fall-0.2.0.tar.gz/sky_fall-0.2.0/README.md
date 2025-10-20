# skyfall

Minimal Python client for the [OpenWeatherMap](https://openweathermap.org/api) current weather endpoint. It keeps the public interface intentionally tiny: instantiate `SkyFall` with your API key, then call `.weather("City Name")` for a structured weather snapshot.

## Installation

```bash
pip install skyfall
```

> **Note:** The package requires Python 3.8 or newer and the `requests` library, which is installed automatically.

## Getting an API key

1. Sign up for a free OpenWeatherMap account.
2. Generate an API key from the dashboard.
3. Provide that key when creating a `SkyFall` instance.

## Usage

```python
from skyfall import SkyFall

client = SkyFall(api_key="your-openweather-api-key")

report = client.weather("Berlin")

print(report.city)            # "Berlin"
print(report.temperature_c)   # e.g. 18.4
print(report.description)     # e.g. "broken clouds"
```

By default results use metric units. Pass `units="imperial"` or `units="standard"` when instantiating the client to change that. Set a custom timeout via the `timeout` keyword if desired.

```python
SkyFall(api_key="...", units="imperial", timeout=5)
```

## Returned data

`.weather(...)` returns a `WeatherReport` dataclass containing:

- `city`: Name OpenWeatherMap associates with the coordinates.
- `description`: Human-readable summary of the current conditions.
- `temperature_c` / `feels_like_c`: Temperatures in the requested unit system (suffix kept for clarity).
- `humidity`: Relative humidity percentage.
- `raw`: The complete JSON payload from OpenWeatherMap for advanced use cases.

Access the raw payload if you need additional fields not surfaced on the dataclass.

## Error handling

Network or API issues raise `SkyFallError`. Double-check your API key, usage limits, and spelling of the city name if you encounter errors. Invalid arguments raise `ValueError`.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .[dev]
```

Run a quick manual check:

```bash
python -c "from skyfall import SkyFall; print(SkyFall(api_key='YOUR_KEY').weather('Tokyo'))"
```

## Publishing

1. Update the version in `pyproject.toml`.
2. Build artifacts: `python -m build`
3. Upload with `twine upload dist/*`

## License

MIT License. See `LICENSE` for details.
