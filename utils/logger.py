import os
import time
import json


class Logger:
    def __init__(self):
        self.result_dir = "data/results"
        self.run_id = time.strftime('%Y%m%d_%H%M%S')
        self.current_run_dir = os.path.join(self.result_dir, self.run_id)
        os.makedirs(self.current_run_dir, exist_ok=True)

        self.inventory_file = os.path.join(self.current_run_dir, "full_inventory.json")
        self.fingerprint_file = os.path.join(self.current_run_dir, "fingerprints.json")
        self.bypass_file = os.path.join(self.current_run_dir, "bypass_details.json")
        self.summary_file = os.path.join(self.current_run_dir, "summary_report.json")

    def log_inventory(self, data):
        with open(self.inventory_file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

    def log_fingerprints(self, data):
        with open(self.fingerprint_file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

    def log_bypass_detail(self, url, payload, status, is_success):
        entry = {"time": time.strftime('%H:%M:%S'), "url": url, "payload": payload, "status": status,
                 "res": "SUCCESS" if is_success else "FAIL"}
        with open(self.bypass_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    def log_summary(self, summary):
        # 对齐逻辑：计算中文字符宽度
        def get_width(s):
            return sum(2 if '\u4e00' <= c <= '\u9fff' else 1 for c in str(s))

        def draw_line(label, value):
            line_content = f" {label}: {value}"
            padding = 46 - get_width(line_content)
            return f"║{line_content}{' ' * padding}║"

        res = summary['results']
        print("\n" + "=" * 48)
        print(f"║{'项目扫描任务总结':^40}║")  # 标题居中
        print("=" * 48)
        print(draw_line("目标关键字", summary['target']))
        print(draw_line("资产总数", res['total']))
        print(draw_line("活跃(200)", res['200']))
        print(draw_line("受限(403)", res['403']))
        print(draw_line("成功绕过", res.get('bypassed', 0)))
        print("=" * 48)

        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=4)


logger = Logger()