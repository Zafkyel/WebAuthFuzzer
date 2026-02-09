import yaml
import os


class ConfigLoader:
    def __init__(self, config_path="config/config.yaml"):
        # 自动定位到项目根目录下的配置文件
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = os.path.join(base_path, config_path)

    def get_fofa_key(self):
        try:
            if not os.path.exists(self.config_path):
                print(f"[-] 错误: 找不到配置文件 {self.config_path}")
                return "", ""  # 返回空字符串而不是 None

            with open(self.config_path, "r", encoding="utf-8") as f:
                conf = yaml.safe_load(f)
                if not conf or 'fofa' not in conf:
                    print("[-] 错误: config.yaml 格式不正确")
                    return "", ""
                return conf['fofa'].get('email', ""), conf['fofa'].get('key', "")
        except Exception as e:
            print(f"[-] 配置文件读取异常: {e}")
            return "", ""  # 确保始终返回两个值
