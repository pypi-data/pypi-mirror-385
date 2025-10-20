from .server import serve


def main():
    """MCP Reddit Server - Reddit functionality for MCP"""
    import asyncio

    asyncio.run(serve())


if __name__ == "__main__":
    main()
