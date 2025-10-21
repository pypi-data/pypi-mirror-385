[![smithery badge](https://smithery.ai/badge/@isdaniel/mcp_weather_server)](https://smithery.ai/server/@isdaniel/mcp_weather_server)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/mcp-weather-server)](https://pypi.org/project/mcp-weather-server/)
[![PyPI - Version](https://img.shields.io/pypi/v/mcp-weather-server)](https://pypi.org/project/mcp-weather-server/)

<a href="https://glama.ai/mcp/servers/@isdaniel/mcp_weather_server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@isdaniel/mcp_weather_server/badge" />
</a>

# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather information using the Open-Meteo API. This server supports multiple transport modes: standard stdio, HTTP Server-Sent Events (SSE), and the new Streamable HTTP protocol for web-based integration.

## Features

### Weather & Air Quality
* Get current weather information with comprehensive metrics:
  * Temperature, humidity, dew point
  * Wind speed, direction, and gusts
  * Precipitation (rain/snow) and probability
  * Atmospheric pressure and cloud cover
  * UV index and visibility
  * "Feels like" temperature
* Get weather data for a date range with hourly details
* Get air quality information including:
  * PM2.5 and PM10 particulate matter
  * Ozone, nitrogen dioxide, carbon monoxide
  * Sulfur dioxide, ammonia, dust
  * Aerosol optical depth
  * Health advisories and recommendations

### Time & Timezone
* Get current date/time in any timezone
* Convert time between timezones
* Get timezone information

### Transport Modes
* Multiple transport modes:
  * **stdio** - Standard MCP for desktop clients (Claude Desktop, etc.)
  * **SSE** - Server-Sent Events for web applications
  * **streamable-http** - Modern MCP Streamable HTTP protocol with stateful/stateless options
* RESTful API endpoints via Starlette integration

## Installation

### Installing via Smithery

To install Weather MCP Server automatically via [Smithery](https://smithery.ai/server/@isdaniel/mcp_weather_server):

```bash
npx -y @smithery/cli install @isdaniel/mcp_weather_server
```

### Standard Installation (for MCP clients like Claude Desktop)

This package can be installed using pip:

```bash
pip install mcp_weather_server
```

### Manual Configuration for MCP Clients

This server is designed to be installed manually by adding its configuration to the `cline_mcp_settings.json` file.

1. Add the following entry to the `mcpServers` object in your `cline_mcp_settings.json` file:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": [
        "-m",
        "mcp_weather_server"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

2. Save the `cline_mcp_settings.json` file.

### HTTP Server Installation (for web applications)

For HTTP SSE or Streamable HTTP support, you'll need additional dependencies:

```bash
pip install mcp_weather_server starlette uvicorn
```

## Server Modes

This MCP server supports **stdio**, **SSE**, and **streamable-http** modes in a single unified server:

### Mode Comparison

| Feature | stdio | SSE | streamable-http |
|---------|-------|-----|-----------------|
| **Use Case** | Desktop MCP clients | Web applications (legacy) | Web applications (modern) |
| **Protocol** | Standard I/O streams | Server-Sent Events | MCP Streamable HTTP |
| **Session Management** | N/A | Stateful | Stateful or Stateless |
| **Endpoints** | N/A | `/sse`, `/messages/` | `/mcp` (single) |
| **Best For** | Claude Desktop, Cline | Browser-based apps | Modern web apps, APIs |
| **State Options** | N/A | Stateful only | Stateful or Stateless |

### 1. Standard MCP Mode (Default)
The standard mode communicates via stdio and is compatible with MCP clients like Claude Desktop.

```bash
# Default mode (stdio)
python -m mcp_weather_server

# Explicitly specify stdio mode
python -m mcp_weather_server.server --mode stdio
```

### 2. HTTP SSE Mode (Web Applications)
The SSE mode runs an HTTP server that provides MCP functionality via Server-Sent Events, making it accessible to web applications.

```bash
# Start SSE server on default host/port (0.0.0.0:8080)
python -m mcp_weather_server --mode sse

# Specify custom host and port
python -m mcp_weather_server --mode sse --host localhost --port 3000

# Enable debug mode
python -m mcp_weather_server --mode sse --debug
```

**SSE Endpoints:**
- `GET /sse` - SSE endpoint for MCP communication
- `POST /messages/` - Message endpoint for sending MCP requests

### 3. Streamable HTTP Mode (Modern MCP Protocol)
The streamable-http mode implements the new MCP Streamable HTTP protocol with a single `/mcp` endpoint. This mode supports both stateful (default) and stateless operations.

```bash
# Start streamable HTTP server on default host/port (0.0.0.0:8080)
python -m mcp_weather_server --mode streamable-http

# Specify custom host and port
python -m mcp_weather_server --mode streamable-http --host localhost --port 3000

# Enable stateless mode (creates fresh transport per request, no session tracking)
python -m mcp_weather_server --mode streamable-http --stateless

# Enable debug mode
python -m mcp_weather_server --mode streamable-http --debug
```

**Streamable HTTP Features:**
- **Stateful mode (default)**: Maintains session state across requests using session IDs
- **Stateless mode**: Creates fresh transport per request with no session tracking
- **Single endpoint**: All MCP communication happens through `/mcp`
- **Modern protocol**: Implements the latest MCP Streamable HTTP specification

**Streamable HTTP Endpoint:**
- `POST /mcp` - Single endpoint for all MCP communication (initialize, tools/list, tools/call, etc.)

**Command Line Options:**
```
--mode {stdio,sse,streamable-http}  Server mode: stdio (default), sse, or streamable-http
--host HOST                          Host to bind to (HTTP modes only, default: 0.0.0.0)
--port PORT                          Port to listen on (HTTP modes only, default: 8080)
--stateless                          Run in stateless mode (streamable-http only)
--debug                              Enable debug mode
```

**Example SSE Usage:**
```javascript
// Connect to SSE endpoint
const eventSource = new EventSource('http://localhost:8080/sse');

// Send MCP tool request
fetch('http://localhost:8080/messages/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: 'tool_call',
    tool: 'get_weather',
    arguments: { city: 'Tokyo' }
  })
});
```

**Example Streamable HTTP Usage:**
```javascript
// Initialize session and call tool using Streamable HTTP protocol
async function callWeatherTool() {
  const response = await fetch('http://localhost:8080/mcp', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: 'tools/call',
      params: {
        name: 'get_current_weather',
        arguments: { city: 'Tokyo' }
      },
      id: 1
    })
  });

  const result = await response.json();
  console.log(result);
}
```

## Configuration

This server does not require an API key. It uses the Open-Meteo API, which is free and open-source.

## Usage

This server provides several tools for weather and time-related operations:

### Available Tools

#### Weather Tools
1. **`get_current_weather`** - Get current weather for a city with comprehensive metrics
2. **`get_weather_by_datetime_range`** - Get weather data for a date range with hourly details
3. **`get_weather_details`** - Get detailed weather information as structured JSON data

#### Air Quality Tools
4. **`get_air_quality`** - Get air quality information with pollutant levels and health advice
5. **`get_air_quality_details`** - Get detailed air quality data as structured JSON

#### Time & Timezone Tools
6. **`get_current_datetime`** - Get current time in any timezone
7. **`get_timezone_info`** - Get timezone information
8. **`convert_time`** - Convert time between timezones

### Tool Details

#### `get_current_weather`

Retrieves comprehensive current weather information for a given city with enhanced metrics.

**Parameters:**
- `city` (string, required): The name of the city (English names only)

**Returns:** Detailed weather data including:
- Temperature and "feels like" temperature
- Humidity, dew point
- Wind speed, direction (as compass direction), and gusts
- Precipitation details (rain/snow) and probability
- Atmospheric pressure and cloud cover
- UV index with warning levels
- Visibility

**Example Response:**
```
The weather in Tokyo is Mainly clear with a temperature of 22.5°C (feels like 21.0°C),
relative humidity at 65%, and dew point at 15.5°C. Wind is blowing from the NE at 12.5 km/h
with gusts up to 18.5 km/h. Atmospheric pressure is 1013.2 hPa with 25% cloud cover.
UV index is 5.5 (Moderate). Visibility is 10.0 km.
```

#### `get_weather_by_datetime_range`

Retrieves hourly weather information with comprehensive metrics for a specified city between start and end dates.

**Parameters:**
- `city` (string, required): The name of the city (English names only)
- `start_date` (string, required): Start date in format YYYY-MM-DD (ISO 8601)
- `end_date` (string, required): End date in format YYYY-MM-DD (ISO 8601)

**Returns:** Comprehensive weather analysis including:
- Hourly weather data with all enhanced metrics
- Temperature trends (highs, lows, averages)
- Precipitation patterns and probabilities
- Wind conditions assessment
- UV index trends
- Weather warnings and recommendations

**Example Response:**
```
[Analysis of weather trends over 2024-01-01 to 2024-01-07]
- Temperature ranges from 5°C to 15°C
- Precipitation expected on Jan 3rd and 5th (60% probability)
- Wind speeds averaging 15 km/h from SW direction
- UV index moderate (3-5) throughout the period
- Recommendation: Umbrella needed for midweek
```

#### `get_weather_details`

Get detailed weather information for a specified city as structured JSON data for programmatic use.

**Parameters:**
- `city` (string, required): The name of the city (English names only)

**Returns:** Raw JSON data with all weather metrics suitable for processing and analysis

#### `get_air_quality`

Get current air quality information for a specified city with pollutant levels and health advisories.

**Parameters:**
- `city` (string, required): The name of the city (English names only)
- `variables` (array, optional): Specific pollutants to retrieve. Options:
  - `pm10` - Particulate matter ≤10μm
  - `pm2_5` - Particulate matter ≤2.5μm
  - `carbon_monoxide` - CO levels
  - `nitrogen_dioxide` - NO2 levels
  - `ozone` - O3 levels
  - `sulphur_dioxide` - SO2 levels
  - `ammonia` - NH3 levels
  - `dust` - Dust particle levels
  - `aerosol_optical_depth` - Atmospheric turbidity

**Returns:** Comprehensive air quality report including:
- Current pollutant levels with units
- Air quality classification (Good/Moderate/Unhealthy/Hazardous)
- Health recommendations for general population
- Specific warnings for sensitive groups
- Comparison with WHO and EPA standards

**Example Response:**
```
Air quality in Beijing (lat: 39.90, lon: 116.41):
PM2.5: 45.3 μg/m³ (Unhealthy for Sensitive Groups)
PM10: 89.2 μg/m³ (Moderate)
Ozone (O3): 52.1 μg/m³
Nitrogen Dioxide (NO2): 38.5 μg/m³
Carbon Monoxide (CO): 420.0 μg/m³

Health Advice: Sensitive groups (children, elderly, people with respiratory conditions)
should limit outdoor activities.
```

#### `get_air_quality_details`

Get detailed air quality information as structured JSON data for programmatic analysis.

**Parameters:**
- `city` (string, required): The name of the city (English names only)
- `variables` (array, optional): Specific pollutants to retrieve (same options as `get_air_quality`)

**Returns:** Raw JSON data with complete air quality metrics and hourly data

#### `get_current_datetime`

Retrieves the current time in a specified timezone.

**Parameters:**
- `timezone_name` (string, required): IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use UTC if no timezone provided.

**Returns:** Current date and time in the specified timezone

**Example:**
```json
{
  "timezone": "America/New_York",
  "current_time": "2024-01-15T14:30:00-05:00",
  "utc_time": "2024-01-15T19:30:00Z"
}
```

#### `get_timezone_info`

Get information about a specific timezone.

**Parameters:**
- `timezone_name` (string, required): IANA timezone name

**Returns:** Timezone details including offset and DST information

#### `convert_time`

Convert time from one timezone to another.

**Parameters:**
- `time_str` (string, required): Time to convert (ISO format)
- `from_timezone` (string, required): Source timezone
- `to_timezone` (string, required): Target timezone

**Returns:** Converted time in target timezone

## MCP Client Usage Examples

### Using with Claude Desktop or MCP Clients

```xml
<use_mcp_tool>
<server_name>weather</server_name>
<tool_name>get_current_weather</tool_name>
<arguments>
{
  "city": "Tokyo"
}
</arguments>
</use_mcp_tool>
```

```xml
<use_mcp_tool>
<server_name>weather</server_name>
<tool_name>get_weather_by_datetime_range</tool_name>
<arguments>
{
  "city": "Paris",
  "start_date": "2024-01-01",
  "end_date": "2024-01-07"
}
</arguments>
</use_mcp_tool>
```

```xml
<use_mcp_tool>
<server_name>weather</server_name>
<tool_name>get_current_datetime</tool_name>
<arguments>
{
  "timezone_name": "Europe/Paris"
}
</arguments>
</use_mcp_tool>
```

```xml
<use_mcp_tool>
<server_name>weather</server_name>
<tool_name>get_air_quality</tool_name>
<arguments>
{
  "city": "Beijing"
}
</arguments>
</use_mcp_tool>
```

```xml
<use_mcp_tool>
<server_name>weather</server_name>
<tool_name>get_air_quality</tool_name>
<arguments>
{
  "city": "Los Angeles",
  "variables": ["pm2_5", "pm10", "ozone"]
}
</arguments>
</use_mcp_tool>
```

## Web Integration (SSE Mode)

When running in SSE mode, you can integrate the weather server with web applications:

### HTML/JavaScript Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Weather MCP Client</title>
</head>
<body>
    <div id="weather-data"></div>
    <script>
        // Connect to SSE endpoint
        const eventSource = new EventSource('http://localhost:8080/sse');

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            document.getElementById('weather-data').innerHTML = JSON.stringify(data, null, 2);
        };

        // Function to get weather
        async function getWeather(city) {
            const response = await fetch('http://localhost:8080/messages/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'tools/call',
                    params: {
                        name: 'get_current_weather',
                        arguments: { city: city }
                    },
                    id: 1
                })
            });
        }

        // Example: Get weather for Tokyo
        getWeather('Tokyo');

        // Example: Get air quality
        async function getAirQuality(city) {
            const response = await fetch('http://localhost:8080/messages/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'tools/call',
                    params: {
                        name: 'get_air_quality',
                        arguments: { city: city }
                    },
                    id: 2
                })
            });
        }

        getAirQuality('Beijing');
    </script>
