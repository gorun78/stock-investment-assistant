# 🎯 股票投资决策辅助系统

基于DIKW（数据-信息-知识-智慧）框架的智能股票投资决策辅助系统，提供完整的投资建议和智能选股功能。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 主要功能

### 📊 股票维护
- 股票列表管理（添加/编辑/删除）
- 股票详情查看
- 风险等级标识

### 🧠 智能选股
- **5种选股策略**：成长股策略、价值股策略、高股息策略、趋势动量策略、均衡配置策略
- 板块筛选功能
- 潜力评分与投资评级
- 一键添加到自选

### 📈 投资分析
- 实时股票数据获取
- 投资组合分析
- 风险评估与时机建议
- 技术指标分析

### 📋 报告生成
- 完整投资报告
- 策略分析报告
- 风险评估报告

### 🚀 专业股票投资辅助工具 (新增)
- **多数据源支持**: 新浪财经 + 东方财富 + Tushare
- **异步数据获取**: 高性能并发处理
- **完整命令行界面**: analyze/monitor/config/report命令
- **动态配置管理**: 灵活的配置文件系统
- **智能缓存机制**: 减少重复网络请求

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

### 环境要求
- Python 3.8+
- Flask 2.x (Web界面)
- aiohttp (专业工具)
- 其他依赖见 requirements.txt

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序

**方式1: 启动Web服务**
```bash
python src/web/web_app.py
```
然后访问 http://127.0.0.1:5000

**方式2: 运行主程序（交互式）**
```bash
python stock_investment_assistant_main.py
```

**方式3: 使用专业股票投资辅助工具**
```bash
# 基本分析
python stock_pro_tool.py analyze --symbols 300730.SZ,688480.SS --profile 稳健型 --amount 100000

# 配置管理
python stock_pro_tool.py config --list
python stock_pro_tool.py config --set monitoring.interval_minutes 10

# 查看帮助
python stock_pro_tool.py --help
python stock_pro_tool.py analyze --help
```

**方式4: 直接使用类**
```python
from src.core.stock_investment_assistant_v2 import EnhancedDIKWStockAssistant

assistant = EnhancedDIKWStockAssistant(user_risk_profile='稳健型', investment_amount=100000)
report = assistant.generate_complete_report()
assistant.display_summary_report()
```

## 📁 项目结构

```
stock-investment-assistant/
├── src/                    # 源代码目录
│   ├── core/               # 核心业务逻辑
│   │   ├── stock_investment_assistant.py      # 基础DIKW框架实现
│   │   └── stock_investment_assistant_v2.py   # 增强版DIKW框架
│   ├── analysis/           # 分析模块
│   │   ├── advanced_analyzer.py      # 高级分析器
│   │   ├── portfolio_optimizer.py    # 投资组合优化器
│   │   ├── report_analyzer.py        # 报告分析器
│   │   ├── risk_timing.py            # 风险与时序控制
│   │   └── technical_indicators.py   # 技术指标计算
│   └── web/                # Web应用
│       ├── templates/      # HTML模板
│       │   └── index.html  # 主页面
│       └── web_app.py      # Flask Web服务
├── stock_pro_tool.py       # 专业股票投资辅助工具 (命令行版本)
├── setup.py                # 专业工具安装脚本
├── test_pro_tool.py        # 专业工具测试脚本
├── demo_pro_tool.py        # 专业工具演示脚本
├── config_template.json    # 配置文件模板
├── PROFESSIONAL_STOCK_TOOL_PLAN.md  # 专业工具项目计划
├── README_PRO_TOOL.md      # 专业工具详细文档
├── UPDATE_SUMMARY.md       # 专业工具更新总结
├── tests/                  # 测试文件
│   ├── test_dikw_assistant.py
│   ├── test_enhanced_features.py
│   └── test_optimization.py
├── reports/                # 报告输出目录
├── docs/                   # 文档目录
│   └── skills/             # 技能文档
├── .gitignore
├── IMPROVEMENT_PLAN.md
├── LICENSE
├── README.md
├── README_投资助手.md
└── requirements.txt
```

## 🎯 五种选股策略

### 1. ⚖️ 均衡配置策略
- **适合**: 稳健型投资者
- **特点**: 兼顾成长与价值的均衡组合

### 2. 🚀 成长股策略
- **适合**: 激进型投资者
- **特点**: 高ROE、高增长潜力的成长型股票

