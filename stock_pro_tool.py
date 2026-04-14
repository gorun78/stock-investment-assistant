#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业股票投资辅助工具 - 核心框架
版本: 2.0
作者: DT老炮
日期: 2026-04-14

基于DIKW框架的专业股票投资分析工具，集成多数据源、AI分析和智能监控。
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import argparse
from pathlib import Path

# ==================== 配置管理 ====================

class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "version": "2.0",
        "data_sources": {
            "sina": {"enabled": True, "priority": 1},
            "eastmoney": {"enabled": True, "priority": 2},
            "tushare": {"enabled": False, "priority": 3, "token": ""}
        },
        "analysis": {
            "technical": True,
            "fundamental": True,
            "sentiment": True,
            "ai_analysis": False
        },
        "monitoring": {
            "enabled": True,
            "interval_minutes": 5,
            "alert_threshold_percent": 2.0,
            "working_hours": ["09:30", "15:00"]
        },
        "risk_management": {
            "max_single_position": 20,
            "max_sector_exposure": 40,
            "stop_loss_default": 8,
            "take_profit_default": 20
        },
        "reporting": {
            "format": ["console", "json"],
            "save_path": "./reports",
            "generate_charts": True
        }
    }
    
    def __init__(self, config_path: str = "~/.stock_pro_tool/config.json"):
        self.config_path = Path(config_path).expanduser()
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"配置文件加载失败: {e}, 使用默认配置")
        
        # 创建配置目录
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"配置文件保存失败: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

# ==================== 数据模型 ====================

class RiskLevel(Enum):
    """风险等级"""
    LOW = "低"
    MEDIUM = "中等"
    HIGH = "高"

class Market(Enum):
    """市场类型"""
    SH = "上海"
    SZ = "深圳"
    HK = "香港"
    US = "美国"

@dataclass
class Stock:
    """股票数据模型"""
    symbol: str
    name: str
    market: Market
    sector: str
    risk_level: RiskLevel
    current_price: float = 0.0
    open_price: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    volume: int = 0
    amount: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "market": self.market.value,
            "sector": self.sector,
            "risk_level": self.risk_level.value,
            "current_price": self.current_price,
            "open_price": self.open_price,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "volume": self.volume,
            "amount": self.amount,
            "change": self.change,
            "change_percent": self.change_percent,
            "pe_ratio": self.pe_ratio,
            "pb_ratio": self.pb_ratio,
            "market_cap": self.market_cap,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class PortfolioAllocation:
    """投资组合分配"""
    stock: Stock
    weight_percent: float
    target_shares: int
    target_amount: float
    current_shares: int = 0
    current_amount: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "stock": self.stock.to_dict(),
            "weight_percent": self.weight_percent,
            "target_shares": self.target_shares,
            "target_amount": self.target_amount,
            "current_shares": self.current_shares,
            "current_amount": self.current_amount
        }

# ==================== 数据服务层 ====================

