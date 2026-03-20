# 🚀 WebAuthFuzzer v1.0.26 (Stable)

> **基于异步协程的自动化 Web 资产搜集与鉴权绕过测试流水线**

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Environment](https://img.shields.io/badge/Environment-Kali%20/%20macOS-orange.svg)

---

## 🎨 Tool Preview

      __      __      ___.                         __  .__     
     /  \    /  \ ____\_ |__ _____   __ __  __ ___/  |_|  |__  
     \   \/\/   // __ \| __ \__  \ |  |  \|  |  \   __\  |  \ 
      \        /\  ___/| \_\ \/ __ \|  |  /|  |  /|  | |   Y  \
       \__/\  /  \___  >___  (____  /____/ |____/ |__| |___|  /
            \/       \/    \/     \/                        \/ 

               >> Offensive Security & Auth-Bypass Pipeline <<

---

## 🌟 核心特性

* **⚡ 异步并发引擎**：基于 `aiohttp` 与 `asyncio`，支持百级并发，扫描效率提升 10 倍。
* **🎯 精准资产搜集**：深度集成 FOFA API，支持域名、公司名及自定义语法批量采集。
* **📂 智能递归探测**：自动化目录爆破与参数 Fuzz，实时记录有效的隐藏接口。
* **🛡️ 鉴权绕过 (Bypass)**：内置多种 403/405 绕过策略，自动尝试头部注入与路径重写。
* **📈 速率动态控制**：
    * **极速模式** (100并发/0延时)：适用于内网安全评估。
    * **均衡模式** (40并发/100ms延时)：实战推荐，兼顾效率与隐蔽。
    * **隐蔽模式** (10并发/500ms延时)：规避基础 WAF 拦截。
* **📊 自动化报表**：任务结束后自动生成可视化 TXT 汇总报告，扫描成果一目了然。

---

## 🛠️ 快速开始

### 1. 环境克隆
```bash
git clone [https://github.com/your-username/WebAuthFuzzer.git](https://github.com/your-username/WebAuthFuzzer.git)
cd WebAuthFuzzer
```

2. 安装依赖
pip3 install -r requirements.txt

3. 配置 API
编辑 config/config.yaml，填入你的 FOFA 密钥：

```YAML
fofa:
  email: "your_email@example.com"
  key: "your_fofa_api_key"
 ```
4. 运行工具
```Bash
python3 main.py
```
📁 目录结构说明
```
core/ : 扫描引擎逻辑 (Config, Scanner, Bypasser)

utils/ : 工具组件 (Logger, Client, OutputManager)

data/ : 存放 Payload 字典及扫描结果数据

reports/ : 自动生成的扫描汇总报告目录
```

⚠️ 免责声明
本工具仅用于合规的渗透测试、安全研究及教学用途。用户在使用本工具进行测试时，应遵守当地法律法规。因不当使用导致的任何后果由使用者本人承担。

Developed with ❤️ for the Security Community.