# 🎯 Stock Investment Decision Assistant

基于DIKW（数据-信息-知识-智慧）框架的智能股票投资决策辅助系统，为8只A股提供完整的投资建议。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/gorun78/stock-investment-assistant)](https://github.com/gorun78/stock-investment-assistant/stargazers)

## 📊 监控的8只A股

| 股票名称 | 代码 | 所属板块 | 风险等级 |
|----------|------|----------|----------|
| 科创信息 | 300730.SZ | 信息技术 | 中等 |
| 赛恩斯 | 688480.SS | 环保工程 | 低 |
| 景嘉微 | 300474.SZ | 半导体 | 高 |
| 深信服 | 300454.SZ | 网络安全 | 高 |
| 科大讯飞 | 002230.SZ | 人工智能 | 中等 |
| 万兴科技 | 300624.SZ | 软件服务 | 中等 |
| 威胜信息 | 688100.SS | 智能电网 | 低 |
| 超图软件 | 300036.SZ | 地理信息 | 低 |

## 🏗️ DIKW框架实现

### 1. 数据层 (Data)
- **功能**: 实时获取股票价格数据
- **数据源**: 新浪财经API
- **获取指标**: 当前价、开盘价、最高价、最低价、成交量、涨跌幅
- **频率**: 实时获取

### 2. 信息层 (Information)
- **功能**: 数据转化为有意义的信息
- **分析内容**:
  - 市场情绪分析（涨跌比例、平均涨跌）
  - 板块轮动分析（最强板块识别）
  - 风险收益特征分析
  - 市场趋势判断

### 3. 知识层 (Knowledge)
- **功能**: 信息提炼为可行动的知识
- **生成内容**:
  - 投资策略选择（激进/稳健/保守）
  - 股票筛选和分类
  - 投资组合构建
  - 风险控制规则
  - 择时策略建议

### 4. 智慧层 (Wisdom)
- **功能**: 知识升维为系统智慧和价值判断
- **生成内容**:
  - 系统理解（投资系统多要素交互）
  - 价值判断（市场展望、核心判断）
  - 未来决策（短/中/长期操作计划）
  - 个性化建议（立即行动、定期检查）

## 🚀 快速开始

### 安装依赖
```bash
pip install requests
```

### 运行程序
```bash
# 方式1: 运行主程序（交互式）
python stock_investment_assistant_main.py

# 方式2: 直接使用类
python -c "
from stock_investment_assistant import DIKWStockAssistant
assistant = DIKWStockAssistant(user_risk_profile='稳健型', investment_amount=100000)
report = assistant.generate_complete_report()
assistant.display_summary_report()
"
```

### 程序交互示例
```
🚀 股票投资决策辅助系统 v1.0
基于DIKW框架: 数据→信息→知识→智慧
============================================================

📝 请配置您的投资偏好:
1. 激进型 (高风险高收益)
2. 稳健型 (中等风险稳健增长)
3. 保守型 (低风险保值增值)
请选择(1/2/3, 默认2): 2

请输入投资金额(元, 默认100000): 100000

============================================================
🎯 股票投资决策辅助系统启动
📊 用户配置: 稳健型 | 投资金额: ¥100,000
============================================================

📈 数据层: 正在获取实时股票数据...
  ✓ 科创信息(300730.SZ): ¥36.89 (-0.88%)
  ✓ 赛恩斯(688480.SS): ¥75.82 (+1.12%)
  ✓ 景嘉微(300474.SZ): ¥144.16 (+2.74%)
  ✓ 深信服(300454.SZ): ¥128.98 (+2.28%)
  ✓ 科大讯飞(002230.SZ): ¥46.33 (+2.75%)
  ✓ 万兴科技(300624.SZ): ¥120.94 (-0.09%)
  ✓ 威胜信息(688100.SS): ¥61.39 (-1.56%)
  ✓ 超图软件(300036.SZ): ¥18.46 (+0.05%)
✅ 数据层完成: 获取到 8 只股票数据

📊 信息层: 正在分析市场信息...
  📈 市场情绪: 震荡整理
  📊 涨跌比例: 5涨/3跌 (62.5%上涨)
  🎯 最强板块: AI (+2.75%)
  📉 平均涨跌: +0.80%
✅ 信息层完成: 市场分析报告生成

🧠 知识层: 正在生成投资知识...
  🎯 适用策略: 稳健型
  📊 目标收益: 年化10-15%
  🛡️  最大回撤: 10%
  📈 推荐股票: 4只
  💰 投资组合分配:
    • 赛恩斯: 25.0% (¥24946, 329股)
    • 威胜信息: 20.0% (¥19952, 325股)
    • 万兴科技: 20.0% (¥19955, 165股)
    • 深信服: 15.0% (¥14961, 116股)
✅ 知识层完成: 投资知识库生成

🌟 智慧层: 正在生成投资智慧...
  🌟 系统理解: 股票投资是宏观经济、行业政策、公司基本面、市场情绪的多要素系统交互
  🎯 核心判断: 科技主线 + 政策受益 + 稳健增长
  📊 市场展望: 中性
  ⏰ 短期重点: 赛恩斯和威胜信息
✅ 智慧层完成: 投资智慧报告生成

📋 正在生成完整投资报告...
✅ 完整报告生成完成!

============================================================
📋 股票投资决策摘要报告
============================================================

📊 市场概况:
  • 市场趋势: 震荡整理
  • 涨跌比例: 5涨/3跌
  • 平均涨跌: +0.80%

🎯 投资策略 (稳健型):
  • 目标收益: 年化10-15%
  • 最大回撤: 10%
  • 持有期限: 12-24个月

💰 投资组合建议:
  • 赛恩斯: 25.0% (¥24946)
  • 威胜信息: 20.0% (¥19952)
  • 万兴科技: 20.0% (¥19955)
  • 深信服: 15.0% (¥14961)
  • 现金储备: ¥20000 (20.0%)

🌟 核心智慧:
  • 市场展望: 中性
  • 核心判断: 科技主线 + 政策受益 + 稳健增长
  • 短期重点: 赛恩斯、威胜信息

⏰ 择时建议:
  • 当前时段: 早盘观察期，避免追高
  • 建议操作: 观察为主，等待回调机会

🛡️ 风险控制:
  • 止损设置: 6%
  • 止盈目标: 15%

💡 立即行动建议:
  1. 根据当前价格调整买入计划
  2. 设置价格预警监控
  3. 准备投资资金，分批入场

⚠️  风险提示:
  • 投资有风险，入市需谨慎
  • 本报告仅供参考，不构成投资建议
  • 请根据自身风险承受能力做出决策
============================================================
```

## 📁 项目结构

```
stock-investment-assistant/
├── stock_investment_assistant.py     # 核心DIKW框架实现
├── stock_investment_assistant_main.py # 交互式主程序
├── test_dikw_assistant.py           # 简化版测试程序
├── requirements.txt                  # 依赖包列表
├── README.md                        # 英文说明文档
├── README_投资助手.md               # 中文详细文档
├── LICENSE                          # MIT许可证
└── .gitignore                       # Git忽略文件
```

## 🎯 三种投资策略

### 1. 激进型策略
- **适合**: 高风险承受能力，追求高收益
- **目标收益**: 年化20%+
- **最大回撤**: 15%
- **重点股票**: 深信服、科大讯飞、景嘉微
- **特点**: 集中投资，重仓高潜力股票

### 2. 稳健型策略
- **适合**: 中等风险承受能力，稳健增长
- **目标收益**: 年化10-15%
- **最大回撤**: 10%
- **重点股票**: 赛恩斯、威胜信息、万兴科技
- **特点**: 均衡配置，行业分散

### 3. 保守型策略
- **适合**: 低风险承受能力，保值增值
- **目标收益**: 年化5-10%
- **最大回撤**: 5%
- **重点股票**: 科创信息、超图软件
- **特点**: 分散投资，侧重低风险

## ⚙️ 风险控制机制

### 仓位管理
- 单只股票仓位 ≤ 20%
- 单个板块仓位 ≤ 40%
- 现金储备: 10-15%

### 止损止盈
- 激进型: 止损8%，止盈20%
- 稳健型: 止损6%，止盈15%
- 保守型: 止损4%，止盈10%

### 再平衡规则
- 频率: 季度再平衡
- 阈值: 权重偏离5%触发调整
- 方法: 再平衡至目标权重

## 🔧 高级功能

### 自定义配置
```python
from stock_investment_assistant import DIKWStockAssistant

# 自定义配置
assistant = DIKWStockAssistant(
    user_risk_profile="稳健型",
    investment_amount=200000,
    # 可扩展: 自定义股票列表、策略参数等
)

# 生成完整报告
report = assistant.generate_complete_report()

# 保存到文件
assistant.save_report_to_file(report, "my_investment_report.json")
```

### 批量分析
```python
# 分析多个风险偏好
profiles = ["激进型", "稳健型", "保守型"]
for profile in profiles:
    assistant = DIKWStockAssistant(user_risk_profile=profile, investment_amount=100000)
    report = assistant.generate_complete_report()
    assistant.save_report_to_file(report, f"report_{profile}.json")
```

### 定时任务
```bash
# 每天开盘后30分钟自动运行
0 10 * * 1-5 cd /path/to/project && python stock_investment_assistant_main.py --auto >> investment_log.txt
```

## 📈 与现有系统集成

### 数据共享
- 使用相同的股票配置
- 共享实时价格数据源（新浪财经API）
- 统一的风险等级分类

### 功能互补
- **监控系统**: 实时价格监控、预警触发
- **决策助手**: 投资分析、策略制定、决策支持
- **结合使用**: 监控系统提供数据，决策助手提供智慧

## 🛠️ 开发指南

### 环境设置
```bash
# 克隆仓库
git clone https://github.com/gorun78/stock-investment-assistant.git
cd stock-investment-assistant

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 代码结构
```python
# 主要类: DIKWStockAssistant
class DIKWStockAssistant:
    # 数据层方法
    def fetch_stock_data(self) -> Dict
    
    # 信息层方法  
    def analyze_market_info(self) -> Dict
    
    # 知识层方法
    def generate_investment_knowledge(self) -> Dict
    
    # 智慧层方法
    def generate_investment_wisdom(self) -> Dict
    
    # 完整流程
    def generate_complete_report(self) -> Dict
```

### 扩展开发
1. **添加新数据源**: 修改`fetch_stock_data()`方法
2. **自定义策略**: 修改`INVESTMENT_STRATEGIES`配置
3. **添加新指标**: 在信息层分析方法中扩展
4. **优化算法**: 改进投资组合构建逻辑

## 🤝 贡献指南

欢迎提交Issue和Pull Request改进本系统：

1. **报告问题**: 在GitHub Issues中描述问题
2. **功能建议**: 提出改进建议和使用场景
3. **代码贡献**: 遵循现有代码风格，添加测试
4. **文档改进**: 完善使用说明和示例

### 开发流程
```bash
# 1. Fork仓库
# 2. 克隆你的fork
git clone https://github.com/your-username/stock-investment-assistant.git

# 3. 创建功能分支
git checkout -b feature/new-feature

# 4. 提交更改
git add .
git commit -m "feat: 添加新功能"

# 5. 推送到fork
git push origin feature/new-feature

# 6. 创建Pull Request
```

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：

- **GitHub Issues**: [提交问题报告](https://github.com/gorun78/stock-investment-assistant/issues)
- **邮箱**: 通过GitHub个人资料联系
- **文档**: 查看详细使用说明

## 🙏 致谢

感谢所有贡献者和用户的支持！特别感谢：

- **DIKW框架** 的理论基础
- **新浪财经** 提供的免费数据API
- **开源社区** 的各种工具和库

---

**最后更新**: 2026-04-10  
**版本**: v1.0  
**作者**: gorun78  
**项目地址**: https://github.com/gorun78/stock-investment-assistant

⭐ 如果这个项目对你有帮助，请给个Star支持一下！