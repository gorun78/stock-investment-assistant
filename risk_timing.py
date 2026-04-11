#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态风险控制和智能择时策略模块
包含动态止损止盈、仓位调整、趋势跟踪择时、均值回归择时等功能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, time


class DynamicRiskController:
    """动态风险控制器"""
    
    def __init__(self):
        """初始化动态风险控制器"""
        self.base_stop_loss = {
            '激进型': 8,
            '稳健型': 6,
            '保守型': 4
        }
        self.base_take_profit = {
            '激进型': 20,
            '稳健型': 15,
            '保守型': 10
        }
    
    def adjust_stop_loss(self, stock_data: Dict, market_condition: str, 
                        risk_profile: str, holding_days: int = 0) -> Dict:
        """
        动态调整止损点
        
        Args:
            stock_data: 股票数据字典
            market_condition: 市场环境（强势上涨、温和上涨、震荡整理、温和下跌、明显下跌）
            risk_profile: 风险偏好
            holding_days: 持有天数
        
        Returns:
            止损建议
        """
        base_stop = self.base_stop_loss.get(risk_profile, 6)
        
        # 根据市场环境调整
        market_adjustment = {
            '强势上涨': 1.3,
            '温和上涨': 1.1,
            '震荡整理': 1.0,
            '温和下跌': 0.9,
            '明显下跌': 0.7
        }
        
        multiplier = market_adjustment.get(market_condition, 1.0)
        
        # 根据个股波动率调整
        volatility = self._calculate_volatility(stock_data)
        if volatility > 5:
            multiplier *= 1.2
        elif volatility < 2:
            multiplier *= 0.9
        
        # 根据持有时间调整
        if holding_days > 30:
            multiplier *= 0.95  # 长期持有，止损收紧
        
        adjusted_stop_loss = base_stop * multiplier
        
        # 计算具体止损价格
        current_price = stock_data.get('current_price', 0)
        stop_loss_price = current_price * (1 - adjusted_stop_loss / 100)
        
        return {
            'stop_loss_percent': adjusted_stop_loss,
            'stop_loss_price': stop_loss_price,
            'base_stop_loss': base_stop,
            'adjustment_factor': multiplier,
            'reason': self._explain_stop_loss_adjustment(market_condition, volatility, holding_days)
        }
    
    def adjust_take_profit(self, stock_data: Dict, market_condition: str, 
                          risk_profile: str, current_profit: float = 0) -> Dict:
        """
        动态调整止盈点
        
        Args:
            stock_data: 股票数据字典
            market_condition: 市场环境
            risk_profile: 风险偏好
            current_profit: 当前盈利百分比
        
        Returns:
            止盈建议
        """
        base_profit = self.base_take_profit.get(risk_profile, 15)
        
        # 根据市场环境调整
        market_adjustment = {
            '强势上涨': 1.5,
            '温和上涨': 1.2,
            '震荡整理': 1.0,
            '温和下跌': 0.8,
            '明显下跌': 0.6
        }
        
        multiplier = market_adjustment.get(market_condition, 1.0)
        
        # 根据当前盈利调整
        if current_profit > 10:
            multiplier *= 0.9  # 已有较大盈利，降低止盈目标
        
        adjusted_take_profit = base_profit * multiplier
        
        # 计算具体止盈价格
        current_price = stock_data.get('current_price', 0)
        take_profit_price = current_price * (1 + adjusted_take_profit / 100)
        
        return {
            'take_profit_percent': adjusted_take_profit,
            'take_profit_price': take_profit_price,
            'base_take_profit': base_profit,
            'adjustment_factor': multiplier,
            'reason': self._explain_take_profit_adjustment(market_condition, current_profit)
        }
    
    def adjust_position(self, portfolio: Dict, market_volatility: float, 
                       market_trend: str, risk_profile: str) -> Dict:
        """
        动态调整仓位
        
        Args:
            portfolio: 投资组合字典
            market_volatility: 市场波动率
            market_trend: 市场趋势
            risk_profile: 风险偏好
        
        Returns:
            仓位调整建议
        """
        # 计算当前仓位
        total_investment = sum(alloc.get('investment_amount', 0) for alloc in portfolio.values())
        
        # 根据市场波动率调整
        if market_volatility > 0.05:  # 高波动
            position_multiplier = 0.7
            action = "降低仓位"
        elif market_volatility > 0.03:  # 中等波动
            position_multiplier = 0.9
            action = "适度降低仓位"
        elif market_volatility < 0.01:  # 低波动
            position_multiplier = 1.1
            action = "可适度增加仓位"
        else:
            position_multiplier = 1.0
            action = "保持当前仓位"
        
        # 根据市场趋势调整
        trend_adjustment = {
            '强势上涨': 1.1,
            '温和上涨': 1.05,
            '震荡整理': 1.0,
            '温和下跌': 0.95,
            '明显下跌': 0.85
        }
        
        position_multiplier *= trend_adjustment.get(market_trend, 1.0)
        
        # 根据风险偏好调整
        risk_adjustment = {
            '激进型': 1.1,
            '稳健型': 1.0,
            '保守型': 0.9
        }
        
        position_multiplier *= risk_adjustment.get(risk_profile, 1.0)
        
        # 限制范围
        position_multiplier = max(0.5, min(1.3, position_multiplier))
        
        # 生成调整建议
        adjusted_portfolio = {}
        for name, alloc in portfolio.items():
            adjusted_portfolio[name] = {
                'original_weight': alloc.get('weight_percent', 0),
                'adjusted_weight': alloc.get('weight_percent', 0) * position_multiplier,
                'original_amount': alloc.get('investment_amount', 0),
                'adjusted_amount': alloc.get('investment_amount', 0) * position_multiplier
            }
        
        return {
            'position_multiplier': position_multiplier,
            'action': action,
            'adjusted_portfolio': adjusted_portfolio,
            'total_adjustment': (position_multiplier - 1) * 100,
            'reason': self._explain_position_adjustment(market_volatility, market_trend)
        }
    
    def generate_risk_alerts(self, stock_data: Dict, portfolio: Dict, 
                            market_analysis: Dict) -> List[Dict]:
        """
        生成风险预警
        
        Args:
            stock_data: 股票数据字典
            portfolio: 投资组合字典
            market_analysis: 市场分析结果
        
        Returns:
            风险预警列表
        """
        alerts = []
        
        # 检查个股风险
        for name, data in stock_data.items():
            # 检查涨跌幅
            change_percent = data.get('change_percent', 0)
            if abs(change_percent) > 5:
                alerts.append({
                    'type': '个股波动预警',
                    'stock': name,
                    'level': '高' if abs(change_percent) > 8 else '中',
                    'message': f"{name}涨跌幅{change_percent:+.2f}%，波动较大",
                    'suggestion': "关注风险，考虑调整仓位" if change_percent < 0 else "注意回调风险"
                })
            
            # 检查波动率
            volatility = self._calculate_volatility(data)
            if volatility > 6:
                alerts.append({
                    'type': '波动率预警',
                    'stock': name,
                    'level': '高',
                    'message': f"{name}波动率{volatility:.2f}%，风险较高",
                    'suggestion': "考虑降低仓位或设置更严格的止损"
                })
        
        # 检查组合集中度
        weights = [alloc.get('weight_percent', 0) for alloc in portfolio.values()]
        max_weight = max(weights) if weights else 0
        if max_weight > 25:
            alerts.append({
                'type': '集中度预警',
                'stock': '投资组合',
                'level': '中',
                'message': f"单只股票最大权重{max_weight:.1f}%，集中度较高",
                'suggestion': "考虑分散投资，降低单一股票风险"
            })
        
        # 检查市场风险
        market_trend = market_analysis.get('market_sentiment', {}).get('market_trend', '')
        if market_trend in ['明显下跌', '温和下跌']:
            alerts.append({
                'type': '市场风险预警',
                'stock': '整体市场',
                'level': '高' if market_trend == '明显下跌' else '中',
                'message': f"市场趋势为{market_trend}，系统性风险上升",
                'suggestion': "考虑降低整体仓位，增加防御性配置"
            })
        
        return alerts
    
    def _calculate_volatility(self, stock_data: Dict) -> float:
        """计算波动率"""
        if stock_data.get('open_price', 0) > 0:
            return abs(stock_data.get('high_price', 0) - stock_data.get('low_price', 0)) / stock_data.get('open_price', 1) * 100
        return 0
    
    def _explain_stop_loss_adjustment(self, market_condition: str, volatility: float, 
                                      holding_days: int) -> str:
        """解释止损调整原因"""
        reasons = []
        
        if market_condition in ['强势上涨', '温和上涨']:
            reasons.append("市场上涨趋势中放宽止损空间")
        elif market_condition in ['明显下跌', '温和下跌']:
            reasons.append("市场下跌趋势中收紧止损保护")
        
        if volatility > 5:
            reasons.append("个股波动率较高，适当放宽止损")
        elif volatility < 2:
            reasons.append("个股波动率较低，可收紧止损")
        
        if holding_days > 30:
            reasons.append("长期持有，逐步收紧止损锁定利润")
        
        return "；".join(reasons) if reasons else "维持基础止损设置"
    
    def _explain_take_profit_adjustment(self, market_condition: str, current_profit: float) -> str:
        """解释止盈调整原因"""
        reasons = []
        
        if market_condition in ['强势上涨']:
            reasons.append("市场强势上涨，提高止盈目标")
        elif market_condition in ['明显下跌']:
            reasons.append("市场下跌风险，降低止盈目标及时获利")
        
        if current_profit > 10:
            reasons.append("已有较大盈利，适度降低止盈目标锁定收益")
        
        return "；".join(reasons) if reasons else "维持基础止盈设置"
    
    def _explain_position_adjustment(self, market_volatility: float, market_trend: str) -> str:
        """解释仓位调整原因"""
        reasons = []
        
        if market_volatility > 0.05:
            reasons.append("市场波动率较高，降低仓位控制风险")
        elif market_volatility < 0.01:
            reasons.append("市场波动率较低，可适度增加仓位")
        
        if market_trend in ['强势上涨', '温和上涨']:
            reasons.append("市场上涨趋势，可适度增加仓位")
        elif market_trend in ['明显下跌', '温和下跌']:
            reasons.append("市场下跌趋势，降低仓位规避风险")
        
        return "；".join(reasons) if reasons else "维持当前仓位"


