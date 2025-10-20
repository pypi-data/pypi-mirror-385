from typing import Optional
from mcp.server.fastmcp import FastMCP
# 初始化FastMCP服务器
mcp = FastMCP("hello-world")
@mcp.tool()
async def hello(name: Optional[str] = None) -> str:
    """
    返回一个简单的问候语。
    Args:
        name: 要问候的名称（可选）
    Returns:
        str: 问候语
    """
    if name:
        return f"Hello, {name}!"
    else:
        return "Hello, World!"
def main():
    mcp.run(transport='stdio')
if __name__ == "__main__":
    # 初始化并运行服务器
    mcp.run(transport='stdio')