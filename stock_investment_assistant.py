#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资决策辅助系统 - 基于DIKW框架
版本: 1.0
作者: DT老炮
日期: 2026-04-10

功能:
1. 数据层: 实时获取8只股票数据
2. 信息层: 分析市场情绪、板块轮动
3. 知识层: 生成投资策略和风险控制方案
4. 智慧层: 提供个性化投资建议和决策支持
"""

import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys
import os

# ==================== 配置部分 ====================

STOCK_CONFIG = {
    "科创信息": {"symbol": "300730.SZ", "sector": "信息技术", "risk_level": "中等"},
    "赛恩斯": {"symbol": "688480.SS", "sector": "环保工程", "risk_level": "低"},
    "景嘉微": {"symbol": "300474.SZ", "sector": "半导体", "risk_level": "高"},
    "深信服": {"symbol": "300454.SZ", "sector": "网络安全", "risk_level": "高"},
    "科大讯飞": {"symbol": "002230.SZ", "sector": "人工智能", "risk_level": "中等"},
    "万兴科技": {"symbol": "300624.SZ", "sector": "软件服务", "risk_level": "中等"},
    "威胜信息": {"symbol": "688100.SS", "sector": "智能电网", "risk_level": "低"},
    "超图软件": {"symbol": "300036.SZ", "sector": "地理信息", "risk_level": "低"}
}

INVESTMENT_STRATEGIES = {
    "激进型": {
        "risk_tolerance": "高",
        "target_return": "年化20%+",
        "max_drawdown": "15%",
        "holding_period": "6-12个月"
    },
    "稳健型": {
        "risk_tolerance": "中等",
        "target_return": "年化10-15%",
        "max_drawdown": "10%",
        "holding_period": "12-24个月"
    },
    "保守型": {
        "risk_tolerance": "低",
        "target_return": "年化5-10%",
        "max_drawdown": "5%",
        "holding_period": "24个月+"
    }
}

# ==================== DIKW框架核心类 ====================

class DIKWStockAssistant:
    """基于DIKW框架的股票投资决策辅助系统"""
    
    def __init__(self, user_risk_profile="稳健型", investment_amount=100000):
        """
        初始化投资助手
        
        Args:
            user_risk_profile: 用户风险偏好（激进型/稳健型/保守型）
            investment_amount: 投资金额（元）
        """
        self.user_risk_profile = user_risk_profile
        self.investment_amount = investment_amount
        self.stock_data = {}
        self.market_analysis = {}
        self.strategy_recommendations = {}
        
        print(f"🎯 股票投资决策辅助系统启动")
        print(f"📊 用户配置: {user_risk_profile} | 投资金额: ¥{investment_amount:,}")
        print("=" * 60)
    
    # ==================== 数据层: 原始数据收集 ====================
    
    def fetch_stock_data(self) -> Dict:
        """
        数据层: 获取实时股票数据
        返回: 原始股票数据字典
        """
        print("📈 数据层: 正在获取实时股票数据...")
        
        stock_data = {}
        for name, config in STOCK_CONFIG.items():
            try:
                symbol = config["symbol"]
                # 使用新浪财经API获取实时数据
                if symbol.endswith(".SZ"):
                    market = "sz"
                    code = symbol.replace(".SZ", "")
                else:  # .SS
                    market = "sh"
                    code = symbol.replace(".SS", "")
                
                url = f"http://hq.sinajs.cn/list={market}{code}"
                print(f"  GET {url}")
                # 添加请求头模拟浏览器访问，避免403 Forbidden
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Referer": "https://finance.sina.com.cn/"
                }
                response = requests.get(url, headers=headers, timeout=100000)        
                print(f"  {response.status_code} {response.reason}")
                
                if response.status_code == 200:
                    content = response.text
                    # 解析新浪财经数据格式
                    data_str = content.split('"')[1]
                    if data_str:
                        data_parts = data_str.split(',')
                        if len(data_parts) > 3:
                            current_price = float(data_parts[3])  # 当前价格
                            open_price = float(data_parts[1])     # 开盘价
                            high_price = float(data_parts[4])     # 最高价
                            low_price = float(data_parts[5])      # 最低价
                            volume = float(data_parts[8])         # 成交量
                            
                            stock_data[name] = {
                                "symbol": symbol,
                                "current_price": current_price,
                                "open_price": open_price,
                                "high_price": high_price,
                                "low_price": low_price,
                                "volume": volume,
                                "change": current_price - open_price,
                                "change_percent": ((current_price - open_price) / open_price * 100) if open_price > 0 else 0,
                                "sector": config["sector"],
                                "risk_level": config["risk_level"],
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            print(f"  ✓ {name}({symbol}): ¥{current_price:.2f} ({stock_data[name]['change_percent']:+.2f}%)")
                time.sleep(0.5)  # 避免请求过快
                
            except Exception as e:
                print(f"  ✗ {name}: 数据获取失败 - {str(e)}")
                # 使用模拟数据作为后备
                stock_data[name] = self._generate_mock_data(name, config)
        
        self.stock_data = stock_data
        print(f"✅ 数据层完成: 获取到 {len(stock_data)} 只股票数据")
        return stock_data
    
    def _generate_mock_data(self, name: str, config: Dict) -> Dict:
        """生成模拟数据（当API不可用时）"""
        import random
        base_price = random.uniform(10, 150)
        change_percent = random.uniform(-5, 5)
        
        return {
            "symbol": config["symbol"],
            "current_price": base_price * (1 + change_percent/100),
            "open_price": base_price,
            "high_price": base_price * (1 + abs(change_percent)/100 + 0.02),
            "low_price": base_price * (1 - abs(change_percent)/100 - 0.02),
            "volume": random.randint(10000, 1000000),
            "change": base_price * change_percent/100,
            "change_percent": change_percent,
            "sector": config["sector"],
            "risk_level": config["risk_level"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True
        }
    
    # ==================== 信息层: 数据转化为信息 ====================
    
    def analyze_market_info(self) -> Dict:
        """
        信息层: 分析市场信息
        返回: 市场分析报告
        """
        print("\n📊 信息层: 正在分析市场信息...")
        
        if not self.stock_data:
            self.fetch_stock_data()
        
        # 1. 市场情绪分析
        rising_stocks = [s for s in self.stock_data.values() if s["change_percent"] > 0]
        falling_stocks = [s for s in self.stock_data.values() if s["change_percent"] < 0]
        
        market_sentiment = {
            "rising_count": len(rising_stocks),
            "falling_count": len(falling_stocks),
            "rising_percent": len(rising_stocks) / len(self.stock_data) * 100,
            "average_change": sum(s["change_percent"] for s in self.stock_data.values()) / len(self.stock_data),
            "strongest_sector": self._analyze_sector_performance(),
            "market_trend": self._determine_market_trend()
        }
        
        # 2. 板块轮动分析
        sector_analysis = {}
        for stock in self.stock_data.values():
            sector = stock["sector"]
            if sector not in sector_analysis:
                sector_analysis[sector] = {"stocks": [], "total_change": 0, "count": 0}
            sector_analysis[sector]["stocks"].append(stock)
            sector_analysis[sector]["total_change"] += stock["change_percent"]
            sector_analysis[sector]["count"] += 1
        
        for sector in sector_analysis:
            sector_analysis[sector]["avg_change"] = sector_analysis[sector]["total_change"] / sector_analysis[sector]["count"]
        
        # 3. 风险收益特征
        risk_return_analysis = {}
        for name, data in self.stock_data.items():
            volatility = abs(data["high_price"] - data["low_price"]) / data["open_price"] * 100
            risk_return_analysis[name] = {
                "volatility": volatility,
                "risk_level": data["risk_level"],
                "return_potential": self._estimate_return_potential(data)
            }
        
        self.market_analysis = {
            "market_sentiment": market_sentiment,
            "sector_analysis": sector_analysis,
            "risk_return_analysis": risk_return_analysis,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 信息层完成: 市场分析报告生成")
        self._display_market_info()
        return self.market_analysis
    
    def _analyze_sector_performance(self) -> str:
        """分析表现最强的板块"""
        sector_performance = {}
        for stock in self.stock_data.values():
            sector = stock["sector"]
            if sector not in sector_performance:
                sector_performance[sector] = []
            sector_performance[sector].append(stock["change_percent"])
        
        best_sector = None
        best_avg = -100
        for sector, changes in sector_performance.items():
            avg_change = sum(changes) / len(changes)
            if avg_change > best_avg:
                best_avg = avg_change
                best_sector = sector
        
        return best_sector if best_sector else "未知"
    
    def _determine_market_trend(self) -> str:
        """判断市场趋势"""
        avg_change = sum(s["change_percent"] for s in self.stock_data.values()) / len(self.stock_data)
        
        if avg_change > 2:
            return "强势上涨"
        elif avg_change > 0.5:
            return "温和上涨"
        elif avg_change > -0.5:
            return "震荡整理"
        elif avg_change > -2:
            return "温和下跌"
        else:
            return "明显下跌"
    
    def _estimate_return_potential(self, stock_data: Dict) -> str:
        """估算股票回报潜力"""
        change = stock_data["change_percent"]
        volatility = abs(stock_data["high_price"] - stock_data["low_price"]) / stock_data["open_price"] * 100
        
        if change > 3 and volatility < 5:
            return "高"
        elif change > 1 and volatility < 8:
            return "中高"
        elif change > -1:
            return "中等"
        else:
            return "低"
    
    def _display_market_info(self):
        """显示市场信息摘要"""
        sentiment = self.market_analysis["market_sentiment"]
        print(f"  📈 市场情绪: {sentiment['market_trend']}")
        print(f"  📊 涨跌比例: {sentiment['rising_count']}涨/{sentiment['falling_count']}跌 ({sentiment['rising_percent']:.1f}%上涨)")
        print(f"  🎯 最强板块: {sentiment['strongest_sector']}")
        print(f"  📉 平均涨跌: {sentiment['average_change']:+.2f}%")
    
    # ==================== 知识层: 信息转化为知识 ====================
    
    def generate_investment_knowledge(self) -> Dict:
        """
        知识层: 生成投资知识（策略、规则、模式）
        返回: 投资知识库
        """
        print("\n🧠 知识层: 正在生成投资知识...")
        
        if not self.market_analysis:
            self.analyze_market_info()
        
        # 1. 根据用户风险偏好选择策略
        strategy_config = INVESTMENT_STRATEGIES[self.user_risk_profile]
        
        # 2. 股票筛选和分类
        recommended_stocks = self._filter_stocks_by_risk()
        
        # 3. 投资组合构建
        portfolio = self._build_portfolio(recommended_stocks)
        
        # 4. 风险控制规则
        risk_rules = self._generate_risk_rules()
        
        # 5. 择时策略
        timing_strategy = self._generate_timing_strategy()
        
        self.investment_knowledge = {
            "user_profile": self.user_risk_profile,
            "strategy_config": strategy_config,
            "recommended_stocks": recommended_stocks,
            "portfolio_allocation": portfolio,
            "risk_control_rules": risk_rules,
            "timing_strategy": timing_strategy,
            "knowledge_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 知识层完成: 投资知识库生成")
        self._display_investment_knowledge()
        return self.investment_knowledge
    
    def _filter_stocks_by_risk(self) -> Dict:
        """根据风险偏好筛选股票"""
        risk_mapping = {
            "激进型": ["高", "中等", "低"],
            "稳健型": ["中等", "低"],
            "保守型": ["低"]
        }
        
        allowed_risks = risk_mapping[self.user_risk_profile]
        filtered = {}
        
        for name, data in self.stock_data.items():
            if data["risk_level"] in allowed_risks:
                # 进一步根据市场表现筛选
                change = data["change_percent"]
                if self.user_risk_profile == "激进型" or abs(change) < 5:  # 避免追涨杀跌
                    filtered[name] = data
        
        return filtered
    
    def _build_portfolio(self, stocks: Dict) -> Dict:
        """构建投资组合"""
        total_investment = self.investment_amount
        
        # 根据风险偏好分配权重
        if self.user_risk_profile == "激进型":
            # 集中投资，重仓高潜力股票
            weights = self._calculate_aggressive_weights(stocks)
        elif self.user_risk_profile == "稳健型":
            # 均衡配置
            weights = self._calculate_moderate_weights(stocks)
        else:  # 保守型
            # 分散投资，侧重低风险
            weights = self._calculate_conservative_weights(stocks)
        
        portfolio = {}
        for name, weight in weights.items():
            if name in stocks:
                amount = total_investment * weight / 100
                shares = int(amount / stocks[name]["current_price"])
                actual_amount = shares * stocks[name]["current_price"]
                
                portfolio[name] = {
                    "weight_percent": weight,
                    "investment_amount": actual_amount,
                    "shares": shares,
                    "price": stocks[name]["current_price"],
                    "sector": stocks[name]["sector"]
                }
        
        return portfolio
    
    def _calculate_aggressive_weights(self, stocks: Dict) -> Dict:
        """计算激进型权重"""
        weights = {}
        stock_count = len(stocks)
        
        if stock_count >= 3:
            # 前3只重仓，其余轻仓
            sorted_stocks = sorted(stocks.items(), key=lambda x: x[1]["change_percent"], reverse=True)
            for i, (name, _) in enumerate(sorted_stocks[:3]):
                weights[name] = 25 if i == 0 else 20
            for name, _ in sorted_stocks[3:]:
                weights[name] = 35 / max(1, len(sorted_stocks[3:]))
        else:
            # 平均分配
            for name in stocks:
                weights[name] = 100 / stock_count
        
        return weights
    
    def _calculate_moderate_weights(self, stocks: Dict) -> Dict:
        """计算稳健型权重"""
        weights = {}
        stock_count = len(stocks)
        
        # 按板块分配
        sectors = {}
        for name, data in stocks.items():
            sector = data["sector"]
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(name)
        
        sector_weight = 100 / len(sectors) if sectors else 0
        
        for sector, stock_list in sectors.items():
            stock_weight = sector_weight / len(stock_list)
            for name in stock_list:
                weights[name] = stock_weight
        
        return weights
    
    def _calculate_conservative_weights(self, stocks: Dict) -> Dict:
        """计算保守型权重"""
        weights = {}
        stock_count = len(stocks)
        
        # 更分散的分配
        base_weight = 100 / stock_count
        for name, data in stocks.items():
            # 低风险股票权重稍高
            if data["risk_level"] == "低":
                weights[name] = base_weight * 1.2
            else:
                weights[name] = base_weight * 0.8
        
        # 归一化
        total = sum(weights.values())
        for name in weights:
            weights[name] = weights[name] * 100 / total
        
        return weights
    
    def _generate_risk_rules(self) -> Dict:
        """生成风险控制规则"""
        rules = {
            "position_limits": {
                "max_single_stock": 20,  # 单只股票最大仓位%
                "max_single_sector": 40,  # 单个板块最大仓位%
                "cash_reserve": 15 if self.user_risk_profile == "保守型" else 10  # 现金储备%
            },
            "stop_loss_rules": {
                "激进型": {"stop_loss": 8, "take_profit": 20},
                "稳健型": {"stop_loss": 6, "take_profit": 15},
                "保守型": {"stop_loss": 4, "take_profit": 10}
            },
            "rebalancing_rules": {
                "frequency": "季度",
                "threshold": 5,  # 权重偏离阈值%
                "method": "再平衡至目标权重"
            }
        }
        return rules
    
    def _generate_timing_strategy(self) -> Dict:
        """生成择时策略"""
        current_hour = datetime.now().hour
        
        if 9 <= current_hour < 10:
            timing = "早盘观察期，避免追高"
            action = "观察为主，等待回调机会"
        elif 10 <= current_hour < 11:
            timing = "上午交易活跃期"
            action = "可考虑分批建仓"
        elif 13 <= current_hour < 14:
            timing = "下午开盘期"
            action = "寻找盘中回调机会"
        elif 14 <= current_hour < 15:
            timing = "尾盘交易期"
            action = "关注收盘前机会，控制仓位"
        else:
            timing = "非交易时间"
            action = "复盘分析，制定明日计划"
        
        return {
            "current_timing": timing,
            "recommended_action": action,
            "best_buy_times": ["09:45-10:15", "13:30-14:00"],
            "best_sell_times": ["10:30-11:00", "14:30-15:00"],
            "avoid_times": ["09:30-09:35", "14:55-15:00"]  # 避免开盘和收盘极端波动
        }
    
    def _display_investment_knowledge(self):
        """显示投资知识摘要"""
        knowledge = self.investment_knowledge
        print(f"  🎯 适用策略: {knowledge['user_profile']}")
        print(f"  📊 目标收益: {knowledge['strategy_config']['target_return']}")
        print(f"  🛡️  最大回撤: {knowledge['strategy_config']['max_drawdown']}")
        print(f"  📈 推荐股票: {len(knowledge['recommended_stocks'])}只")
        
        # 显示投资组合
        print("  💰 投资组合分配:")
        portfolio = knowledge['portfolio_allocation']
        for name, alloc in portfolio.items():
            print(f"    • {name}: {alloc['weight_percent']:.1f}% (¥{alloc['investment_amount']:.0f}, {alloc['shares']}股)")
    
    # ==================== 智慧层: 知识转化为智慧 ====================
    
    def generate_investment_wisdom(self) -> Dict:
        """
        智慧层: 生成投资智慧（系统理解、价值判断、未来决策）
        返回: 投资智慧报告
        """
        print("\n🌟 智慧层: 正在生成投资智慧...")
        
        if not self.investment_knowledge:
            self.generate_investment_knowledge()
        
        # 1. 系统理解
        system_understanding = self._understand_investment_system()
        
        # 2. 价值判断
        value_judgment = self._make_value_judgment()
        
        # 3. 未来决策
        future_decisions = self._make_future_decisions()
        
        # 4. 个性化建议
        personalized_advice = self._generate_personalized_advice()
        
        self.investment_wisdom = {
            "system_understanding": system_understanding,
            "value_judgment": value_judgment,
            "future_decisions": future_decisions,
            "personalized_advice": personalized_advice,
            "wisdom_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 智慧层完成: 投资智慧报告生成")
        self._display_investment_wisdom()
        return self.investment_wisdom
    
    def _understand_investment_system(self) -> Dict:
        """理解投资系统"""
        return {
            "core_insight": "股票投资是宏观经济、行业政策、公司基本面、市场情绪的多要素系统交互",
            "key_factors": [
                "宏观经济周期",
                "行业政策导向",
                "公司竞争优势",
                "市场情绪波动",
                "资金流向变化"
            ],
            "system_interactions": {
                "policy_impact": "环保政策→赛恩斯受益，网络安全政策→深信服受益",
                "tech_cycle": "半导体周期→景嘉微波动，AI发展→科大讯飞成长",
                "market_sentiment": "风险偏好变化影响科技股 vs 防御股表现"
            },
            "adaptability": "不同策略在不同市场环境下的适用性不同，需要动态调整"
        }
    
    def _make_value_judgment(self) -> Dict:
        """做出价值判断"""
        # 基于当前市场分析的价值判断
        sentiment = self.market_analysis["market_sentiment"]
        
        if sentiment["market_trend"] in ["强势上涨", "温和上涨"]:
            market_outlook = "乐观"
            risk_appetite = "可适度增加风险暴露"
        elif sentiment["market_trend"] == "震荡整理":
            market_outlook = "中性"
            risk_appetite = "保持现有风险水平"
        else:
            market_outlook = "谨慎"
            risk_appetite = "降低风险暴露，增加防御"
        
        return {
            "market_outlook": market_outlook,
            "risk_appetite": risk_appetite,
            "core_judgment": "科技主线 + 政策受益 + 稳健增长",
            "priority_ranking": [
                "深信服 (网络安全龙头，政策支持)",
                "科大讯飞 (AI国家队，技术壁垒)",
                "赛恩斯 (环保政策受益，现金流稳定)",
                "景嘉微 (国产替代，成长空间大)"
            ],
            "ethical_consideration": "避免追涨杀跌，坚持价值投资，控制情绪化交易"
        }
    
    def _make_future_decisions(self) -> Dict:
        """制定未来决策"""
        return {
            "short_term_1_3m": {
                "focus": "深信服、科大讯飞",
                "action": "分批建仓，控制成本",
                "target": "完成核心仓位配置",
                "risk_control": "严格执行止损，单股仓位≤20%"
            },
            "medium_term_3_12m": {
                "focus": "优化投资组合",
                "action": "季度再平衡，优胜劣汰",
                "target": "实现稳健收益",
                "risk_control": "动态调整止损止盈点"
            },
            "long_term_12m_plus": {
                "focus": "价值发现和成长投资",
                "action": "关注基本面变化，长期持有",
                "target": "穿越周期，实现复利增长",
                "risk_control": "系统性风险防范"
            }
        }
    
    def _generate_personalized_advice(self) -> Dict:
        """生成个性化建议"""
        advice = {
            "immediate_actions": [
                "根据当前价格调整买入计划",
                "设置价格预警监控",
                "准备投资资金，分批入场"
            ],
            "weekly_checklist": [
                "复盘投资组合表现",
                "检查止损止盈触发情况",
                "关注市场情绪变化"
            ],
            "monthly_review": [
                "评估策略有效性",
                "调整投资组合权重",
                "学习新的投资知识"
            ],
            "quarterly_adjustment": [
                "全面再平衡投资组合",
                "淘汰表现不佳的股票",
                "纳入新的投资机会"
            ],
            "behavioral_guidance": [
                "保持耐心，避免频繁交易",
                "控制情绪，理性决策",
                "坚持投资纪律，不随意更改策略"
            ]
        }
        
        # 根据风险偏好调整建议
        if self.user_risk_profile == "激进型":
            advice["risk_warning"] = "注意控制仓位，避免过度集中，严格执行止损"
        elif self.user_risk_profile == "保守型":
            advice["risk_warning"] = "保持充足现金储备，优先配置低风险股票，注重本金安全"
        else:
            advice["risk_warning"] = "平衡收益与风险，适度分散投资，定期再平衡"
        
        return advice
    
    def _display_investment_wisdom(self):
        """显示投资智慧摘要"""
        wisdom = self.investment_wisdom
        print(f"  🌟 系统理解: {wisdom['system_understanding']['core_insight']}")
        print(f"  🎯 核心判断: {wisdom['value_judgment']['core_judgment']}")
        print(f"  📊 市场展望: {wisdom['value_judgment']['market_outlook']}")
        
        # 显示短期决策
        short_term = wisdom['future_decisions']['short_term_1_3m']
        print(f"  ⏰ 短期重点: {short_term['focus']}")
        print(f"  🎯 短期目标: {short_term['target']}")
    
    # ==================== 完整报告生成 ====================
    
    def generate_complete_report(self) -> Dict:
        """
        生成完整的DIKW投资报告
        返回: 包含所有层级的完整报告
        """
        print("\n📋 正在生成完整投资报告...")
        
        # 执行完整的DIKW流程
        data_layer = self.fetch_stock_data()
        info_layer = self.analyze_market_info()
        knowledge_layer = self.generate_investment_knowledge()
        wisdom_layer = self.generate_investment_wisdom()
        
        complete_report = {
            "report_metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_profile": self.user_risk_profile,
                "investment_amount": self.investment_amount,
                "stocks_analyzed": len(self.stock_data),
                "framework": "DIKW (数据-信息-知识-智慧)"
            },
            "data_layer": data_layer,
            "info_layer": info_layer,
            "knowledge_layer": knowledge_layer,
            "wisdom_layer": wisdom_layer
        }
        
        print("✅ 完整报告生成完成!")
        return complete_report
    
    def save_report_to_file(self, report: Dict, filename: str = None):
        """保存报告到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_investment_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📁 报告已保存到: {filename}")
        return filename
    
    def display_summary_report(self):
        """显示摘要报告（命令行友好格式）"""
        print("\n" + "="*60)
        print("📋 股票投资决策摘要报告")
        print("="*60)
        
        # 显示关键信息
        print(f"\n📊 市场概况:")
        sentiment = self.market_analysis.get('market_sentiment', {})
        if sentiment:
            print(f"  • 市场趋势: {sentiment.get('market_trend', '未知')}")
            print(f"  • 涨跌比例: {sentiment.get('rising_count', 0)}涨/{sentiment.get('falling_count', 0)}跌")
            print(f"  • 平均涨跌: {sentiment.get('average_change', 0):+.2f}%")
        
        print(f"\n🎯 投资策略 ({self.user_risk_profile}):")
        knowledge = self.investment_knowledge
        if knowledge:
            config = knowledge.get('strategy_config', {})
            print(f"  • 目标收益: {config.get('target_return', '未知')}")
            print(f"  • 最大回撤: {config.get('max_drawdown', '未知')}")
            print(f"  • 持有期限: {config.get('holding_period', '未知')}")
        
        print(f"\n💰 投资组合建议:")
        portfolio = knowledge.get('portfolio_allocation', {}) if knowledge else {}
        total_invested = sum(alloc.get('investment_amount', 0) for alloc in portfolio.values())
        cash_reserve = self.investment_amount - total_invested
        
        for name, alloc in portfolio.items():
            print(f"  • {name}: {alloc.get('weight_percent', 0):.1f}% (¥{alloc.get('investment_amount', 0):.0f})")
        print(f"  • 现金储备: ¥{cash_reserve:.0f} ({cash_reserve/self.investment_amount*100:.1f}%)")
        
        print(f"\n🌟 核心智慧:")
        wisdom = self.investment_wisdom
        if wisdom:
            judgment = wisdom.get('value_judgment', {})
            print(f"  • 市场展望: {judgment.get('market_outlook', '未知')}")
            print(f"  • 核心判断: {judgment.get('core_judgment', '未知')}")
            
            decisions = wisdom.get('future_decisions', {})
            short_term = decisions.get('short_term_1_3m', {})
            print(f"  • 短期重点: {short_term.get('focus', '未知')}")
        
        print(f"\n⏰ 择时建议:")
        timing = knowledge.get('timing_strategy', {}) if knowledge else {}
        print(f"  • 当前时段: {timing.get('current_timing', '未知')}")
        print(f"  • 建议操作: {timing.get('recommended_action', '未知')}")
        
        print(f"\n🛡️ 风险控制:")
        risk_rules = knowledge.get('risk_control_rules', {}) if knowledge else {}
        stop_loss = risk_rules.get('stop_loss_rules', {}).get(self.user_risk_profile, {})
        print(f"  • 止损设置: {stop_loss.get('stop_loss', '未知')}%")
        print(f"  • 止盈目标: {stop_loss.get('take_profit', '未知')}%")
        
        print("\n" + "="*60)
        print("💡 立即行动建议:")
        advice = wisdom.get('personalized_advice', {}) if wisdom else {}
        immediate = advice.get('immediate_actions', [])
        for i, action in enumerate(immediate[:3], 1):
            print(f"  {i}. {action}")
        
        print("\n⚠️  风险提示:")
        print("  • 投资有风险，入市需谨慎")
        print("  • 本报告仅供参考，不构成投资建议")
        print("  • 请根据自身风险承受能力做出决策")
        
        print("="*60)
