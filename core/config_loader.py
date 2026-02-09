import yaml
import os


class ConfigLoader:
    def __init__(self, config_path="config/config.yaml"):
        # 自动定位到项目根目录下的配置文件
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_path, config_path)

    def get_fofa_key(self):
        try:
            with open(self.config_path, "r") as f:
                conf = yaml.safe_load(f)
                return conf['fofa']['email'], conf['fofa']['key']
        except Exception as e:
            print(f"[-] 配置文件读取失败: {e}")
            return None, None