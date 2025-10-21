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


@mcp.tool(description="Fetch all currency conversion rates for a given base currency.")
def get_all_conversion_rates(base_currency: str) -> dict:
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
        },
    )
    response.raise_for_status()
    data = response.json()
    return data


@mcp.tool(description="Convert a given amount of currency to a target currency.")
def convert_currency(amount: float, base_currency: str, target_currency: str) -> dict:
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
    conversion_rate = data["rates"][target_currency]
    converted_amount = amount * conversion_rate
    return {
        "converted_amount": converted_amount,
        "conversion_rate": conversion_rate,
        "base_currency": base_currency,
        "target_currency": target_currency,
        "rate_date": data["date"],
    }


def main() -> None:
    """Run the currency MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
