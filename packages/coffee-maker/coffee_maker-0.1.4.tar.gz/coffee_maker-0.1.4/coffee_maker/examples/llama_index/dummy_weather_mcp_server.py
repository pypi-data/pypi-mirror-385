from mcp.server.fastmcp import FastMCP

PORT = 3001


def main(port: int = PORT) -> FastMCP:
    """Configures and runs the MCP server."""
    # Create an MCP server
    mcp = FastMCP("Weather Service", port=port)

    @mcp.tool()
    def get_weather(location: str) -> str:
        """Get the current weather for a specified location."""
        return f"Weather in {location}: Sunny, 72°F"

    @mcp.resource("weather://{location}")
    def weather_resource(location: str) -> str:
        """Provide weather data as a resource."""
        return f"Weather data for {location}: Sunny, 72°F"

    @mcp.prompt()
    def weather_report(location: str) -> str:
        """Create a weather report prompt."""
        return f"""You are a weather reporter. Weather report for {location}?"""

    # Explicitly run the server with the 'sse' transport protocol.
    print(f"MCP server starting with SSE transport on port {PORT}...")
    mcp.run(transport="sse")
    return mcp


# Run the server
if __name__ == "__main__":
    main()
