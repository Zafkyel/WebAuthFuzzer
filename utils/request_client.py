import aiohttp
import asyncio


class RequestClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def check_status(self, url: str) -> dict:
        """探测 URL 状态码"""
        if not url.startswith('http'):
            url = f"http://{url}"

        try:
            # 使用 ssl=False 忽略证书错误，allow_redirects=True 跟踪跳转
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url, timeout=5, ssl=False, allow_redirects=True) as response:
                    return {"url": url, "status": response.status}
        except Exception:
            return {"url": url, "status": 0}  # 0 代表连接失败