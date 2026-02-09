from utils.request_client import RequestClient
import asyncio


# core/dispatcher.py

class Dispatcher:
    def __init__(self):
        self.client = RequestClient()
        self.results = {
            "200": [],
            "403": [],
            "others": []
        }

    async def dispatch(self, url_list: list):
        print(f"[*] 正在对 {len(url_list)} 个资产进行存活验证...")

        tasks = [self.client.check_status(url) for url in url_list]
        responses = await asyncio.gather(*tasks)

        for res in responses:
            if res is None: continue  # 预防性检查

            status = str(res.get('status', 0))
            url = res.get('url', 'Unknown')

            if status == "200":
                self.results["200"].append(url)
            elif status == "403":
                self.results["403"].append(url)
            elif status != "0":
                self.results["others"].append(url)

        print(f"[+] 验证完成: 200({len(self.results['200'])}), 403({len(self.results['403'])})")

        # --- 关键：必须加上这一行 ---
        return self.results