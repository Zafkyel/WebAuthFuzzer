import httpx

class AsyncReq:
    def __init__(self, timeout=10):
        self.timeout = timeout
        # 忽略 SSL 错误，这是扫描工具的刚需
        self.client = httpx.AsyncClient(verify=False, timeout=self.timeout)

    async def get_status(self, url):
        try:
            resp = await self.client.get(url)
            return resp.status_code, len(resp.content)
        except Exception:
            return None, 0