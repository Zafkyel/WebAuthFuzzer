import os
import time
import json


class Logger:
    def __init__(self):
        self.result_dir = "data/results"
        # 按照本次运行时间创建独立文件夹，方便区分多次扫描
        self.run_id = time.strftime('%Y%m%d_%H%M%S')
        self.current_run_dir = os.path.join(self.result_dir, self.run_id)

        if not os.path.exists(self.current_run_dir):
            os.makedirs(self.current_run_dir)

        # 分别定义成功和失败的文件路径
        self.success_file = os.path.join(self.current_run_dir, "success_bypass.json")
        self.failed_file = os.path.join(self.current_run_dir, "failed_attempts.json")
        self.summary_file = os.path.join(self.current_run_dir, "summary.json")

    def log_result(self, url, payload, status, is_success=False):
        """统一记录结果，根据 is_success 存入不同文件"""
        data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "url": url,
            "payload": payload,
            "status": status
        }

        target_file = self.success_file if is_success else self.failed_file

        with open(target_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def log_summary(self, summary_data):
        """记录最终统计信息"""
        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=4)
        print(f"\n[+] 扫描报告已生成在: {self.current_run_dir}")


# 实例化
logger = Logger()