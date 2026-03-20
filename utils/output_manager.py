import os
import datetime
import random
import string


class OutputManager:
    def __init__(self, target):
        self.target = target
        self.start_time = datetime.datetime.now()

        # 1. 文件夹名唯一化：时间戳 + 域名 + 4位随机字符
        rand_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        self.folder_name = f"{self.start_time.strftime('%Y%m%d_%H%M%S')}_{target.replace('.', '_')}_{rand_id}"

        # 2. 路径脱敏：仅在内部计算绝对路径，外部输出只显示相对路径
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 原始数据结果存放地 (data/results/xxx)
        self.results_path = os.path.join(self.base_dir, "data", "results", self.folder_name)
        # 汇总报告存放地 (reports/)
        self.reports_base_path = os.path.join(self.base_dir, "reports")

        # 3. 文件名描述增强：1234 后面加上具体含义
        self.file_map = {
            "1": "1_initial_alive_targets.txt",  # 初始存活资产
            "2": "2_discovered_directories.txt",  # 扫描发现的目录
            "3": "3_status_info_3xx_4xx.txt",  # 状态码异常信息
            "4": "4_fuzz_success_payloads.txt",  # Fuzz 成功的有效路径
            "bypass": "5_bypass_results.txt"
        }
        self.cache = {k: set() for k in self.file_map.keys()}
        self.dir_created = False

    def _ensure_dir(self):
        """空文件夹保护：只有真正调用 save 时才创建 data/results 目录"""
        if not self.dir_created:
            os.makedirs(self.results_path, exist_ok=True)
            self.dir_created = True

    def save(self, key, val):
        if key not in self.file_map or val in self.cache[key]: return
        self.cache[key].add(val)
        self._ensure_dir()

        file_path = os.path.join(self.results_path, self.file_map[key])
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"{val}\n")

    def generate_report(self, mode_name):
        """
        生成脱敏汇总报告：
        1. 报告不再存放在 data/results/ 下。
        2. 报告统一存放在项目根目录的 reports/ 目录下。
        3. 报告命名规则：Report_域名_时间戳.txt
        """
        c = {k: len(v) for k, v in self.cache.items()}

        # 如果没有任何发现（2号和4号为空），则判定为无效扫描
        if c.get('2', 0) == 0 and c.get('4', 0) == 0:
            print(f"\n [!] 任务结束: {self.target} 未发现有效敏感路径，跳过报告生成。")
            return

        finish_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 报告文本内容 (ASCII 工业风)
        report_content = f"""
+-------------------------------------------------------+
|             WEBAUTHFUZZER SCAN SUMMARY                |
+-------------------------------------------------------+
  Target Context : {self.target}
  Finish Time    : {finish_time_str}
  Scan Mode      : {mode_name}
+-------------------------------------------------------+
  [1] Initial Assets   : {c.get('1', 0)}
  [2] Dirs Discovered  : {c.get('2', 0)}
  [3] Status Info      : {c.get('3', 0)}
  [4] Fuzz Success     : {c.get('4', 0)}
+-------------------------------------------------------+
[*] Data Files    : data/results/{self.folder_name}/
"""
        # 1. 打印到控制台 (脱敏路径)
        print(report_content)

        # 2. 确保 reports 目录存在
        os.makedirs(self.reports_base_path, exist_ok=True)

        # 3. 按照命名规则生成报告文件
        report_filename = f"Report_{self.target}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt"
        report_full_path = os.path.join(self.reports_base_path, report_filename)

        with open(report_full_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        # 4. 控制台最后提示 (脱敏路径)
        print(f"[*] 汇总报告已归档至: reports/{report_filename}")