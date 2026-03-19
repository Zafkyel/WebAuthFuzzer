import os
import yaml
from utils.logger import logger

class ConfigLoader:
    def __init__(self):
        # 1. 定位项目根目录 (WebAuthFuzzer/)
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 2. 锁定配置文件路径
        self.config_path = os.path.join(self.base_path, "config", "config.yaml")
        # 3. 锁定字典文件夹路径 (修复属性缺失错误)
        self.payload_dir = os.path.join(self.base_path, "data", "payloads")

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.error(f"配置文件不存在: {self.config_path}")
            return {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                return content if content else {}
        except Exception as e:
            logger.error(f"YAML 解析失败: {e}")
            return {}

    def load_dict(self, filename):
        """
        统一字典加载入口
        """
        path = os.path.join(self.payload_dir, filename)
        if not os.path.exists(path):
            logger.warning(f"字典文件不存在: {path}")
            return []
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                # 过滤空行和注释
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except Exception as e:
            logger.error(f"读取字典 {filename} 失败: {e}")
            return []

# 实例化单例供全局调用
config_loader = ConfigLoader()