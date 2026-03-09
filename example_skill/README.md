# Weather Skill for OpenClaw

This is the Weather skill downloaded from clawhub.com for OpenClaw agents.

## Description

Get current weather and forecasts via wttr.in or Open-Meteo. No API key needed.

## Installation

```bash
clawhub install weather
```

## Usage

### Basic Weather Query
```
What's the weather in London?
```

### Forecast Request
```
What's the forecast for New York this weekend?
```

### Temperature Check
```
Temperature in Tokyo?
```

## Features

- Current weather conditions
- 3-day forecasts
- Temperature, humidity, wind speed
- Precipitation information
- No API key required

## Implementation

The skill uses `wttr.in` service via curl commands:

```bash
# Current weather
curl "wttr.in/London?format=3"

# Detailed forecast
curl "wttr.in/London"
```

## Files

- `SKILL.md` - Skill definition and documentation
- `README.md` - This file

## License

This skill is provided as-is from clawhub.com. Check the original source for license information.

## Source

Originally downloaded from: https://clawhub.com/skills/weather

## Contributing

To contribute improvements back to the community:

1. Fork this repository
2. Make your changes
3. Submit a pull request
4. Consider publishing to clawhub.com

## Related Skills

- `weather-pollen` - Pollen information
- `google-weather` - Google Weather integration
- `openmeteo-sh-weather-advanced` - Advanced OpenMeteo integration