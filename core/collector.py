import asyncio
import base64
import aiohttp
from utils.logger import logger


class FOFACollector:
    def __init__(self, email, key):
        self.email = email
        self.key = key
        self.base_url = "https://fofa.info/api/v1/search/all"

    def build_query(self, mode, value):
        if mode == "1": return f'domain="{value}"'
        if mode == "2": return f'org="{value}" || icp="{value}"'
        if mode == "3": return value
        return f'host="{value}"'

    async def fetch(self, query, size=1000):
        qbase64 = base64.b64encode(query.encode()).decode()
        all_raw = []
        page = 1

        # 强制小粒度采集，防止大 size 被服务端截断
        page_size = 50

        logger.info(f"[*] 目标总量: {size} | 正在尝试突破权限采集...")

        try:
            async with aiohttp.ClientSession() as session:
                while len(all_raw) < size:
                    api_url = f"{self.base_url}?email={self.email}&key={self.key}&qbase64={qbase64}&size={page_size}&page={page}"

                    async with session.get(api_url, timeout=20) as resp:
                        if resp.status != 200:
                            logger.error(f"[-] 接口响应异常: {resp.status}")
                            break

                        data = await resp.json()
                        if data.get("error"):
                            # 如果报错 [-700] 或权限问题，这里会打印
                            logger.error(f"[-] FOFA 提示: {data.get('errmsg')}")
                            break

                        results = data.get("results", [])
                        total_in_fofa = data.get("size", 0)

                        if not results:
                            # 关键点：如果第一页都没满就没了，说明真是权限封顶了
                            logger.warning(
                                f"[!] 无法获取更多数据。当前已获取: {len(all_raw)} / 全球总数: {total_in_fofa}")
                            break

                        all_raw.extend(results)
                        logger.info(f"[+] 进度: {len(all_raw)}/{size} (Page: {page})")

                        # 如果已经拿到了 FOFA 库里的所有数据，提前退出
                        if len(all_raw) >= total_in_fofa:
                            break

                        page += 1
                        await asyncio.sleep(1.2)  # 稍微慢一点，避免触发 API 频率限制

                # 格式化 URL
                formatted = []
                for item in all_raw:
                    try:
                        host, port = item[0], str(item[-1])
                        url = host if "://" in host else (
                            f"https://{host}" if port == "443" else f"http://{host}:{port}")
                        formatted.append(url)
                    except:
                        continue

                final_res = list(set(formatted))[:size]
                logger.success(f"[!] 最终成功导出资产: {len(final_res)} 条")
                return final_res

        except Exception as e:
            logger.error(f"[-] 采集器崩溃: {e}")
            return []