# 🎯 专业股票投资辅助工具

基于DIKW框架的专业级股票投资分析工具，集成多数据源、智能分析和实时监控。

## ✨ 核心特性

### 🏗️ DIKW分析框架
- **数据层**: 多数据源实时获取
- **信息层**: 市场情绪、板块轮动分析
- **知识层**: 投资策略、组合构建、风险控制
- **智慧层**: 系统理解、价值判断、未来决策

### 📊 多数据源支持
- 新浪财经API (免费，实时性好)
- 东方财富API (可选)
- Tushare专业数据 (可选，需要token)

### 🧠 智能分析
- 技术分析 (涨跌幅、波动率)
- 基本面分析 (PE/PB/市值)
- 市场情绪分析
- AI分析集成 (开发中)

### 📈 实时监控
- 价格波动预警
- 技术指标监控
- 定时任务调度

### 💼 投资组合管理
- 自动组合构建
- 风险控制规则
- 业绩评估报告

## 🚀 快速开始

### 安装依赖
```bash
pip install requests aiohttp
```

### 基本使用
```bash
# 1. 分析股票
python stock_pro_tool.py analyze --symbols 300730.SZ,688480.SS --profile 稳健型 --amount 100000

# 2. 配置管理
python stock_pro_tool.py config --list
python stock_pro_tool.py config --set data_sources.tushare.enabled true

# 3. 监控股票
python stock_pro_tool.py monitor --symbols 300730.SZ,300474.SZ --interval 5 --alert 2.0
```

### 完整示例
```bash
# 分析8只A股，稳健型策略，投资10万元
python stock_pro_tool.py analyze \
  --symbols 300730.SZ,688480.SS,300474.SZ,300454.SZ,002230.SZ,300624.SZ,688100.SS,300036.SZ \
  --profile 稳健型 \
  --amount 100000 \
  --output report.json \
  --format json
```

## 📋 命令行参考

### analyze - 分析股票
```bash
python stock_pro_tool.py analyze --symbols <股票代码> --profile <风险偏好> --amount <投资金额>

参数:
  --symbols    股票代码，逗号分隔 (如: 300730.SZ,688480.SS)
  --profile    风险偏好 [激进型|稳健型|保守型] (默认: 稳健型)
  --amount     投资金额(元) (默认: 100000)
  --output     输出文件路径
  --format     输出格式 [json|console|html] (默认: json)
```

### monitor - 监控股票
```bash
python stock_pro_tool.py monitor --symbols <股票代码> --interval <分钟> --alert <百分比>

参数:
  --symbols    股票代码，逗号分隔
  --config     配置文件路径
  --interval   监控间隔(分钟) (默认: 5)
  --alert      预警阈值(百分比) (默认: 2.0)
```

### config - 配置管理
```bash
python stock_pro_tool.py config [--get <键>] [--set <键> <值>] [--list]

参数:
  --get        获取配置值
  --set        设置配置值 (键 值)
  --list       列出所有配置
```

### report - 生成报告
```bash
python stock_pro_tool.py report <输入文件> --format <格式> --output <输出文件>

参数:
  input        输入文件或分析ID
  --format     报告格式 [html|pdf|markdown] (默认: html)
  --output     输出文件路径 (必需)
```

## ⚙️ 配置说明

### 配置文件位置
- 默认: `~/.stock_pro_tool/config.json`
- 首次运行自动创建

### 主要配置项
```json
{
  "data_sources": {
    "sina": {"enabled": true, "priority": 1},
    "eastmoney": {"enabled": false, "priority": 2},
    "tushare": {"enabled": false, "priority": 3, "token": ""}
  },
  "analysis": {
    "technical": true,
    "fundamental": true,
    "sentiment": true,
    "ai_analysis": false
  },
  "monitoring": {
    "enabled": true,
    "interval_minutes": 5,
    "alert_threshold_percent": 2.0,
    "working_hours": ["09:30", "15:00"]
  }
}
```

### 配置示例
```bash
# 启用Tushare数据源
python stock_pro_tool.py config --set data_sources.tushare.enabled true
python stock_pro_tool.py config --set data_sources.tushare.token your_tushare_token

# 调整监控设置
python stock_pro_tool.py config --set monitoring.interval_minutes 10
python stock_pro_tool.py config --set monitoring.alert_threshold_percent 1.5

# 启用AI分析
python stock_pro_tool.py config --set analysis.ai_analysis true
```

## 📊 分析报告

### 报告内容
1. **市场概况**
   - 市场趋势判断
   - 涨跌比例统计
   - 最强板块识别
   - 平均涨跌幅

2. **投资策略**
   - 风险承受能力
   - 目标收益
   - 最大回撤
   - 持有期限

3. **投资组合**
   - 股票权重分配
   - 投资金额计算
   - 现金储备建议

4. **核心智慧**
   - 市场展望
   - 核心判断
   - 优先级排序

5. **择时建议**
   - 当前时段分析
   - 最佳买卖时间
   - 避免时段提醒

6. **风险控制**
   - 止损止盈设置
   - 仓位限制
   - 再平衡规则

### 报告格式
- **JSON格式**: 完整数据，适合程序处理
- **控制台输出**: 摘要信息，适合快速查看
- **HTML报告**: 可视化图表 (开发中)
- **PDF报告**: 正式文档 (开发中)

## 🎯 投资策略

### 激进型策略
- **适合**: 高风险承受能力，追求高收益
- **目标收益**: 年化20%+
- **最大回撤**: 15%
- **重点股票**: 高成长性、高波动性
- **特点**: 集中投资，重仓高潜力股票

