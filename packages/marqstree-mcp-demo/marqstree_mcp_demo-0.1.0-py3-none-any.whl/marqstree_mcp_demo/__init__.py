from mcp.server.fastmcp import Context, FastMCP
mcp = FastMCP("Demo")

@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport='stdio')