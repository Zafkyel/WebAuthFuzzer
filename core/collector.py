import base64
import json
from utils.request_client import request_client
from utils.logger import logger


class FOFACollector:
    """
    FOFA 资产搜集模块
    功能：支持 3 种搜索模式，返回干净的 URL 列表
    """

    def __init__(self, email, key):
        self.email = email
        self.key = key
        self.base_url = "https://fofa.info/api/v1/search/all"

    def build_query(self, mode, value):
        if mode == "1":  # 域名模式
            query = f'domain="{value}"'
        elif mode == "2":  # 公司/ICP模式
            query = f'org="{value}" || icp="{value}"'
        elif mode == "3":  # 原生语法模式
            query = value
        else:
            query = f'host="{value}"'
        return query

    async def fetch(self, query, size=100):
        q_base64 = base64.b64encode(query.encode()).decode()
        url = f"{self.base_url}?email={self.email}&key={self.key}&qbase64={q_base64}&size={size}&fields=protocol,host"

        logger.info(f"正在请求 FOFA API: {query}")
        resp, content = await request_client.fetch(url, timeout=15)

        if not resp or resp.status != 200:
            logger.error("FOFA API 请求失败，请检查 Key 或网络。")
            return []

        try:
            data = json.loads(content)
            results = data.get("results", [])
            urls = []
            for protocol, host in results:
                if protocol:
                    urls.append(f"{protocol}://{host}")
                else:
                    # 默认补全 https，由 Dispatcher 进一步验证
                    urls.append(f"https://{host}")
            return list(set(urls))
        except Exception as e:
            logger.error(f"解析 FOFA 数据异常: {e}")
            return []