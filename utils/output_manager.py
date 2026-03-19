import os
import time


class OutputManager:
    """
    结果输出模块 (核心功能 5)
    功能：强制 5 路隔离存储，支持秒级目录
    """

    def __init__(self, target):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.folder_name = f"{self.timestamp}_{target.replace('.', '_')}"
        self.output_path = os.path.join(self.base_dir, "data", "results", self.folder_name)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # 你的 5 个指定分类
        self.file_map = {
            "alive": "01_alive_200.txt",  # 1. 存活资产
            "recursive": "02_dir_scanned.txt",  # 2. 目录扫描后的资产
            "others": "03_3xx_4xx_assets.txt",  # 3. 3xx 和 4xx 资产
            "fuzz": "04_fuzz_params.txt",  # 4. Fuzz 成功参数的 URL
            "bypass": "05_bypass_success.txt"  # 5. 403/405 绕过的 URL
        }

    def save(self, category, data):
        """通用保存接口"""
        if not data: return
        filename = self.file_map.get(category)
        if not filename: return

        file_full_path = os.path.join(self.output_path, filename)
        if isinstance(data, str): data = [data]

        with open(file_full_path, "a", encoding="utf-8") as f:
            for item in data:
                f.write(item.strip() + "\n")