### 3. 📊 价值股策略
- **适合**: 价值投资者
- **特点**: 低PE、估值合理的价值型股票

### 4. 💰 高股息策略
- **适合**: 收益型投资者
- **特点**: 稳定分红、现金流充沛的股票

### 5. 📈 趋势动量策略
- **适合**: 技术型投资者
- **特点**: 近期表现强势的股票

## 🎯 三种投资风险偏好

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

## 🌐 Web API接口

### 股票维护
- `GET /api/stocks` - 获取股票列表
- `POST /api/stocks` - 添加股票
- `PUT /api/stocks/<name>` - 更新股票
- `DELETE /api/stocks/<name>` - 删除股票

### 智能选股
- `GET /api/stock_pool` - 获取股票池
- `GET /api/selection_strategies` - 获取选股策略
- `GET /api/sectors` - 获取板块列表
- `POST /api/select_stocks` - 执行智能选股

### 投资分析
- `GET /api/analyze` - 获取投资分析
- `GET /api/stocks/<name>/indicators` - 获取股票技术指标
- `POST /api/generate_report` - 生成投资报告

## 🚀 专业股票投资辅助工具

### 核心特性
1. **🏗️ 模块化架构**: 配置管理、数据获取、DIKW分析引擎、命令行界面
2. **📊 多数据源**: 新浪财经 + 东方财富 + Tushare，支持优先级配置
3. **⚡ 异步高性能**: 异步数据获取，智能缓存机制
4. **🎯 完整CLI**: analyze/monitor/config/report命令，丰富的参数选项
5. **⚙️ 动态配置**: 配置文件管理，支持运行时配置更新
6. **🧠 智能分析**: 完整的DIKW框架实现，从数据到智慧的完整流程

### 快速使用
```bash
# 1. 安装专业工具
python setup.py

# 2. 基本分析
python stock_pro_tool.py analyze --symbols 300730.SZ,688480.SS --profile 稳健型 --amount 100000

# 3. 批量分析不同策略
for profile in "激进型 稳健型 保守型"; do
  python stock_pro_tool.py analyze --symbols 300730.SZ,688480.SS --profile $profile --amount 100000 --output report_${profile}.json
done

# 4. 配置监控
python stock_pro_tool.py config --set monitoring.interval_minutes 10
python stock_pro_tool.py config --set monitoring.alert_threshold_percent 1.5
```

### 与Web版本的对比
| 特性 | Web版本 | 专业工具 |
|------|---------|----------|
| 界面 | Web浏览器 | 命令行 |
| 数据源 | 新浪财经 | 多数据源 |
| 性能 | 同步请求 | 异步并发 |
| 配置 | 硬编码 | 动态配置 |
| 部署 | 需要Web服务器 | 单机运行 |
| 自动化 | 有限 | 完整支持 |

### 详细文档
- 完整使用说明: [README_PRO_TOOL.md](README_PRO_TOOL.md)
- 项目计划: [PROFESSIONAL_STOCK_TOOL_PLAN.md](PROFESSIONAL_STOCK_TOOL_PLAN.md)
- 更新总结: [UPDATE_SUMMARY.md](UPDATE_SUMMARY.md)

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

### 扩展开发
1. **添加新数据源**: 修改`fetch_stock_data()`方法
2. **自定义策略**: 修改策略配置
3. **添加新指标**: 在信息层分析方法中扩展
4. **优化算法**: 改进投资组合构建逻辑
5. **集成专业工具**: 将专业工具功能集成到Web版本

## 🤝 贡献指南

欢迎提交Issue和Pull Request改进本系统：

1. **报告问题**: 在GitHub Issues中描述问题
2. **功能建议**: 提出改进建议和使用场景
3. **代码贡献**: 遵循现有代码风格，添加测试
4. **文档改进**: 完善使用说明和示例

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：

- **GitHub Issues**: [提交问题报告](https://github.com/gorun78/stock-investment-assistant/issues)
- **邮箱**: 通过GitHub个人资料联系

## 🙏 致谢

感谢所有贡献者和用户的支持！特别感谢：

- **DIKW框架** 的理论基础
- **新浪财经** 提供的免费数据API
- **开源社区** 的各种工具和库

---

**最后更新**: 2026-04-11  
**版本**: v2.0  
**作者**: gorun78  
**项目地址**: https://github.com/gorun78/stock-investment-assistant

⭐ 如果这个项目对你有帮助，请给个Star支持一下！
