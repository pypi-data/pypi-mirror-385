from reddit_mcp.tools import tools
from pydantic import TypeAdapter
import json


def main():
    schemas = {tool.__name__: TypeAdapter(tool).json_schema() for tool in tools}
    print(json.dumps(schemas, indent=2))


if __name__ == "__main__":
    main()
