import requests
import aiohttp
from typing import Dict, Any, Optional, Tuple
import asyncio


class Client:
    """基础认证类，提供公共的 API key 认证和请求方法"""

    def __init__(self, api_key: str):
        self.base_url = "https://thirdparty.pixelarrayai.com"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    def _request(self, method: str, url: str, **kwargs) -> Tuple[Dict[str, Any], bool]:
        """统一的请求方法"""
        resp = requests.request(
            method, f"{self.base_url}{url}", headers=self.headers, **kwargs
        )
        if resp.status_code == 200 and resp.json().get("success") is True:
            return resp.json().get("data", {}), True
        return {}, False


class AsyncClient:
    def __init__(self, api_key: str):
        self.base_url = "https://thirdparty.pixelarrayai.com"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

    async def _request(self, method: str, url: str, **kwargs) -> Tuple[Dict[str, Any], bool]:
        async with aiohttp.ClientSession() as session:
            req_method = getattr(session, method.lower())
            async with req_method(
                f"{self.base_url}{url}", headers=self.headers, **kwargs
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success") is True:
                        return result.get("data", {}), True
                return {}, False