</body>
</html>
```

## Docker Deployment

The project includes Docker configurations for easy deployment:

### SSE Mode Docker
```bash
# Build
docker build -t mcp-weather-server:sse .

# Run (port will be read from PORT env var, defaults to 8081)
docker run -p 8081:8081 mcp-weather-server:sse

# Run with custom port
docker run -p 8080:8080 -e PORT=8080 mcp-weather-server:sse
```

### Streamable HTTP Mode Docker
```bash
# Build using streamable-http Dockerfile
docker build -f Dockerfile.streamable-http -t mcp-weather-server:streamable-http .

# Run in stateful mode
docker run -p 8080:8080 mcp-weather-server:streamable-http

# Run in stateless mode
docker run -p 8080:8080 -e STATELESS=true mcp-weather-server:streamable-http
```

## Development

### Project Structure

```
mcp_weather_server/
├── src/
│   └── mcp_weather_server/
│       ├── __init__.py
│       ├── __main__.py          # Main MCP server entry point
│       ├── server.py            # Unified server (stdio, SSE, streamable-http)
│       ├── utils.py             # Utility functions
│       └── tools/               # Tool implementations
│           ├── __init__.py
│           ├── toolhandler.py   # Base tool handler
│           ├── tools_weather.py # Weather-related tools
│           ├── tools_time.py    # Time-related tools
│           ├── tools_air_quality.py # Air quality tools
│           ├── weather_service.py   # Weather API service
│           └── air_quality_service.py # Air quality API service
├── tests/
├── Dockerfile                   # Docker configuration for SSE mode
├── Dockerfile.streamable-http   # Docker configuration for streamable-http mode
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Running for Development

