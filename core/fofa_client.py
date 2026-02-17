import aiohttp
import base64
import json


class FofaClient:
    def __init__(self, email, key):
        """
        初始化 FOFA 客户端
        :param email: FOFA 账号邮箱
        :param key: FOFA API Key
        """
        self.email = email
        self.key = key
        self.base_url = "https://fofa.info/api/v1/search/all"

    async def fetch_assets(self, query: str, size: int = 100):
        """
        从 FOFA 获取资产
        :param query: 查询语句 (如 domain="example.com" 或 org="阿里巴巴")
        :param size: 抓取数量
        :return: 经过清洗的 URL 列表
        """
        try:
            # 关键点：显式使用 utf-8 编码 query 字符串，防止公司名等中文报错
            qbase64 = base64.b64encode(query.encode('utf-8')).decode('utf-8')

            params = {
                "email": self.email,
                "key": self.key,
                "qbase64": qbase64,
                "size": size,
                "fields": "host"  # 我们只需要 host 字段 (包含 ip:port 或 domain)
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        content = await resp.json()

                        # 检查 FOFA 返回的逻辑错误
                        if content.get("error"):
                            print(f"[-] FOFA API 返回错误: {content.get('errmsg')}")
                            return []

                        # 提取结果列表
                        results = content.get("results", [])

                        # 格式化处理：确保所有结果都带有 http/https 前缀
                        formatted_assets = self._format_urls(results)
                        return formatted_assets

                    elif resp.status == 401:
                        print("[-] FOFA 认证失败：请检查 API Key 和 Email 是否正确")
                        return []
                    else:
                        print(f"[-] FOFA 请求异常，状态码: {resp.status}")
                        return []

        except Exception as e:
            print(f"[-] 资产采集过程发生异常: {e}")
            return []

    def _format_urls(self, hosts):
        """
        内部工具：将 FOFA 返回的原始 host 转换为标准 URL 格式
        """
        clean_urls = []
        for host in hosts:
            if not host:
                continue
            # 如果没有协议头，默认加上 http://
            if not host.startswith(('http://', 'https://')):
                # 简单判断：如果有 443 端口一般是 https
                if ":443" in host:
                    url = f"https://{host}"
                else:
                    url = f"http://{host}"
            else:
                url = host
            clean_urls.append(url)
        return list(set(clean_urls))  # 去重