import aiohttp
import asyncio


class RequestClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def check_status(self, url: str, custom_headers: dict = None) -> dict:
        # 深度拷贝默认 Header，防止互相干扰
        headers = self.headers.copy()
        if custom_headers:
            headers.update(custom_headers)

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                # allow_redirects=False 非常重要，这样我们能看到真实的 403 还是跳转
                async with session.get(url, timeout=5, ssl=False, allow_redirects=False) as response:
                    return {
                        "url": url,
                        "status": response.status,
                        "payload": custom_headers if custom_headers else url
                    }
        except Exception as e:
            return {"url": url, "status": 0, "payload": url, "error": str(e)}