#### Standard MCP Mode (stdio)
```bash
# From project root
python -m mcp_weather_server

# Or with PYTHONPATH
export PYTHONPATH="/path/to/mcp_weather_server/src"
python -m mcp_weather_server
```

#### SSE Server Mode
```bash
# From project root
python -m mcp_weather_server --mode sse --host 0.0.0.0 --port 8080

# With custom host/port
python -m mcp_weather_server --mode sse --host localhost --port 3000
```

#### Streamable HTTP Mode
```bash
# Stateful mode (default)
python -m mcp_weather_server --mode streamable-http --host 0.0.0.0 --port 8080

# With debug logging
python -m mcp_weather_server --mode streamable-http --debug
```

### Adding New Tools

To add new weather or time-related tools:

1. Create a new tool handler in the appropriate file under `tools/`
2. Inherit from the `ToolHandler` base class
3. Implement the required methods (`get_name`, `get_description`, `call`)
4. Register the tool in `server.py`

## Dependencies

### Core Dependencies
- `mcp>=1.0.0` - Model Context Protocol implementation
- `httpx>=0.28.1` - HTTP client for API requests
- `python-dateutil>=2.8.2` - Date/time parsing utilities

### SSE Server Dependencies
- `starlette` - ASGI web framework
- `uvicorn` - ASGI server