### 稳健型策略
- **适合**: 中等风险承受能力，稳健增长
- **目标收益**: 年化10-15%
- **最大回撤**: 10%
- **重点股票**: 行业龙头、稳定增长
- **特点**: 均衡配置，行业分散

### 保守型策略
- **适合**: 低风险承受能力，保值增值
- **目标收益**: 年化5-10%
- **最大回撤**: 5%
- **重点股票**: 低估值、高分红
- **特点**: 分散投资，侧重低风险

## 🛡️ 风险控制

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

## ⏰ 择时策略

### 交易时段建议
- **09:30-10:30**: 早盘观察期，避免追高
- **10:30-11:30**: 上午交易活跃期，可分批建仓
- **13:00-14:00**: 下午开盘期，寻找回调机会
- **14:00-15:00**: 尾盘交易期，控制仓位

### 最佳时机
- **最佳买入**: 09:45-10:15, 13:30-14:00
- **最佳卖出**: 10:30-11:00, 14:30-15:00
- **避免时段**: 09:30-09:35, 14:55-15:00 (极端波动)

## 🔄 定期操作流程

### 每日操作
1. 运行分析获取最新建议
2. 检查价格预警触发情况
3. 根据择时建议调整操作

### 每周检查
1. 复盘投资组合表现
2. 检查止损止盈触发
3. 关注市场情绪变化

### 每月复盘
1. 评估策略有效性
2. 调整投资组合权重
3. 学习新的投资知识

### 季度调整
1. 全面再平衡投资组合
2. 淘汰表现不佳的股票
3. 纳入新的投资机会

## 📈 与现有系统集成

### 数据共享
- 使用相同的股票配置
- 共享实时价格数据源
- 统一的风险等级分类

### 功能互补
- **监控系统**: 实时价格监控、预警触发
- **决策助手**: 投资分析、策略制定、决策支持
- **专业工具**: 多数据源、智能分析、组合管理

### 自动化集成
```bash
# 定时运行示例 (每天开盘后30分钟)
0 10 * * 1-5 cd /path/to/workspace && python stock_pro_tool.py analyze --symbols 300730.SZ,688480.SS --profile 稳健型 --amount 100000 --output daily_report.json
```

## 🛠️ 高级功能

### 自定义股票列表
```python
# 通过配置文件自定义
{
  "stocks": {
    "default_watchlist": [
      "600519.SH",  # 贵州茅台
      "000858.SZ",  # 五粮液
      "002415.SZ"   # 海康威视
    ]
  }
}
```

### 批量分析
```bash
# 分析多个风险偏好
for profile in "激进型 稳健型 保守型"; do
  python stock_pro_tool.py analyze --symbols 300730.SZ,688480.SS --profile $profile --amount 100000 --output report_${profile}.json
done
```

### API接口 (开发中)
```python
from stock_pro_tool import DIKWEngine, ConfigManager

config = ConfigManager()
engine = DIKWEngine(config)

# 异步分析
import asyncio
report = asyncio.run(engine.analyze(["300730.SZ", "688480.SS"], "稳健型", 100000))
```

## ⚠️ 注意事项

### 数据源可靠性
- 新浪财经API为免费数据源，可能存在延迟
- 重要决策建议使用付费数据源验证
- 非交易时间可能无法获取实时数据

### 投资风险提示
1. **本工具仅供参考**，不构成投资建议
2. **投资有风险**，入市需谨慎
3. **过去表现不代表未来**，市场可能变化
4. **请根据自身风险承受能力**做出决策
5. **建议咨询专业投资顾问**进行重大投资

### 技术限制
- 依赖网络连接获取实时数据
- 免费API可能有调用频率限制
- AI分析功能需要额外配置

## 🔧 故障排除

### 常见问题
1. **数据获取失败**: 检查网络连接，稍后重试
2. **API限制**: 降低请求频率，使用缓存数据
3. **程序错误**: 查看错误日志，确保依赖包已安装

### 调试模式
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
python stock_pro_tool.py analyze --symbols 300730.SZ --profile 稳健型 --amount 100000

# 使用离线模式 (开发中)
python stock_pro_tool.py analyze --offline --symbols 300730.SZ --profile 稳健型 --amount 100000
```

## 📚 学习资源

### DIKW框架
- 《信息架构：超越Web设计》
- 《知识的边界》
- DIKW模型在投资决策中的应用研究

### 投资知识
- 《聪明的投资者》（本杰明·格雷厄姆）
- 《投资最重要的事》（霍华德·马克斯）
- 《漫步华尔街》（伯顿·马尔基尔）

### 技术分析
- 《日本蜡烛图技术》
- 《技术分析》（马丁·普林格）
- 《股票大作手回忆录》

## 🚀 开发计划

### 短期计划 (1-2周)
1. 完善HTML报告生成
2. 添加更多技术指标
3. 实现历史回测功能

### 中期计划 (1-2月)
1. 集成机器学习模型
2. 添加多因子选股模型
3. 实现投资组合优化算法

### 长期计划 (3-6月)
1. 开发Web界面
2. 实现自动化交易接口
3. 构建完整的量化投资平台

## 👥 贡献指南

欢迎提交Issue和Pull Request改进本工具：

1. **报告问题**: 描述具体问题和重现步骤
2. **功能建议**: 提出改进建议和使用场景
3. **代码贡献**: 遵循现有代码风格，添加测试
4. **文档改进**: 完善使用说明和示例

## 📄 许可证

本项目采用MIT许可证。

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：
- GitHub Issues: 提交问题报告
- 文档: 查看详细使用说明

---

**版本**: v2.0  
**最后更新**: 2026-04-14  
**作者**: DT老炮  
**致谢**: 感谢所有贡献者和用户的支持！