# WebAuthFuzzer 🚀

> **基于响应特征驱动的智能化 Web 资产测绘与未授权探测系统**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Developing-orange.svg)]()

WebAuthFuzzer 是一款针对企业级攻击面管理的自动化安全工具。它能从一个公司名称开始，自动化完成资产搜集、存活探测，并针对 **403 Forbidden** 及 **未授权 API** 进行智能化绕过与深度探测。

---

## 🛠️ 系统架构

本项目采用异步 I/O 架构，确保在实战环境下的高并发处理能力。



- **Recon Module**: 集成 FOFA API 与 Subfinder，实现被动+主动的资产画像。
- **Smart Dispatcher**: 根据响应状态码（200/403/30x）动态路由至不同的探测算子。
- **Bypass Engine**: 自动化执行 Header 注入、路径穿越及权限校验绕过。
- **Reporter**: 自动生成包含漏洞复现证据的 HTML 可视化报告。

---

## 📂 项目目录

```text
WebAuthFuzzer/
├── config/             # 配置文件 (API Key, 策略配置)
├── core/               # 核心引擎 (Recon, Dispatcher, Fuzzer)
├── data/               # 存放 Fuzzing 字典与扫描缓存
├── utils/              # 异步请求封装、日志管理
├── reports/            # 报告模板与输出目录
├── main.py             # 统一入口
└── requirements.txt    # 依赖库清单
```
⚡ 快速开始

1. 环境克隆与安装
```bash
git clone https://github.com/Zafkyel/WebAuthFuzzer.git
cd WebAuthFuzzer
pip install -r requirements.txt 
```

2. 配置 API
编辑 config/config.yaml:
```yaml
fofa:
  email: "your_email"
  key: "your_key"
```

3. 运行探测
```bash
python main.py -d example.com
```

⚖️ 免责声明
本工具仅用于安全研究与授权测试。用户因使用本工具导致的任何法律纠纷，作者不承担任何责任。


---