### Development Dependencies
- `pytest` - Testing framework

## API Data Sources

This server uses free and open-source APIs:

### Weather Data: [Open-Meteo Weather API](https://open-meteo.com/)
- Free and open-source
- No API key required
- Provides accurate weather forecasts
- Supports global locations
- Historical and current weather data
- Comprehensive metrics (wind, precipitation, UV, visibility)

### Air Quality Data:
- Free and open-source
- No API key required
- Real-time air quality data
- Multiple pollutant measurements (PM2.5, PM10, O3, NO2, CO, SO2)
- Global coverage
- Health-based air quality indices

## Troubleshooting

### Common Issues

**1. City not found**
- Ensure city names are in English
- Try using the full city name or include country (e.g., "Paris, France")
- Check spelling of city names

**2. HTTP Server not accessible (SSE or Streamable HTTP)**
- Verify the server is running with the correct mode:
  - SSE: `python -m mcp_weather_server --mode sse`
  - Streamable HTTP: `python -m mcp_weather_server --mode streamable-http`
- Check firewall settings for the specified port
- Ensure all dependencies are installed: `pip install starlette uvicorn`
- Verify the correct endpoint:
  - SSE: `http://localhost:8080/sse` and `http://localhost:8080/messages/`
  - Streamable HTTP: `http://localhost:8080/mcp`

**3. MCP Client connection issues**
- Verify Python path in MCP client configuration
- Check that `mcp_weather_server` package is installed
- Ensure Python environment has required dependencies

**4. Date format errors**
- Use ISO 8601 format for dates: YYYY-MM-DD
- Ensure start_date is before end_date
- Check that dates are not too far in the future

### Error Responses

The server returns structured error messages:

```json
{
  "error": "Could not retrieve coordinates for InvalidCity."
}
```

