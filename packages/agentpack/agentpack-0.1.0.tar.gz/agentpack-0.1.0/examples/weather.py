"""
Weather lookup example tool.

This demonstrates the ZERO-CONFIG approach:
- User writes ONLY business logic
- NO server setup, NO Docker, NO infrastructure
- Just define the tool - Builder + Runtime handle the rest

This tool demonstrates:
- External API calls with ctx.http
- Secret management with ctx.secrets
- Structured logging with ctx.logger
- Input/output validation with Pydantic
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from agentpack import ExecutionContext, tool


class Units(str, Enum):
    """Temperature units."""

    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class WeatherInput(BaseModel):
    """Weather lookup input schema."""

    location: str = Field(description="City name or ZIP code")
    units: Units = Field(default=Units.CELSIUS, description="Temperature units")


class WeatherOutput(BaseModel):
    """Weather lookup output schema."""

    location: str
    temperature: float
    conditions: str
    humidity: float
    wind_speed: float


@tool(
    name="weather_lookup",
    description="Get current weather for a location using OpenWeatherMap API",
    input_schema=WeatherInput,
    output_schema=WeatherOutput,
)
async def weather_lookup(input: WeatherInput, ctx: ExecutionContext) -> WeatherOutput:
    """Look up weather for a location."""
    ctx.logger.info("Looking up weather", location=input.location)

    # Get API key from environment (requires OPENWEATHER_API_KEY env var)
    api_key = await ctx.secrets.require("OPENWEATHER_API_KEY")

    # Determine units for API call
    units_param = "metric" if input.units == Units.CELSIUS else "imperial"

    # Make API request with automatic retries
    response = await ctx.http.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": input.location,
            "appid": api_key,
            "units": units_param,
        },
    )

    data = response.data

    ctx.logger.info(
        "Weather lookup successful",
        location=input.location,
        temp=data["main"]["temp"],
    )

    return WeatherOutput(
        location=data["name"],
        temperature=data["main"]["temp"],
        conditions=data["weather"][0]["description"],
        humidity=data["main"]["humidity"],
        wind_speed=data["wind"]["speed"],
    )


# That's it! No server code, no infrastructure.
# Builder will:
#   1. Scan tools/ directory
#   2. Find this file
#   3. Generate .agentpack-manifest.json
#   4. Build Docker image with runtime
#   5. Deploy to container backend
#
# Runtime will:
#   1. Load manifest
#   2. Import this tool
#   3. Start gRPC server
#   4. Handle requests from Rust core
