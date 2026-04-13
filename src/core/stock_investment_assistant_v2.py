#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资决策辅助系统 - 增强版（基于DIKW框架）
版本: 2.0
作者: DT老炮
日期: 2026-04-10

功能:
1. 数据层: 实时获取8只股票数据
2. 信息层: 分析市场情绪、板块轮动、技术指标
3. 知识层: 生成投资策略和风险控制方案（含投资组合优化）
4. 智慧层: 提供个性化投资建议和决策支持（含动态风险控制和智能择时）
"""

import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys
import os

# 设置系统编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入新增模块
from analysis.technical_indicators import TechnicalIndicators
from analysis.advanced_analyzer import SectorAnalyzer, RiskAnalyzer, CapitalFlowAnalyzer
from analysis.portfolio_optimizer import PortfolioOptimizer
from analysis.risk_timing import DynamicRiskController, TimingStrategy
from analysis.report_analyzer import ReportAnalyzer

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

# ==================== 增强版DIKW框架核心类 ====================

class EnhancedDIKWStockAssistant:
    """增强版DIKW股票投资决策辅助系统"""
    
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
        
        # 初始化新增模块
        self.technical_indicators = TechnicalIndicators()
        self.sector_analyzer = SectorAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.capital_flow_analyzer = CapitalFlowAnalyzer()
        self.portfolio_optimizer = PortfolioOptimizer()
        self.risk_controller = DynamicRiskController()
        self.timing_strategy = TimingStrategy()
        self.report_analyzer = ReportAnalyzer(self)
        
        print(f"🎯 股票投资决策辅助系统 v2.0 启动")
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
                if symbol.endswith(".SZ"):
                    market = "sz"
                    code = symbol.replace(".SZ", "")
                else:
                    market = "sh"
                    code = symbol.replace(".SS", "")
                
                url = f"http://hq.sinajs.cn/list={market}{code}"
                print(f"  GET {url}")
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Referer": "https://finance.sina.com.cn/"
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                print(f"  {response.status_code} {response.reason}")
                
                if response.status_code == 200:
                    content = response.text
                    data_str = content.split('"')[1]
                    if data_str:
                        data_parts = data_str.split(',')
                        if len(data_parts) > 3:
                            current_price = float(data_parts[3])
                            open_price = float(data_parts[1])
                            high_price = float(data_parts[4])
                            low_price = float(data_parts[5])
                            volume = float(data_parts[8])
                            
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
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  ✗ {name}: 数据获取失败 - {str(e)}")
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
    
    # ==================== 信息层: 数据转化为信息（增强版） ====================
    
    def analyze_market_info(self) -> Dict:
        """
        信息层: 分析市场信息（增强版，含技术指标、板块分析、资金流向）
        返回: 市场分析报告
        """
        print("\n📊 信息层: 正在进行深度市场分析...")
        
        if not self.stock_data:
            self.fetch_stock_data()
        
        # 1. 基础市场情绪分析
        rising_stocks = [s for s in self.stock_data.values() if s["change_percent"] > 0]
        falling_stocks = [s for s in self.stock_data.values() if s["change_percent"] < 0]
        
        market_sentiment = {
            "rising_count": len(rising_stocks),
            "falling_count": len(falling_stocks),
            "rising_percent": len(rising_stocks) / len(self.stock_data) * 100,
            "average_change": sum(s["change_percent"] for s in self.stock_data.values()) / len(self.stock_data),
            "market_trend": self._determine_market_trend()
        }
        
        # 2. 板块深度分析（新增）
        print("  📊 执行板块深度分析...")
        sector_analysis = self.sector_analyzer.analyze_sectors(self.stock_data)
        
        # 3. 技术指标分析（新增）
        print("  📈 执行技术指标分析...")
        technical_analysis = {}
        for name, data in self.stock_data.items():
            data['name'] = name
            technical_analysis[name] = self.technical_indicators.generate_technical_report(data)
        
        # 4. 资金流向分析（新增）
        print("  💰 执行资金流向分析...")
        capital_flow = self.capital_flow_analyzer.analyze_capital_flow(self.stock_data)
        
        self.market_analysis = {
            "market_sentiment": market_sentiment,
            "sector_analysis": sector_analysis,
            "technical_analysis": technical_analysis,
            "capital_flow": capital_flow,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 信息层完成: 深度市场分析报告生成")
        self._display_market_info_enhanced()
        return self.market_analysis
    
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
    
    def _display_market_info_enhanced(self):
        """显示增强版市场信息摘要"""
        sentiment = self.market_analysis["market_sentiment"]
        print(f"  📈 市场情绪: {sentiment['market_trend']}")
        print(f"  📊 涨跌比例: {sentiment['rising_count']}涨/{sentiment['falling_count']}跌 ({sentiment['rising_percent']:.1f}%上涨)")
        print(f"  📉 平均涨跌: {sentiment['average_change']:+.2f}%")
        
        # 显示板块排名
        sector_ranking = self.market_analysis['sector_analysis']['sector_ranking']
        if sector_ranking:
            print(f"  🎯 最强板块: {sector_ranking[0]['sector']} (+{sector_ranking[0]['avg_change']:.2f}%)")
        
        # 显示资金流向
        flow_trend = self.market_analysis['capital_flow']['flow_trend']
        print(f"  💰 资金流向: {flow_trend['trend']} (¥{abs(flow_trend['net_flow']):,.0f})")
    
    # ==================== 知识层: 信息转化为知识（增强版） ====================
    
    def generate_investment_knowledge(self) -> Dict:
        """
        知识层: 生成投资知识（增强版，含投资组合优化）
        返回: 投资知识库
        """
        print("\n🧠 知识层: 正在生成投资知识...")
        
        if not self.market_analysis:
            self.analyze_market_info()
        
        # 1. 根据用户风险偏好选择策略
        strategy_config = INVESTMENT_STRATEGIES[self.user_risk_profile]
        
        # 2. 股票筛选和分类
        recommended_stocks = self._filter_stocks_by_risk()
        
        # 3. 投资组合优化（新增）
        print("  🎯 执行投资组合优化...")
        optimized_portfolio = self.portfolio_optimizer.optimize_portfolio(
            recommended_stocks, 
            method='mean_variance', 
            risk_profile=self.user_risk_profile
        )
        
        # 4. 构建投资组合
        portfolio = self._build_portfolio_enhanced(recommended_stocks, optimized_portfolio)
        
        # 5. 风险分析（新增）
        print("  🛡️ 执行组合风险分析...")
        risk_analysis = self.risk_analyzer.analyze_portfolio_risk(self.stock_data, portfolio)
        
        # 6. 风险控制规则
        risk_rules = self._generate_risk_rules()
        
        # 7. 择时策略（新增）
        timing_analysis = self.timing_strategy.analyze_timing(
            self.stock_data, 
            self.market_analysis, 
            self.user_risk_profile
        )
        
        self.investment_knowledge = {
            "user_profile": self.user_risk_profile,
            "strategy_config": strategy_config,
            "recommended_stocks": recommended_stocks,
            "optimized_portfolio": optimized_portfolio,
            "portfolio_allocation": portfolio,
            "risk_analysis": risk_analysis,
            "risk_control_rules": risk_rules,
            "timing_analysis": timing_analysis,
            "knowledge_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 知识层完成: 投资知识库生成")
        self._display_investment_knowledge_enhanced()
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
                change = data["change_percent"]
                if self.user_risk_profile == "激进型" or abs(change) < 5:
                    filtered[name] = data
        
        return filtered
    
    def _build_portfolio_enhanced(self, stocks: Dict, optimized: Dict) -> Dict:
        """构建投资组合（增强版，使用优化权重）"""
        total_investment = self.investment_amount
        
        # 使用优化后的权重
        weights = optimized.get('weights', {})
        
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
    
    def _generate_risk_rules(self) -> Dict:
        """生成风险控制规则"""
        rules = {
            "position_limits": {
                "max_single_stock": 20,
                "max_single_sector": 40,
                "cash_reserve": 15 if self.user_risk_profile == "保守型" else 10
            },
            "stop_loss_rules": {
                "激进型": {"stop_loss": 8, "take_profit": 20},
                "稳健型": {"stop_loss": 6, "take_profit": 15},
                "保守型": {"stop_loss": 4, "take_profit": 10}
            },
            "rebalancing_rules": {
                "frequency": "季度",
                "threshold": 5,
                "method": "再平衡至目标权重"
            }
        }
        return rules
    
    def _display_investment_knowledge_enhanced(self):
        """显示增强版投资知识摘要"""
        knowledge = self.investment_knowledge
        print(f"  🎯 适用策略: {knowledge['user_profile']}")
        print(f"  📊 目标收益: {knowledge['strategy_config']['target_return']}")
        print(f"  🛡️  最大回撤: {knowledge['strategy_config']['max_drawdown']}")
        print(f"  📈 推荐股票: {len(knowledge['recommended_stocks'])}只")
        
        # 显示优化指标
        optimized = knowledge['optimized_portfolio']
        if optimized.get('status') == 'success':
            print(f"  📊 组合夏普比率: {optimized.get('sharpe_ratio', 0):.3f}")
            print(f"  📊 预期年化收益: {optimized.get('expected_return', 0)*100:.2f}%")
        
        # 显示投资组合
        print("  💰 投资组合分配:")
        portfolio = knowledge['portfolio_allocation']
        for name, alloc in portfolio.items():
            print(f"    • {name}: {alloc['weight_percent']:.1f}% (¥{alloc['investment_amount']:.0f}, {alloc['shares']}股)")
        
        # 显示风险等级
        risk_level = knowledge['risk_analysis'].get('risk_level', '未知')
        print(f"  ⚠️  组合风险等级: {risk_level}")
    
    # ==================== 智慧层: 知识转化为智慧（增强版） ====================
    
    def generate_investment_wisdom(self) -> Dict:
        """
        智慧层: 生成投资智慧（增强版，含动态风险控制和智能择时）
        返回: 投资智慧报告
        """
        print("\n🌟 智慧层: 正在生成投资智慧...")
        
        if not self.investment_knowledge:
            self.generate_investment_knowledge()
        
        # 1. 系统理解
        system_understanding = self._understand_investment_system()
        
        # 2. 价值判断
        value_judgment = self._make_value_judgment()
        
        # 3. 动态风险控制（新增）
        print("  🛡️ 生成动态风险控制建议...")
        dynamic_risk_control = self._generate_dynamic_risk_control()
        
        # 4. 智能择时建议（新增）
        print("  ⏰ 生成智能择时建议...")
        timing_recommendations = self._generate_timing_recommendations()
        
        # 5. 未来决策
        future_decisions = self._make_future_decisions()
        
        # 6. 个性化建议
        personalized_advice = self._generate_personalized_advice()
        
        self.investment_wisdom = {
            "system_understanding": system_understanding,
            "value_judgment": value_judgment,
            "dynamic_risk_control": dynamic_risk_control,
            "timing_recommendations": timing_recommendations,
            "future_decisions": future_decisions,
            "personalized_advice": personalized_advice,
            "wisdom_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("✅ 智慧层完成: 投资智慧报告生成")
        self._display_investment_wisdom_enhanced()
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
            "priority_ranking": self._generate_priority_ranking(),
            "ethical_consideration": "避免追涨杀跌，坚持价值投资，控制情绪化交易"
        }
    
    def _generate_priority_ranking(self) -> List[str]:
        """生成优先级排名"""
        # 基于技术分析和市场表现生成排名
        rankings = []
        
        for name, tech in self.market_analysis.get('technical_analysis', {}).items():
            score = tech.get('technical_score', {}).get('score', 50)
            rankings.append((name, score))
        
        # 按评分排序
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return [f"{name} (技术评分{score:.0f}分)" for name, score in rankings[:4]]
    
    def _generate_dynamic_risk_control(self) -> Dict:
        """生成动态风险控制建议"""
        recommendations = {}
        
        # 为每只股票生成动态止损止盈建议
        for name, data in self.stock_data.items():
            market_trend = self.market_analysis['market_sentiment']['market_trend']
            
            stop_loss = self.risk_controller.adjust_stop_loss(
                data, market_trend, self.user_risk_profile, 0
            )
            
            take_profit = self.risk_controller.adjust_take_profit(
                data, market_trend, self.user_risk_profile, 0
            )
            
            recommendations[name] = {
                'stop_loss': stop_loss,
                'take_profit': take_profit
            }
        
        # 生成仓位调整建议
        portfolio = self.investment_knowledge.get('portfolio_allocation', {})
        market_volatility = self.market_analysis['market_sentiment']['average_change'] / 100
        market_trend = self.market_analysis['market_sentiment']['market_trend']
        
        position_adjustment = self.risk_controller.adjust_position(
            portfolio, market_volatility, market_trend, self.user_risk_profile
        )
        
        # 生成风险预警
        risk_alerts = self.risk_controller.generate_risk_alerts(
            self.stock_data, portfolio, self.market_analysis
        )
        
        return {
            'stock_recommendations': recommendations,
            'position_adjustment': position_adjustment,
            'risk_alerts': risk_alerts
        }
    
    def _generate_timing_recommendations(self) -> Dict:
        """生成智能择时建议"""
        timing = self.investment_knowledge.get('timing_analysis', {})
        combined_signal = timing.get('combined_signal', {})
        
        return {
            'overall_signal': combined_signal.get('signal', '持有信号'),
            'action': combined_signal.get('action', '持有观望'),
            'confidence': combined_signal.get('confidence', '中'),
            'score': combined_signal.get('score', 50),
            'reason': combined_signal.get('reason', ''),
            'best_timing': self._get_best_timing()
        }
    
    def _get_best_timing(self) -> Dict:
        """获取最佳时机"""
        timing = self.investment_knowledge.get('timing_analysis', {})
        time_timing = timing.get('time_timing', {})
        
        return {
            'current_period': time_timing.get('period', '未知'),
            'suggested_action': time_timing.get('time_action', '观望'),
            'best_buy_times': ["09:45-10:15", "13:30-14:00"],
            'best_sell_times': ["10:30-11:00", "14:30-15:00"]
        }
    
    def _make_future_decisions(self) -> Dict:
        """制定未来决策"""
        return {
            "short_term_1_3m": {
                "focus": "根据技术分析选择强势股",
                "action": "分批建仓，控制成本",
                "target": "完成核心仓位配置",
                "risk_control": "严格执行动态止损"
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
            "immediate_actions": self._generate_immediate_actions(),
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
            advice["risk_warning"] = "注意控制仓位，避免过度集中，严格执行动态止损"
        elif self.user_risk_profile == "保守型":
            advice["risk_warning"] = "保持充足现金储备，优先配置低风险股票，注重本金安全"
        else:
            advice["risk_warning"] = "平衡收益与风险，适度分散投资，定期再平衡"
        
        return advice
    
    def _generate_immediate_actions(self) -> List[str]:
        """生成立即行动建议"""
        actions = []
        
        # 基于择时信号
        timing = self.investment_knowledge.get('timing_analysis', {})
        signal = timing.get('combined_signal', {}).get('signal', '')
        
        if '买入' in signal:
            actions.append("根据择时信号，可考虑建仓或加仓")
        elif '卖出' in signal:
            actions.append("根据择时信号，考虑减仓或止损")
        else:
            actions.append("当前持有观望，等待更好时机")
        
        # 基于技术分析
        actions.append("根据技术指标设置价格预警监控")
        actions.append("准备投资资金，按计划分批入场")
        
        return actions
    
    def _display_investment_wisdom_enhanced(self):
        """显示增强版投资智慧摘要"""
        wisdom = self.investment_wisdom
        print(f"  🌟 系统理解: {wisdom['system_understanding']['core_insight']}")
        print(f"  🎯 核心判断: {wisdom['value_judgment']['core_judgment']}")
        print(f"  📊 市场展望: {wisdom['value_judgment']['market_outlook']}")
        
        # 显示择时建议
        timing = wisdom['timing_recommendations']
        print(f"  ⏰ 择时信号: {timing['overall_signal']} (评分{timing['score']:.0f})")
        print(f"  📋 建议操作: {timing['action']}")
        
        # 显示风险预警数量
        risk_alerts = wisdom['dynamic_risk_control'].get('risk_alerts', [])
        if risk_alerts:
            print(f"  ⚠️  风险预警: {len(risk_alerts)}项")
    
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
                "framework": "Enhanced DIKW (数据-信息-知识-智慧) v2.0"
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
            filename = f"stock_investment_report_v2_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📁 报告已保存到: {filename}")
        return filename
    
    def display_summary_report(self):
        """显示摘要报告（增强版）"""
        print("\n" + "="*60)
        print("📋 股票投资决策摘要报告 v2.0")
        print("="*60)
        
        # 显示市场概况
        print(f"\n📊 市场概况:")
        sentiment = self.market_analysis.get('market_sentiment', {})
        if sentiment:
            print(f"  • 市场趋势: {sentiment.get('market_trend', '未知')}")
            print(f"  • 涨跌比例: {sentiment.get('rising_count', 0)}涨/{sentiment.get('falling_count', 0)}跌")
            print(f"  • 平均涨跌: {sentiment.get('average_change', 0):+.2f}%")
        
        # 显示板块信息
        sector_ranking = self.market_analysis.get('sector_analysis', {}).get('sector_ranking', [])
        if sector_ranking:
            print(f"\n🎯 板块表现:")
            for i, sector in enumerate(sector_ranking[:3], 1):
                print(f"  {i}. {sector['sector']}: {sector['avg_change']:+.2f}% ({sector['strength']})")
        
        # 显示投资策略
        print(f"\n🎯 投资策略 ({self.user_risk_profile}):")
        knowledge = self.investment_knowledge
        if knowledge:
            config = knowledge.get('strategy_config', {})
            print(f"  • 目标收益: {config.get('target_return', '未知')}")
            print(f"  • 最大回撤: {config.get('max_drawdown', '未知')}")
            print(f"  • 持有期限: {config.get('holding_period', '未知')}")
            
            # 显示优化指标
            optimized = knowledge.get('optimized_portfolio', {})
            if optimized.get('status') == 'success':
                print(f"  • 夏普比率: {optimized.get('sharpe_ratio', 0):.3f}")
                print(f"  • 预期收益: {optimized.get('expected_return', 0)*100:.2f}%")
        
        # 显示投资组合
        print(f"\n💰 投资组合建议:")
        portfolio = knowledge.get('portfolio_allocation', {}) if knowledge else {}
        total_invested = sum(alloc.get('investment_amount', 0) for alloc in portfolio.values())
        cash_reserve = self.investment_amount - total_invested
        
        for name, alloc in portfolio.items():
            print(f"  • {name}: {alloc.get('weight_percent', 0):.1f}% (¥{alloc.get('investment_amount', 0):.0f})")
        print(f"  • 现金储备: ¥{cash_reserve:.0f} ({cash_reserve/self.investment_amount*100:.1f}%)")
        
        # 显示风险分析
        print(f"\n🛡️ 风险分析:")
        risk_analysis = knowledge.get('risk_analysis', {}) if knowledge else {}
        print(f"  • 风险等级: {risk_analysis.get('risk_level', '未知')}")
        var = risk_analysis.get('var', {})
        if var:
            print(f"  • VaR(95%): ¥{var.get('var_95', 0):.2f} ({var.get('var_95_percent', 0):.2f}%)")
        
        # 显示择时建议
        print(f"\n⏰ 择时建议:")
        timing = knowledge.get('timing_analysis', {}) if knowledge else {}
        combined = timing.get('combined_signal', {})
        print(f"  • 综合信号: {combined.get('signal', '未知')} (评分{combined.get('score', 50):.0f})")
        print(f"  • 建议操作: {combined.get('action', '未知')}")
        
        # 显示核心智慧
        print(f"\n🌟 核心智慧:")
        wisdom = self.investment_wisdom
        if wisdom:
            judgment = wisdom.get('value_judgment', {})
            print(f"  • 市场展望: {judgment.get('market_outlook', '未知')}")
            print(f"  • 核心判断: {judgment.get('core_judgment', '未知')}")
            
            # 显示风险预警
            risk_alerts = wisdom.get('dynamic_risk_control', {}).get('risk_alerts', [])
            if risk_alerts:
                print(f"  • 风险预警: {len(risk_alerts)}项")
        
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
    
    def generate_reports(self, report_types: List[str] = None, formats: List[str] = None) -> List[str]:
        """
        生成报告
        
        Args:
            report_types: 报告类型列表，默认包含所有类型
            formats: 输出格式列表，默认包含json和csv
            
        Returns:
            生成的报告文件路径列表
        """
        if report_types is None:
            report_types = ["summary", "technical", "portfolio", "risk"]
        if formats is None:
            formats = ["json", "csv"]
        
        generated_files = []
        for report_type in report_types:
            for fmt in formats:
                try:
                    file_path = self.report_analyzer.generate_report(report_type, fmt)
                    generated_files.append(file_path)
                except Exception as e:
                    print(f"生成{report_type}报告({fmt})失败: {str(e)}")
        
        return generated_files


# 使用示例
if __name__ == "__main__":
    # 创建增强版投资助手实例
    assistant = EnhancedDIKWStockAssistant(
        user_risk_profile="稳健型",
        investment_amount=100000
    )
    
    # 生成完整报告
    report = assistant.generate_complete_report()
    
    # 显示摘要报告
    assistant.display_summary_report()
    
    # 生成各种类型的报告
    print("\n📋 正在生成报告...")
    generated_files = assistant.generate_reports()
    print(f"✅ 生成了 {len(generated_files)} 个报告文件")
