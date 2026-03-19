import hashlib


class Deduplicator:
    """
    智能去重模块 (核心功能 2)
    功能：URL去重 + 响应哈希去重
    """

    def __init__(self):
        self.seen_urls = set()
        self.seen_hashes = set()

    def is_new_url(self, url):
        u = url.strip().lower().rstrip('/')
        if u not in self.seen_urls:
            self.seen_urls.add(u)
            return True
        return False

    def is_new_content(self, html):
        if not html: return False
        # 预处理：去掉空格和换行，只取前 5000 字符计算 Hash，防止动态生成的 Token 干扰
        clean_html = "".join(html.split())[:5000]
        h = hashlib.md5(clean_html.encode(errors='ignore')).hexdigest()

        if h not in self.seen_hashes:
            self.seen_hashes.add(h)
            return True
        return False


deduplicator = Deduplicator()