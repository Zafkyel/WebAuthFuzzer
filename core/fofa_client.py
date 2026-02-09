import base64
import asyncio
import aiohttp
from typing import List, Dict


class FofaClient:
    """
    FOFA 资产采集模块
    亮点：异步高并发、自动 Base64 编码、结构化输出
    """

    def __init__(self, email: str, key: str):
        self.email = email
        self.key = key
        self.base_url = "https://fofa.info/api/v1/search/all"

    async def fetch_assets(self, query: str, size: int = 100) -> List[str]:
        """
        根据语法查询资产
        :param query: FOFA 查询语句，如 'app="Apache"'
        :param size: 获取条数
        """
        # 1. 对查询语句进行 Base64 编码
        qbase64 = base64.b64encode(query.encode()).decode()

        # 2. 构造请求参数
        params = {
            "email": self.email,
            "key": self.key,
            "qbase64": qbase64,
            "size": size,
            "fields": "host"  # 只取主机名/IP
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("error"):
                            print(f"[-] FOFA 错误: {data.get('errmsg')}")
                            return []

                        results = data.get("results", [])
                        print(f"[+] 成功从 FOFA 抓取到 {len(results)} 条资产")
                        return results
                    else:
                        print(f"[-] 请求失败，状态码: {response.status}")
                        return []
            except Exception as e:
                print(f"[-] 网络请求异常: {e}")
                return []


# 快速测试脚本
if __name__ == "__main__":
    # 这里仅作演示，正式环境请从 ConfigLoader 获取
    # test_client = FofaClient("your_email", "your_key")
    # asyncio.run(test_client.fetch_assets('domain="baidu.com"'))
    pass
