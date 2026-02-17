import asyncio
from utils.request_client import RequestClient


class Dispatcher:
    def __init__(self):
        self.client = RequestClient()
        self.results = {
            "200": [],
            "301/302": [],
            "403": [],
            "404": [],
            "others": []
        }

    async def dispatch(self, url_list: list):
        """核心分发方法"""
        print(f"[*] 正在对 {len(url_list)} 个资产进行并发探测...")
        tasks = [self.client.check_status(url) for url in url_list]
        responses = await asyncio.gather(*tasks)

        for res in responses:
            if not res: continue

            status = str(res.get('status'))
            url = res.get('url')

            if status == "200":
                self.results["200"].append(url)
            elif status in ["301", "302"]:
                self.results["301/302"].append(url)
            elif status == "403":
                self.results["403"].append(url)
            elif status == "404":
                self.results["404"].append(url)
            else:
                self.results["others"].append(url)

        return self.results