class TimingStrategy:
    """智能择时策略"""
    
    def __init__(self):
        """初始化择时策略"""
        pass
    
    def analyze_timing(self, stock_data: Dict, market_analysis: Dict, 
                      risk_profile: str) -> Dict:
        """
        综合择时分析
        
        Args:
            stock_data: 股票数据字典
            market_analysis: 市场分析结果
            risk_profile: 风险偏好
        
        Returns:
            择时分析结果
        """
        # 趋势跟踪择时
        trend_timing = self._trend_following_timing(stock_data, market_analysis)
        
        # 均值回归择时
        mean_reversion_timing = self._mean_reversion_timing(stock_data)
        
        # 市场情绪择时
        sentiment_timing = self._sentiment_timing(market_analysis)
        
        # 时间择时
        time_timing = self._time_based_timing()
        
        # 综合判断
        combined_signal = self._combine_signals(
            trend_timing, mean_reversion_timing, sentiment_timing, time_timing, risk_profile
        )
        
        return {
            'trend_timing': trend_timing,
            'mean_reversion_timing': mean_reversion_timing,
            'sentiment_timing': sentiment_timing,
            'time_timing': time_timing,
            'combined_signal': combined_signal,
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _trend_following_timing(self, stock_data: Dict, market_analysis: Dict) -> Dict:
        """趋势跟踪择时"""
        signals = []
        
        # 分析市场趋势
        market_trend = market_analysis.get('market_sentiment', {}).get('market_trend', '震荡整理')
        
        # 分析个股趋势
        for name, data in stock_data.items():
            change_percent = data.get('change_percent', 0)
            
            if change_percent > 2:
                signal = "强势上涨趋势，持有或轻仓追涨"
                action = "持有/轻仓买入"
            elif change_percent > 0.5:
                signal = "温和上涨趋势，可考虑建仓"
                action = "建仓/持有"
            elif change_percent > -0.5:
                signal = "震荡整理，观望为主"
                action = "观望"
            elif change_percent > -2:
                signal = "温和下跌趋势，谨慎操作"
                action = "减仓/观望"
            else:
                signal = "强势下跌趋势，规避风险"
                action = "卖出/观望"
            
            signals.append({
                'stock': name,
                'trend': '上涨' if change_percent > 0.5 else '下跌' if change_percent < -0.5 else '震荡',
                'signal': signal,
                'action': action,
                'confidence': '高' if abs(change_percent) > 2 else '中'
            })
        
        # 综合市场趋势
        if market_trend in ['强势上涨', '温和上涨']:
            market_signal = "市场上涨趋势，可积极参与"
            market_action = "买入/持有"
        elif market_trend in ['明显下跌', '温和下跌']:
            market_signal = "市场下跌趋势，谨慎操作"
            market_action = "减仓/观望"
        else:
            market_signal = "市场震荡整理，精选个股"
            market_action = "观望/轻仓"
        
        return {
            'stock_signals': signals,
            'market_signal': market_signal,
            'market_action': market_action,
            'strategy': '趋势跟踪'
        }
    
    def _mean_reversion_timing(self, stock_data: Dict) -> Dict:
        """均值回归择时"""
        signals = []
        
        for name, data in stock_data.items():
            change_percent = data.get('change_percent', 0)
            
            # 计算价格位置
            high = data.get('high_price', 0)
            low = data.get('low_price', 0)
            current = data.get('current_price', 0)
            
            if high > low:
                position = (current - low) / (high - low)
            else:
                position = 0.5
            
            # 判断超买超卖
            if position < 0.2:
                signal = "超卖区域，可能存在反弹机会"
                action = "关注买入机会"
                level = "超卖"
            elif position > 0.8:
                signal = "超买区域，注意回调风险"
                action = "考虑减仓"
                level = "超买"
            else:
                signal = "价格处于正常区间"
                action = "持有/观望"
                level = "正常"
            
            signals.append({
                'stock': name,
                'position': position,
                'level': level,
                'signal': signal,
                'action': action,
                'z_score': (position - 0.5) / 0.29  # 简化Z-score估算
            })
        
        return {
            'stock_signals': signals,
            'strategy': '均值回归'
        }
    
    def _sentiment_timing(self, market_analysis: Dict) -> Dict:
        """市场情绪择时"""
        sentiment = market_analysis.get('market_sentiment', {})
        
        rising_percent = sentiment.get('rising_percent', 50)
        avg_change = sentiment.get('average_change', 0)
        
        # 计算情绪指标
        if rising_percent > 70 and avg_change > 1:
            sentiment_level = "极度乐观"
            signal = "市场情绪极度乐观，注意回调风险"
            action = "谨慎追高，考虑减仓"
        elif rising_percent > 60 and avg_change > 0.5:
            sentiment_level = "乐观"
            signal = "市场情绪乐观，可积极参与"
            action = "买入/持有"
        elif rising_percent < 30 and avg_change < -1:
            sentiment_level = "极度悲观"
            signal = "市场情绪极度悲观，可能存在反弹机会"
            action = "关注低吸机会"
        elif rising_percent < 40 and avg_change < -0.5:
            sentiment_level = "悲观"
            signal = "市场情绪悲观，谨慎操作"
            action = "观望/轻仓"
        else:
            sentiment_level = "中性"
            signal = "市场情绪中性，震荡为主"
            action = "观望"
        
        return {
            'sentiment_level': sentiment_level,
            'rising_percent': rising_percent,
            'avg_change': avg_change,
            'signal': signal,
            'action': action,
            'strategy': '市场情绪'
        }
    
    def _time_based_timing(self) -> Dict:
        """时间择时"""
        now = datetime.now()
        current_time = now.time()
        weekday = now.weekday()
        
        # 判断交易时段
        if time(9, 30) <= current_time < time(10, 0):
            period = "开盘集合竞价"
            signal = "开盘波动大，谨慎操作"
            action = "观望为主"
        elif time(10, 0) <= current_time < time(11, 30):
            period = "上午交易时段"
            signal = "交易活跃期，可积极参与"
            action = "根据信号操作"
        elif time(13, 0) <= current_time < time(14, 30):
            period = "下午交易时段"
            signal = "交易活跃期，可积极参与"
            action = "根据信号操作"
        elif time(14, 30) <= current_time < time(15, 0):
            period = "尾盘交易时段"
            signal = "尾盘波动大，注意收盘价"
            action = "谨慎操作，关注收盘"
        else:
            period = "非交易时段"
            signal = "非交易时间，做好复盘"
            action = "复盘分析，制定计划"
        
        # 周几效应
        if weekday == 0:  # 周一
            week_signal = "周一效应，注意周末消息影响"
        elif weekday == 4:  # 周五
            week_signal = "周五效应，注意周末不确定性"
        else:
            week_signal = "正常交易日"
        
        return {
            'period': period,
            'time_signal': signal,
            'time_action': action,
            'weekday': weekday,
            'week_signal': week_signal,
            'strategy': '时间择时'
        }
    
    def _combine_signals(self, trend: Dict, mean_reversion: Dict, sentiment: Dict, 
                        time_timing: Dict, risk_profile: str) -> Dict:
        """综合信号"""
        # 计算综合评分
        score = 50  # 基础分
        
        # 趋势信号权重
        if '上涨' in trend.get('market_signal', ''):
            score += 15
        elif '下跌' in trend.get('market_signal', ''):
            score -= 15
        
        # 情绪信号权重
        sentiment_level = sentiment.get('sentiment_level', '中性')
        if sentiment_level == '乐观':
            score += 10
        elif sentiment_level == '悲观':
            score -= 10
        elif sentiment_level == '极度乐观':
            score -= 5  # 反向指标
        elif sentiment_level == '极度悲观':
            score += 5  # 反向指标
        
        # 时间信号权重
        if '交易活跃期' in time_timing.get('period', ''):
            score += 5
        elif '非交易时段' in time_timing.get('period', ''):
            score -= 5
        
        # 根据风险偏好调整
        if risk_profile == '激进型':
            score += 5
        elif risk_profile == '保守型':
            score -= 5
        
        # 生成综合建议
        if score >= 70:
            overall_signal = "强烈买入信号"
            action = "积极建仓，把握机会"
        elif score >= 60:
            overall_signal = "买入信号"
            action = "可考虑建仓或加仓"
        elif score >= 40:
            overall_signal = "持有信号"
            action = "持有观望，等待机会"
        elif score >= 30:
            overall_signal = "减仓信号"
            action = "考虑减仓，控制风险"
        else:
            overall_signal = "卖出信号"
            action = "及时止损，规避风险"
        
        return {
            'score': score,
            'signal': overall_signal,
            'action': action,
            'confidence': '高' if abs(score - 50) > 20 else '中',
            'reason': self._explain_combined_signal(trend, sentiment, time_timing)
        }
    
    def _explain_combined_signal(self, trend: Dict, sentiment: Dict, time_timing: Dict) -> str:
        """解释综合信号"""
        reasons = []
        
        if '上涨' in trend.get('market_signal', ''):
            reasons.append("市场趋势向上")
        elif '下跌' in trend.get('market_signal', ''):
            reasons.append("市场趋势向下")
        
        sentiment_level = sentiment.get('sentiment_level', '中性')
        if sentiment_level != '中性':
            reasons.append(f"市场情绪{sentiment_level}")
        
        if '交易活跃期' in time_timing.get('period', ''):
            reasons.append("当前为交易活跃时段")
        
        return "，".join(reasons) if reasons else "市场处于平衡状态"


# 使用示例
if __name__ == "__main__":
    # 测试数据
    test_stock_data = {
        '科创信息': {
            'symbol': '300730.SZ',
            'current_price': 14.69,
            'open_price': 14.67,
            'high_price': 14.99,
            'low_price': 14.65,
            'change_percent': 0.14
        }
    }
    
    test_market_analysis = {
        'market_sentiment': {
            'market_trend': '震荡整理',
            'rising_percent': 62.5,
            'average_change': 0.80
        }
    }
    
    # 动态风险控制
    risk_controller = DynamicRiskController()
    stop_loss = risk_controller.adjust_stop_loss(
        test_stock_data['科创信息'], '震荡整理', '稳健型', 10
    )
    print("止损建议:")
    print(f"止损百分比: {stop_loss['stop_loss_percent']:.2f}%")
    print(f"止损价格: ¥{stop_loss['stop_loss_price']:.2f}")
    print(f"调整原因: {stop_loss['reason']}")
    
    # 智能择时
    timing_strategy = TimingStrategy()
    timing_result = timing_strategy.analyze_timing(
        test_stock_data, test_market_analysis, '稳健型'
    )
    print("\n择时分析:")
    print(f"综合信号: {timing_result['combined_signal']['signal']}")
    print(f"建议操作: {timing_result['combined_signal']['action']}")
