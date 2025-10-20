<div align="center">
  <img src="https://raw.githubusercontent.com/UnifiedOffer/mcpserver/main/docs/assets/logo.png" alt="UOP Logo" width="120" height="120">

  # uop-mcp-server

  mcp-name: com.unifiedoffer/mcp-server

  Universal MCP Server for AI-powered e-commerce integration

  [![PyPI version](https://img.shields.io/pypi/v/uop-mcp-server.svg)](https://pypi.org/project/uop-mcp-server/)
  [![Python](https://img.shields.io/pypi/pyversions/uop-mcp-server.svg)](https://pypi.org/project/uop-mcp-server/)
  [![Downloads](https://img.shields.io/pypi/dm/uop-mcp-server.svg)](https://pypi.org/project/uop-mcp-server/)
  [![License](https://img.shields.io/pypi/l/uop-mcp-server.svg)](https://github.com/UnifiedOffer/mcpserver/blob/main/LICENSE)
  [![MCP](https://img.shields.io/badge/MCP-v2024--11--05-blue)](https://modelcontextprotocol.io)

</div>

Connect AI applications to Shopify, WooCommerce, and Shopware 6 with automatic discount generation.

## Installation

```bash
pip install uop-mcp-server
```

## Quick Start

```python
from uop_mcp_server import UOPMCPClient

# Create client
client = UOPMCPClient("YOUR_API_KEY")

# Search products
products = client.search_products("laptop", limit=10)

# Generate affiliate links
links = client.generate_links([product_id1, product_id2])

# Negotiate price
offer = client.negotiate_price(product_id, 15)  # 15% discount

# Context manager (auto-close)
with UOPMCPClient("YOUR_API_KEY") as client:
    products = client.search_products("laptop")
```

## Async Support

```python
import asyncio
from uop_mcp_server import UOPMCPClient

async def main():
    async with UOPMCPClient("YOUR_API_KEY") as client:
        products = await client.search_products_async("laptop")
        print(products)

asyncio.run(main())
```

## Features

- **Product Search**: Query products across connected e-commerce platforms
- **Affiliate Links**: Generate trackable links with automatic discounts
- **Price Negotiation**: AI-powered price negotiation within merchant rules
- **Thread Management**: Persistent conversations with context
- **Multi-Platform**: Shopify, WooCommerce, Shopware 6 support
- **Async/Await**: Full async support with httpx

## API Key

Get your free API key at [https://unifiedoffer.com](https://unifiedoffer.com)

## Documentation

- [Full Documentation](https://unifiedoffer.com/docs)
- [MCP Specification](https://modelcontextprotocol.io)
- [API Reference](https://unifiedoffer.com/mcp)

## License

MIT
