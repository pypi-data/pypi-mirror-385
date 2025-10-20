from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://restapi.amap.com/v3/weather/weatherInfo"
API_KEY = "6e1569803da7979b7fffab3efdf67649"

@mcp.tool()
async def get_alerts(city: str) -> str:
    """获取中国各城市的天气警报。

    Args:
        city: 城市信息（例如 北京、上海）
    """
    url = f"{NWS_API_BASE}?city=110101&key={API_KEY}"
    response = await make_nws_request(url)
    lives = response["lives"]

    return f"""
    北京天气情况
    天气：{lives[0]["weather"]}
    温度：{lives[0]["temperature"]}
    凤向：{lives[0]["winddirection"]}
    凤级：{lives[0]["windpower"]}
    温度：{lives[0]["temperature_float"]}
    """


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """向 NWS API 发送请求，并进行适当的错误处理。"""
    headers = {
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()