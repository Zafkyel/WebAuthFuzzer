import os
import sys
import random


class Logger:
    def __init__(self):
        # 1. 颜色与样式定义 (保持高对比度)
        self.CYAN = "\033[96m"
        self.PURPLE = "\033[95m"
        self.BLUE = "\033[94m"
        self.GREEN = "\033[92m"
        self.YELLOW = "\033[93m"
        self.RED = "\033[91m"
        self.BOLD = "\033[1m"
        self.END = "\033[0m"

        # 2. 骚话池 (Cyber-Quotes) - 保留你的随机语录功能
        self.quotes = [
            "Everything is a target.",
            "Information wants to be free.",
            "The quieter you become, the more you are able to hear.",
            "Hack the planet.",
            "Security is an illusion.",
            "Access Denied is just a temporary state.",
            "Tracing assets... 1%... 99%... Done."
        ]

        # 3. 启动自检并喷绘第一版 Banner
        self._show_art()

    def _show_art(self):
        # 解决 TERM 变量报错
        if not os.environ.get("TERM"):
            os.environ["TERM"] = "xterm-256color"

        # 自动清屏
        os.system('cls' if os.name == 'nt' else 'clear')

        # --- 回归第一版经典 Slant 字体 ---
        art = r"""
{cy}{bd}
      __      __      ___.                         __  .__     
     /  \    /  \ ____\_ |__ _____   __ __  __ ___/  |_|  |__  
     \   \/\/   // __ \| __ \\__  \ |  |  \|  |  \   __\  |  \ 
      \        /\  ___/| \_\ \/ __ \|  |  /|  |  /|  | |   Y  \\
       \__/\  /  \___  >___  (____  /____/ |____/ |__| |___|  /
            \/       \/    \/     \/                        \/ 
{pu}               >> Offensive Security & Auth-Bypass Pipeline <<
{ed}{bl}
    [ 版本 ] : v1.0.26 (Stable)
    [ 模块 ] : FOFA / DirScan / ParamFuzz / 403Bypass
{ed}
        """.format(
            cy=self.CYAN, bd=self.BOLD, pu=self.PURPLE,
            ed=self.END, bl=self.BLUE, ye=self.YELLOW
        )
        print(art)

        # 打印随机语录
        quote = random.choice(self.quotes)
        print(f" {self.PURPLE}⚡ {self.BOLD}{quote}{self.END}\n")

    def banner(self):
        """兼容 main.py 的调用，防止报错"""
        pass

    def info(self, msg):
        print(f" {self.BLUE}[*]{self.END} {msg}")

    def success(self, msg):
        print(f" {self.GREEN}[+]{self.END} {msg}")

    def warning(self, msg):
        print(f" {self.YELLOW}[!]{self.END} {msg}")

    def error(self, msg):
        print(f" {self.RED}[-]{self.END} {msg}")

    def print_url(self, url, status="200"):
        color = self.GREEN if status == "200" else self.BLUE
        print(f" {color}{url}{self.END}")


# 全局实例化
logger = Logger()