class DataFetcher:
    """数据获取器 - 多数据源支持"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    async def fetch_stock_data(self, symbol: str) -> Optional[Stock]:
        """获取股票数据（异步）"""
        # 检查缓存
        cache_key = f"stock_{symbol}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        # 按优先级尝试不同数据源
        data_sources = self.config.get("data_sources", {})
        sorted_sources = sorted(
            [(k, v) for k, v in data_sources.items() if v.get("enabled", False)],
            key=lambda x: x[1].get("priority", 99)
        )
        
        for source_name, source_config in sorted_sources:
            try:
                if source_name == "sina":
                    data = await self._fetch_from_sina(symbol)
                elif source_name == "eastmoney":
                    data = await self._fetch_from_eastmoney(symbol)
                elif source_name == "tushare":
                    data = await self._fetch_from_tushare(symbol)
                else:
                    continue
                
                if data:
                    self.cache[cache_key] = (data, datetime.now())
                    return data
            except Exception as e:
                logging.warning(f"数据源 {source_name} 获取失败: {e}")
                continue
        
        return None
    
    async def _fetch_from_sina(self, symbol: str) -> Optional[Stock]:
        """从新浪财经获取数据"""
        import aiohttp
        
        # 解析symbol
        if symbol.endswith('.SZ'):
            market = 'sz'
            code = symbol.replace('.SZ', '')
        elif symbol.endswith('.SH'):
            market = 'sh'
            code = symbol.replace('.SH', '')
        else:
            return None
        
        url = f"http://hq.sinajs.cn/list={market}{code}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    # 解析新浪财经格式
                    data_str = text.split('"')[1]
                    if data_str:
                        parts = data_str.split(',')
                        if len(parts) >= 32:
                            return Stock(
                                symbol=symbol,
                                name=parts[0],
                                market=Market.SZ if market == 'sz' else Market.SH,
                                sector="",  # 需要额外接口获取
                                risk_level=RiskLevel.MEDIUM,
                                current_price=float(parts[3]),
                                open_price=float(parts[1]),
                                high_price=float(parts[4]),
                                low_price=float(parts[5]),
                                volume=int(float(parts[8])),
                                amount=float(parts[9]),
                                change=float(parts[3]) - float(parts[2]),
                                change_percent=(float(parts[3]) - float(parts[2])) / float(parts[2]) * 100
                            )
        return None
    
    async def _fetch_from_eastmoney(self, symbol: str) -> Optional[Stock]:
        """从东方财富获取数据（简化版）"""
        # TODO: 实现东方财富API
        return None
    
    async def _fetch_from_tushare(self, symbol: str) -> Optional[Stock]:
        """从Tushare获取数据"""
        # TODO: 实现Tushare API
        return None
    
    def fetch_batch_stocks(self, symbols: List[str]) -> Dict[str, Stock]:
        """批量获取股票数据"""
        results = {}
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def fetch_all():
            tasks = [self.fetch_stock_data(symbol) for symbol in symbols]
            stock_data = await asyncio.gather(*tasks)
            for symbol, data in zip(symbols, stock_data):
                if data:
                    results[symbol] = data
        
        loop.run_until_complete(fetch_all())
        loop.close()
        return results

# ==================== DIKW分析引擎 ====================

class DIKWEngine:
    """DIKW分析引擎"""
    
    def __init__(self, config: ConfigManager, data_fetcher: DataFetcher):
        self.config = config
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)
    
    # ========== 数据层 ==========
    
    async def data_layer(self, symbols: List[str]) -> Dict[str, Stock]:
        """数据层：获取原始数据"""
        self.logger.info("数据层：获取股票原始数据")
        
        stock_data = {}
        for symbol in symbols:
            data = await self.data_fetcher.fetch_stock_data(symbol)
            if data:
                stock_data[symbol] = data
                self.logger.debug(f"获取到 {symbol}: ¥{data.current_price:.2f} ({data.change_percent:+.2f}%)")
            else:
                self.logger.warning(f"获取 {symbol} 数据失败")
        
        return stock_data
    
    # ========== 信息层 ==========
    
    def information_layer(self, stock_data: Dict[str, Stock]) -> Dict:
        """信息层：数据转化为信息"""
        self.logger.info("信息层：分析市场信息")
        
        if not stock_data:
            return {}
        
        # 市场情绪分析
        rising_stocks = [s for s in stock_data.values() if s.change_percent > 0]
        falling_stocks = [s for s in stock_data.values() if s.change_percent < 0]
        
        # 板块分析
        sector_performance = {}
        for stock in stock_data.values():
            if stock.sector not in sector_performance:
                sector_performance[stock.sector] = []
            sector_performance[stock.sector].append(stock.change_percent)
        
        # 风险收益特征
        risk_return_analysis = {}
        for symbol, stock in stock_data.items():
            volatility = abs(stock.high_price - stock.low_price) / stock.open_price * 100 if stock.open_price > 0 else 0
            risk_return_analysis[symbol] = {
                "volatility": volatility,
                "risk_level": stock.risk_level.value,
                "return_potential": self._estimate_return_potential(stock)
            }
        
        return {
            "market_sentiment": {
                "rising_count": len(rising_stocks),
                "falling_count": len(falling_stocks),
                "rising_percent": len(rising_stocks) / len(stock_data) * 100,
                "average_change": sum(s.change_percent for s in stock_data.values()) / len(stock_data),
                "strongest_sector": self._find_strongest_sector(sector_performance),
                "market_trend": self._determine_market_trend(stock_data)
            },
            "sector_analysis": sector_performance,
            "risk_return_analysis": risk_return_analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _find_strongest_sector(self, sector_performance: Dict) -> str:
        """找出表现最强的板块"""
        best_sector = None
        best_avg = -100
        
        for sector, changes in sector_performance.items():
            if changes:
                avg_change = sum(changes) / len(changes)
                if avg_change > best_avg:
                    best_avg = avg_change
                    best_sector = sector
        
        return best_sector if best_sector else "未知"
    
    def _determine_market_trend(self, stock_data: Dict[str, Stock]) -> str:
        """判断市场趋势"""
        avg_change = sum(s.change_percent for s in stock_data.values()) / len(stock_data)
        
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
    
    def _estimate_return_potential(self, stock: Stock) -> str:
        """估算回报潜力"""
        change = stock.change_percent
        volatility = abs(stock.high_price - stock.low_price) / stock.open_price * 100 if stock.open_price > 0 else 0
        
        if change > 3 and volatility < 5:
            return "高"
        elif change > 1 and volatility < 8:
            return "中高"
        elif change > -1:
            return "中等"
        else:
            return "低"
    
    # ========== 知识层 ==========
    
    def knowledge_layer(self, stock_data: Dict[str, Stock], 
                       market_info: Dict,
                       user_profile: str = "稳健型",
                       investment_amount: float = 100000) -> Dict:
        """知识层：信息转化为知识"""
        self.logger.info("知识层：生成投资知识")
        
        # 投资策略配置
        strategies = {
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
        
        strategy_config = strategies.get(user_profile, strategies["稳健型"])
        
        # 股票筛选
        recommended_stocks = self._filter_stocks_by_risk(stock_data, user_profile)
        
        # 投资组合构建
        portfolio = self._build_portfolio(recommended_stocks, user_profile, investment_amount)
        
        # 风险控制规则
        risk_rules = self._generate_risk_rules(user_profile)
        
        # 择时策略
        timing_strategy = self._generate_timing_strategy()
        
        return {
            "user_profile": user_profile,
            "strategy_config": strategy_config,
            "recommended_stocks": {k: v.to_dict() for k, v in recommended_stocks.items()},
            "portfolio_allocation": {k: v.to_dict() for k, v in portfolio.items()},
            "risk_control_rules": risk_rules,
            "timing_strategy": timing_strategy,
            "timestamp": datetime.now().isoformat()
        }
    
    def _filter_stocks_by_risk(self, stock_data: Dict[str, Stock], user_profile: str) -> Dict[str, Stock]:
        """根据风险偏好筛选股票"""
        risk_mapping = {
            "激进型": [RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW],
            "稳健型": [RiskLevel.MEDIUM, RiskLevel.LOW],
            "保守型": [RiskLevel.LOW]
        }
        
        allowed_risks = risk_mapping.get(user_profile, [RiskLevel.MEDIUM, RiskLevel.LOW])
        filtered = {}
        
        for symbol, stock in stock_data.items():
            if stock.risk_level in allowed_risks:
                # 避免追涨杀跌
                if user_profile == "激进型" or abs(stock.change_percent) < 5:
                    filtered[symbol] = stock
        
        return filtered
    
    def _build_portfolio(self, stocks: Dict[str, Stock], 
                        user_profile: str, 
                        investment_amount: float) -> Dict[str, PortfolioAllocation]:
        """构建投资组合"""
        if not stocks:
            return {}
        
        # 根据风险偏好分配权重
        if user_profile == "激进型":
            weights = self._calculate_aggressive_weights(stocks)
        elif user_profile == "稳健型":
            weights = self._calculate_moderate_weights(stocks)
        else:  # 保守型
            weights = self._calculate_conservative_weights(stocks)
        
        portfolio = {}
        for symbol, weight in weights.items():
            if symbol in stocks:
                stock = stocks[symbol]
                amount = investment_amount * weight / 100
                shares = int(amount / stock.current_price) if stock.current_price > 0 else 0
                actual_amount = shares * stock.current_price
                
                portfolio[symbol] = PortfolioAllocation(
                    stock=stock,
                    weight_percent=weight,
                    target_shares=shares,
                    target_amount=actual_amount
                )
        
        return portfolio
    
    def _calculate_aggressive_weights(self, stocks: Dict[str, Stock]) -> Dict[str, float]:
        """计算激进型权重"""
        weights = {}
        stock_count = len(stocks)
        
        if stock_count >= 3:
            # 按涨跌幅排序，前3只重仓
            sorted_stocks = sorted(
                stocks.items(), 
                key=lambda x: x[1].change_percent, 
                reverse=True
            )
            
            # 分配权重
            for i, (symbol, _) in enumerate(sorted_stocks[:3]):
                if i == 0:
                    weights[symbol] = 25
                elif i == 1:
                    weights[symbol] = 22
                else:
                    weights[symbol] = 18
            
            # 剩余股票平均分配
            remaining_weight = 35
            remaining_stocks = sorted_stocks[3:]
            if remaining_stocks:
                weight_per_stock = remaining_weight / len(remaining_stocks)
                for symbol, _ in remaining_stocks:
                    weights[symbol] = weight_per_stock
        else:
            # 平均分配
            weight_per_stock = 100 / stock_count
            for symbol in stocks:
                weights[symbol] = weight_per_stock
        
        return weights
    
    def _calculate_moderate_weights(self, stocks: Dict[str, Stock]) -> Dict[str, float]:
        """计算稳健型权重"""
        weights = {}
        
        # 按板块分配
        sectors = {}
        for symbol, stock in stocks.items():
            if stock.sector not in sectors:
                sectors[stock.sector] = []
            sectors[stock.sector].append(symbol)
        
        if sectors:
            sector_weight = 100 / len(sectors)
            for sector, symbol_list in sectors.items():
                stock_weight = sector_weight / len(symbol_list)
                for symbol in symbol_list:
                    weights[symbol] = stock_weight
        else:
            # 平均分配
            weight_per_stock = 100 / len(stocks)
            for symbol in stocks:
                weights[symbol] = weight_per_stock
        
        return weights
    
    def _calculate_conservative_weights(self, stocks: Dict[str, Stock]) -> Dict[str, float]:
        """计算保守型权重"""
        weights = {}
        stock_count = len(stocks)
        
        # 基础权重
        base_weight = 100 / stock_count
        
        for symbol, stock in stocks.items():
            # 低风险股票权重稍高
            if stock.risk_level == RiskLevel.LOW:
                weights[symbol] = base_weight * 1.2
            else:
                weights[symbol] = base_weight * 0.8
        
        # 归一化
        total = sum(weights.values())
        if total > 0:
            for symbol in weights:
                weights[symbol] = weights[symbol] * 100 / total
        
        return weights
    
    def _generate_risk_rules(self, user_profile: str) -> Dict:
        """生成风险控制规则"""
        rules = {
            "position_limits": {
                "max_single_stock": 20,
                "max_single_sector": 40,
                "cash_reserve": 15 if user_profile == "保守型" else 10
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
            "avoid_times": ["09:30-09:35", "14:55-15:00"]
        }
    
    # ========== 智慧层 ==========
    
    def wisdom_layer(self, stock_data: Dict[str, Stock],
                    market_info: Dict,
                    investment_knowledge: Dict) -> Dict:
        """智慧层：知识转化为智慧"""
        self.logger.info("智慧层：生成投资智慧")
        
        # 系统理解
        system_understanding = self._understand_investment_system()
        
        # 价值判断
        value_judgment = self._make_value_judgment(market_info)
        
        # 未来决策
        future_decisions = self._make_future_decisions()
        
        # 个性化建议
        personalized_advice = self._generate_personalized_advice(
            investment_knowledge["user_profile"]
        )
        
        return {
            "system_understanding": system_understanding,
            "value_judgment": value_judgment,
            "future_decisions": future_decisions,
            "personalized_advice": personalized_advice,
            "timestamp": datetime.now().isoformat()
        }
    
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
                "policy_impact": "环保政策→环保股受益，网络安全政策→网络安全股受益",
                "tech_cycle": "半导体周期→半导体股波动，AI发展→AI股成长",
                "market_sentiment": "风险偏好变化影响科技股 vs 防御股表现"
            },
            "adaptability": "不同策略在不同市场环境下的适用性不同，需要动态调整"
        }
    
    def _make_value_judgment(self, market_info: Dict) -> Dict:
        """做出价值判断"""
        sentiment = market_info.get("market_sentiment", {})
        market_trend = sentiment.get("market_trend", "未知")
        
        if market_trend in ["强势上涨", "温和上涨"]:
            market_outlook = "乐观"
            risk_appetite = "可适度增加风险暴露"
        elif market_trend == "震荡整理":
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
    
    def _generate_personalized_advice(self, user_profile: str) -> Dict:
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
        if user_profile == "激进型":
            advice["risk_warning"] = "注意控制仓位，避免过度集中，严格执行止损"
        elif user_profile == "保守型":
            advice["risk_warning"] = "保持充足现金储备，优先配置低风险股票，注重本金安全"
        else:
            advice["risk_warning"] = "平衡收益与风险，适度分散投资，定期再平衡"
        
        return advice
    
    # ========== 完整分析流程 ==========
    
    async def analyze(self, symbols: List[str], 
                     user_profile: str = "稳健型",
                     investment_amount: float = 100000) -> Dict:
        """执行完整的DIKW分析"""
        self.logger.info(f"开始DIKW分析: {len(symbols)}只股票")
        
        # 数据层
        stock_data = await self.data_layer(symbols)
        
        # 信息层
        market_info = self.information_layer(stock_data)
        
        # 知识层
        investment_knowledge = self.knowledge_layer(
            stock_data, market_info, user_profile, investment_amount
        )
        
        # 智慧层
        investment_wisdom = self.wisdom_layer(
            stock_data, market_info, investment_knowledge
        )
        
        # 整合报告
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "user_profile": user_profile,
                "investment_amount": investment_amount,
                "stocks_analyzed": len(stock_data),
                "framework": "DIKW (数据-信息-知识-智慧)"
            },
            "data_layer": {k: v.to_dict() for k, v in stock_data.items()},
            "info_layer": market_info,
            "knowledge_layer": investment_knowledge,
            "wisdom_layer": investment_wisdom
        }
        
        self.logger.info("DIKW分析完成")
        return report

# ==================== 命令行界面 ====================

class CLI:
    """命令行界面"""
    
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="专业股票投资辅助工具",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
示例:
  %(prog)s analyze --symbols 300730.SZ,688480.SS --profile 稳健型 --amount 100000
  %(prog)s monitor --config ./config.json --interval 5
  %(prog)s config --set data_sources.tushare.enabled true
            """
        )
        self.setup_arguments()
        
    def setup_arguments(self):
        """设置命令行参数"""
        subparsers = self.parser.add_subparsers(dest="command", help="命令")
        
        # analyze命令
        analyze_parser = subparsers.add_parser("analyze", help="分析股票")
        analyze_parser.add_argument("--symbols", required=True, 
                                   help="股票代码，逗号分隔 (如: 300730.SZ,688480.SS)")
        analyze_parser.add_argument("--profile", default="稳健型",
                                   choices=["激进型", "稳健型", "保守型"],
                                   help="风险偏好")
        analyze_parser.add_argument("--amount", type=float, default=100000,
                                   help="投资金额(元)")
        analyze_parser.add_argument("--output", help="输出文件路径")
        analyze_parser.add_argument("--format", default="json",
                                   choices=["json", "console", "html"],
                                   help="输出格式")
        
        # monitor命令
        monitor_parser = subparsers.add_parser("monitor", help="监控股票")
        monitor_parser.add_argument("--symbols", help="股票代码，逗号分隔")
        monitor_parser.add_argument("--config", help="配置文件路径")
        monitor_parser.add_argument("--interval", type=int, default=5,
                                   help="监控间隔(分钟)")
        monitor_parser.add_argument("--alert", type=float, default=2.0,
                                   help="预警阈值(百分比)")
        
        # config命令
        config_parser = subparsers.add_parser("config", help="配置管理")
        config_parser.add_argument("--get", help="获取配置值")
        config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"),
                                  help="设置配置值")
        config_parser.add_argument("--list", action="store_true",
                                  help="列出所有配置")
        
        # report命令
        report_parser = subparsers.add_parser("report", help="生成报告")
        report_parser.add_argument("input", help="输入文件或分析ID")
        report_parser.add_argument("--format", default="html",
                                  choices=["html", "pdf", "markdown"],
                                  help="报告格式")
        report_parser.add_argument("--output", required=True,
                                  help="输出文件路径")
        
    def run(self, args=None):
        """运行命令行界面"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return
        
        # 初始化配置
        config = ConfigManager()
        
        # 执行命令
        if parsed_args.command == "analyze":
            self.handle_analyze(parsed_args, config)
        elif parsed_args.command == "monitor":
            self.handle_monitor(parsed_args, config)
        elif parsed_args.command == "config":
            self.handle_config(parsed_args, config)
        elif parsed_args.command == "report":
            self.handle_report(parsed_args, config)
    
    def handle_analyze(self, args, config):
        """处理分析命令"""
        print("🚀 专业股票投资分析工具")
        print("="*60)
        
        # 解析股票代码
        symbols = [s.strip() for s in args.symbols.split(",")]
        
        print(f"📊 分析配置:")
        print(f"  • 股票数量: {len(symbols)}")
        print(f"  • 风险偏好: {args.profile}")
        print(f"  • 投资金额: ¥{args.amount:,}")
        print()
        
        # 创建分析引擎
        data_fetcher = DataFetcher(config)
        engine = DIKWEngine(config, data_fetcher)
        
        # 执行分析
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            report = loop.run_until_complete(
                engine.analyze(symbols, args.profile, args.amount)
            )
            loop.close()
            
            # 显示摘要
            self.display_summary(report)
            
            # 保存结果
            if args.output:
                self.save_report(report, args.output, args.format)
            elif args.format == "console":
                # 控制台输出完整报告
                print("\n" + "="*60)
                print("📋 完整分析报告:")
                print(json.dumps(report, ensure_ascii=False, indent=2))
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
    
    def display_summary(self, report: Dict):
        """显示摘要报告"""
        print("✅ 分析完成!")
        print("="*60)
        
        # 市场概况
        market_info = report.get("info_layer", {})
        sentiment = market_info.get("market_sentiment", {})
        
        print(f"📊 市场概况:")
        print(f"  • 市场趋势: {sentiment.get('market_trend', '未知')}")
        print(f"  • 涨跌比例: {sentiment.get('rising_count', 0)}涨/{sentiment.get('falling_count', 0)}跌")
        print(f"  • 平均涨跌: {sentiment.get('average_change', 0):+.2f}%")
        print(f"  • 最强板块: {sentiment.get('strongest_sector', '未知')}")
        
        # 投资策略
        knowledge = report.get("knowledge_layer", {})
        strategy = knowledge.get("strategy_config", {})
        
        print(f"\n🎯 投资策略:")
        print(f"  • 风险承受: {strategy.get('risk_tolerance', '未知')}")
        print(f"  • 目标收益: {strategy.get('target_return', '未知')}")
        print(f"  • 最大回撤: {strategy.get('max_drawdown', '未知')}")
        print(f"  • 持有期限: {strategy.get('holding_period', '未知')}")
        
        # 投资组合
        portfolio = knowledge.get("portfolio_allocation", {})
        if portfolio:
            print(f"\n💰 投资组合建议:")
            total_invested = 0
            for symbol, alloc in portfolio.items():
                stock = alloc.get("stock", {})
                amount = alloc.get("target_amount", 0)
                weight = alloc.get("weight_percent", 0)
                print(f"  • {stock.get('name', symbol)}: {weight:.1f}% (¥{amount:.0f})")
                total_invested += amount
            
            investment_amount = report["metadata"]["investment_amount"]
            cash_reserve = investment_amount - total_invested
            print(f"  • 现金储备: ¥{cash_reserve:.0f} ({cash_reserve/investment_amount*100:.1f}%)")
        
        # 核心智慧
        wisdom = report.get("wisdom_layer", {})
        judgment = wisdom.get("value_judgment", {})
        
        print(f"\n🌟 核心智慧:")
        print(f"  • 市场展望: {judgment.get('market_outlook', '未知')}")
        print(f"  • 核心判断: {judgment.get('core_judgment', '未知')}")
        
        # 择时建议
        timing = knowledge.get("timing_strategy", {})
        print(f"\n⏰ 择时建议:")
        print(f"  • 当前时段: {timing.get('current_timing', '未知')}")
        print(f"  • 建议操作: {timing.get('recommended_action', '未知')}")
        
        # 立即行动
        advice = wisdom.get("personalized_advice", {})
        immediate = advice.get("immediate_actions", [])
        if immediate:
            print(f"\n💡 立即行动:")
            for i, action in enumerate(immediate[:3], 1):
                print(f"  {i}. {action}")
        
        print("\n" + "="*60)
        print("⚠️  风险提示: 投资有风险，入市需谨慎。本报告仅供参考，不构成投资建议。")
    
    def save_report(self, report: Dict, output_path: str, format: str = "json"):
        """保存报告"""
        try:
            if format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                print(f"✅ JSON报告已保存到: {output_path}")
            elif format == "html":
                # TODO: 实现HTML报告生成
                print("⚠️  HTML报告功能开发中，暂时保存为JSON格式")
                with open(output_path.replace('.html', '.json'), 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
            else:
                print(f"⚠️  格式 {format} 暂不支持，保存为JSON格式")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
    
    def handle_monitor(self, args, config):
        """处理监控命令"""
        print("📈 股票监控系统启动中...")
        print("⚠️  监控功能开发中，敬请期待")
        # TODO: 实现监控功能
    
    def handle_config(self, args, config):
        """处理配置命令"""
        if args.get:
            value = config.get(args.get)
            print(f"{args.get} = {value}")
        elif args.set:
            key, value_str = args.set
            # 尝试解析值
            try:
                if value_str.lower() in ["true", "false"]:
                    value = value_str.lower() == "true"
                elif value_str.isdigit():
                    value = int(value_str)
                elif value_str.replace('.', '', 1).isdigit():
                    value = float(value_str)
                else:
                    value = value_str
                
                config.set(key, value)
                print(f"✅ 配置已更新: {key} = {value}")
            except Exception as e:
                print(f"❌ 配置更新失败: {e}")
        elif args.list:
            print("📋 当前配置:")
            print(json.dumps(config.config, ensure_ascii=False, indent=2))
        else:
            print("请使用 --get, --set 或 --list 参数")
    
    def handle_report(self, args, config):
        """处理报告命令"""
        print("📄 报告生成系统启动中...")
        print("⚠️  报告生成功能开发中，敬请期待")
        # TODO: 实现报告生成功能

# ==================== 主程序 ====================

def main():
    """主程序入口"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行命令行界面
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()