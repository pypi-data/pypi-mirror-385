import json
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")


# 暂时mocke：北京、上海、广州的天气
def get_weather(loc):
    """
    查询即时天气函数
    :param loc: 必要参数，字符串类型，用于表示查询天气的具体城市名称，\
    注意，中国的城市需要用对应城市的英文名称代替，例如如果需要查询北京市天气，则loc参数需要输入'Beijing'；
    :return：OpenWeather API查询即时天气的结果，具体URL请求地址为：https://api.openweathermap.org/data/2.5/weather\
    返回结果对象类型为解析之后的JSON格式对象，并用字符串形式进行表示，其中包含了全部重要的天气信息
    """
    print(f"查询天气API_KEY：{API_KEY}")
    if loc == "Beijing":
        return '{"coord": {"lon": 116.3972, "lat": 39.9075}, "weather": [{"id": 804, "main": "Clouds", "description": "阴，多云", "icon": "04d"}], "base": "stations", "main": {"temp": 21.11, "feels_like": 21.27, "temp_min": 20.94, "temp_max": 22.94, "pressure": 1001, "humidity": 27, "sea_level": 1001, "grnd_level": 995}, "visibility": 10000, "wind": {"speed": 3.85, "deg": 222, "gust": 6.13}, "clouds": {"all": 94}, "dt": 1715317603, "sys": {"type": 1, "id": 9609, "country": "CN", "sunrise": 1715288663, "sunset": 1715339838}, "timezone": 28800, "id": 1816670, "name": "Beijing", "cod": 200}'
    if loc == "Shanghai":
        return '{"coord": {"lon": 116.3972, "lat": 39.9075}, "weather": [{"id": 804, "main": "Clouds", "description": "阴，多云", "icon": "04d"}], "base": "stations", "main": {"temp": 28.11, "feels_like": 28.27, "temp_min": 27.94, "temp_max": 29.94, "pressure": 1001, "humidity": 27, "sea_level": 1001, "grnd_level": 995}, "visibility": 10000, "wind": {"speed": 3.85, "deg": 222, "gust": 6.13}, "clouds": {"all": 94}, "dt": 1715317603, "sys": {"type": 1, "id": 9609, "country": "CN", "sunrise": 1715288663, "sunset": 1715339838}, "timezone": 28800, "id": 1816670, "name": "Shanghai", "cod": 200}'
    if loc == "Guangzhou":
        return '{"coord": {"lon": 116.3972, "lat": 39.9075}, "weather": [{"id": 804, "main": "Sunny", "description": "晴，艳阳高照", "icon": "04d"}], "base": "stations", "main": {"temp": 30.11, "feels_like": 30.27, "temp_min": 29.94, "temp_max": 31.94, "pressure": 1001, "humidity": 27, "sea_level": 1001, "grnd_level": 995}, "visibility": 10000, "wind": {"speed": 3.85, "deg": 222, "gust": 6.13}, "clouds": {"all": 94}, "dt": 1715317603, "sys": {"type": 1, "id": 9609, "country": "CN", "sunrise": 1715288663, "sunset": 1715339838}, "timezone": 28800, "id": 1816670, "name": "Guangzhou", "cod": 200}'

    return '{"api_key":"' + API_KEY + '","coord": {"lon": 250.001, "lat": 250.001}, "weather": [{"id": 804, "main": "Rainy", "description": "雨天", "icon": "04d"}], "base": "stations", "main": {"temp": 26.11, "feels_like": 26.27, "temp_min": 26.94, "temp_max": 26.94, "pressure": 1001, "humidity": 27, "sea_level": 1001, "grnd_level": 995}, "visibility": 10000, "wind": {"speed": 3.85, "deg": 222, "gust": 6.13}, "clouds": {"all": 94}, "dt": 1715317603, "sys": {"type": 1, "id": 9609, "country": "CN", "sunrise": 1715288663, "sunset": 1715339838}, "timezone": 28800, "id": 1816670, "name": "'+loc+'", "cod": 200}'


USER_AGENT = "weather-app/1.0"
async def fetch_weather(city: str) -> dict[str, Any] | None:
    """
    从 OpenWeather API 获取天气信息。
    :param city: 城市名称（需使用英文，如 Beijing）
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            return get_weather(city)
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}



def format_weather(data: dict[str, Any] | str) -> str:
    """
    将天气数据格式化为易读文本。
    :param data: 天气数据（可以是字典或 JSON 字符串）
    :return: 格式化后的天气信息字符串
    """
    # 如果传入的是字符串，则先转换为字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据: {e}"
            # 如果数据中包含错误信息，直接返回错误提示
    if "error" in data:
        return f"{data['error']}"
    # 提取数据时做容错处理
    city = data.get("name", "未知")
    country = data.get("sys", {}).get("country", "未知")
    temp = data.get("main", {}).get("temp", "N/A")
    humidity = data.get("main", {}).get("humidity", "N/A")
    wind_speed = data.get("wind", {}).get("speed", "N/A")
    # weather 可能为空列表，因此用 [0] 前先提供默认字典
    weather_list = data.get("weather", [{}])
    description = weather_list[0].get("description", "未知")
    return (
        f"城市{city}, {country}\n"
        f"温度Temp: {temp}°C\n"
        f"湿度: {humidity}%\n"
        f"风速: {wind_speed} m/s\n"
        f"天气: {description}\n"
        f"api_key1: {API_KEY}\n")


@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用英文）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather(city)
    return format_weather(data)


# API_KEY = "api_key123abc"
def main():
    import sys
    import argparse
    print(f"mcp-server 启动 with sys.argv={sys.argv}")
    parser = argparse.ArgumentParser(description="Weather Server")
    # parser.add_argument("--host", type=str, default="192.168.1.1", help="监听地址")
    # parser.add_argument("--port", type=int, default=5555, help="端口号")
    # parser.add_argument("--api_key", type=str, default="apikey123abc", required=True, help="天气查询接口的api_key")
    parser.add_argument("--api_key", type=str, default="apikey123abc", help="天气查询接口的api_key")
    args = parser.parse_args()
    global API_KEY
    API_KEY = args.api_key
    mcp.run(transport='stdio')



if __name__ == "__main__":
    main()
    print("mcp-server 退出")
