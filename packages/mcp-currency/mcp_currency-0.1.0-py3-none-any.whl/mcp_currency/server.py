from fastmcp import FastMCP
import httpx

API_URL = "https://api.frankfurter.dev/v1/latest"


mcp = FastMCP(
    name="Currency MCP Server",
    instructions="A Model Context Protocol server that provides tools to fetch and chart currency data.",
)


@mcp.tool(
    description="Fetch the latest currency conversion rate for a given currency pair."
)
def get_currency_conversion_rate(base_currency: str, target_currency: str) -> dict:
    # Documentation: https://frankfurter.dev/
    # Response example:
    # {
    #     "base": "USD",
    #     "date": "2025-10-20",
    #     "rates": {
    #         "AUD": 1.5414,
    #         "BGN": 1.6781,
    #         "BRL": 5.4064,
    #         "CAD": 1.4044,
    #         "...": "..."
    #     }
    # }
    response = httpx.get(
        API_URL,
        params={
            "base": base_currency,
            "symbols": target_currency,
        },
    )
    response.raise_for_status()
    data = response.json()
    return data


def main() -> None:
    """Run the currency MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
