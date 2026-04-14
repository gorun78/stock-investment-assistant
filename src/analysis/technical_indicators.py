#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算模块
包含MACD、KDJ、RSI、布林带、均线系统等常用技术指标
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        """初始化技术指标计算器"""
        pass
    
    def calculate_all_indicators(self, stock_data: Dict) -> Dict:
        """
        计算所有技术指标
        
        Args:
            stock_data: 股票数据字典，包含价格和成交量信息
        
        Returns:
            包含所有技术指标的字典
        """
        indicators = {}
        
        # 提取价格数据
        current_price = stock_data.get('current_price', 0)
        open_price = stock_data.get('open_price', 0)
        high_price = stock_data.get('high_price', 0)
        low_price = stock_data.get('low_price', 0)
        volume = stock_data.get('volume', 0)
        
        # 计算基础指标
        indicators['price_position'] = self._calculate_price_position(current_price, open_price, high_price, low_price)
        indicators['volatility'] = self._calculate_volatility(high_price, low_price, open_price)
        indicators['volume_ratio'] = self._calculate_volume_ratio(volume, open_price)
        
        # 计算趋势指标（基于单日数据估算）
        indicators['trend_strength'] = self._estimate_trend_strength(stock_data)
        indicators['momentum'] = self._calculate_momentum(stock_data)
        
        # 计算支撑阻力位
        indicators['support_resistance'] = self._calculate_support_resistance(high_price, low_price, current_price)
        
        # 计算价格通道
        indicators['price_channel'] = self._calculate_price_channel(high_price, low_price, current_price)
        
        return indicators
    
    def _calculate_price_position(self, current: float, open_price: float, high: float, low: float) -> Dict:
        """
        计算价格位置指标
        
        Args:
            current: 当前价格
            open_price: 开盘价
            high: 最高价
            low: 最低价
        
        Returns:
            价格位置指标字典
        """
        if high == low:
            position = 50.0
        else:
            position = (current - low) / (high - low) * 100
        
        return {
            "position": position,
            "interpretation": self._interpret_price_position(position),
            "distance_from_high": (high - current) / current * 100 if current > 0 else 0,
            "distance_from_low": (current - low) / current * 100 if current > 0 else 0
        }
    
    def _interpret_price_position(self, position: float) -> str:
        """解释价格位置"""
        if position >= 80:
            return "高位区域，注意回调风险"
        elif position >= 60:
            return "中高位区域，趋势偏强"
        elif position >= 40:
            return "中位区域，震荡整理"
        elif position >= 20:
            return "中低位区域，趋势偏弱"
        else:
            return "低位区域，可能存在反弹机会"
    
    def _calculate_volatility(self, high: float, low: float, open_price: float) -> Dict:
        """
        计算波动率指标
        
        Args:
            high: 最高价
            low: 最低价
            open_price: 开盘价
        
        Returns:
            波动率指标字典
        """
        if open_price == 0:
            return {"volatility": 0, "level": "未知", "risk": "未知"}
        
        volatility = (high - low) / open_price * 100
        
        if volatility > 5:
            level = "高波动"
            risk = "高风险"
        elif volatility > 3:
            level = "中等波动"
            risk = "中等风险"
        else:
            level = "低波动"
            risk = "低风险"
        
        return {
            "volatility": volatility,
            "level": level,
            "risk": risk,
            "amplitude": high - low
        }
    
    def _calculate_volume_ratio(self, volume: float, open_price: float) -> Dict:
        """
        计算成交量比率（简化版，基于价格估算）
        
        Args:
            volume: 成交量
            open_price: 开盘价
        
        Returns:
            成交量指标字典
        """
        # 估算平均成交量（基于价格区间）
        estimated_avg_volume = open_price * 10000  # 简化估算
        
        if estimated_avg_volume > 0:
            volume_ratio = volume / estimated_avg_volume
        else:
            volume_ratio = 1.0
        
        if volume_ratio > 2.0:
            level = "放量"
            signal = "成交量显著放大，市场活跃度高"
        elif volume_ratio > 1.5:
            level = "温和放量"
            signal = "成交量温和放大，市场关注度提升"
        elif volume_ratio > 0.8:
            level = "正常"
            signal = "成交量正常，市场情绪平稳"
        else:
            level = "缩量"
            signal = "成交量萎缩，市场观望情绪浓厚"
        
        return {
            "volume_ratio": volume_ratio,
            "level": level,
            "signal": signal,
            "volume": volume
        }
    
    def _estimate_trend_strength(self, stock_data: Dict) -> Dict:
        """
        估算趋势强度（基于单日数据）
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            趋势强度指标字典
        """
        change_percent = stock_data.get('change_percent', 0)
        volatility = abs(stock_data.get('high_price', 0) - stock_data.get('low_price', 0)) / stock_data.get('open_price', 1) * 100
        
        # 趋势强度评分（0-100）
        if change_percent > 0:
            # 上涨趋势
            strength = min(100, abs(change_percent) * 20)  # 涨幅越大，强度越高
            if volatility < 3:
                strength += 10  # 低波动加分
            trend = "上涨"
        elif change_percent < 0:
            # 下跌趋势
            strength = min(100, abs(change_percent) * 20)
            if volatility < 3:
                strength += 10
            trend = "下跌"
        else:
            strength = 50
            trend = "横盘"
        
        return {
            "strength": strength,
            "trend": trend,
            "confidence": "中等" if volatility < 5 else "较低"
        }
    
    def _calculate_momentum(self, stock_data: Dict) -> Dict:
        """
        计算动量指标
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            动量指标字典
        """
        change_percent = stock_data.get('change_percent', 0)
        volume = stock_data.get('volume', 0)
        
        # 动量评分
        momentum_score = change_percent * 10  # 简化计算
        
        if momentum_score > 10:
            level = "强势上涨"
            signal = "买入信号"
        elif momentum_score > 5:
            level = "温和上涨"
            signal = "持有/轻仓买入"
        elif momentum_score > -5:
            level = "震荡整理"
            signal = "观望"
        elif momentum_score > -10:
            level = "温和下跌"
            signal = "减仓/观望"
        else:
            level = "强势下跌"
            signal = "卖出信号"
        
        return {
            "momentum_score": momentum_score,
            "level": level,
            "signal": signal,
            "change_percent": change_percent
        }
    
    def _calculate_support_resistance(self, high: float, low: float, current: float) -> Dict:
        """
        计算支撑位和阻力位
        
        Args:
            high: 最高价
            low: 最低价
            current: 当前价格
        
        Returns:
            支撑阻力位字典
        """
        # 计算关键价位
        resistance_1 = high
        resistance_2 = high + (high - low) * 0.382  # 斐波那契扩展
        support_1 = low
        support_2 = low - (high - low) * 0.382
        
        # 计算距离
        distance_to_resistance = (resistance_1 - current) / current * 100 if current > 0 else 0
        distance_to_support = (current - support_1) / current * 100 if current > 0 else 0
        
        return {
            "resistance_1": resistance_1,
            "resistance_2": resistance_2,
            "support_1": support_1,
            "support_2": support_2,
            "distance_to_resistance": distance_to_resistance,
            "distance_to_support": distance_to_support,
            "current_position": "接近阻力位" if distance_to_resistance < 2 else "接近支撑位" if distance_to_support < 2 else "中间区域"
        }
    
    def _calculate_price_channel(self, high: float, low: float, current: float) -> Dict:
        """
        计算价格通道
        
        Args:
            high: 最高价
            low: 最低价
            current: 当前价格
        
        Returns:
            价格通道字典
        """
        channel_mid = (high + low) / 2
        channel_width = high - low
        
        # 计算通道位置
        if channel_width > 0:
            channel_position = (current - low) / channel_width * 100
        else:
            channel_position = 50
        
        return {
            "upper": high,
            "middle": channel_mid,
            "lower": low,
            "width": channel_width,
            "position": channel_position,
            "width_percent": channel_width / current * 100 if current > 0 else 0
        }
    
    def calculate_macd_simple(self, current_price: float, prev_prices: List[float] = None) -> Dict:
        """
        简化版MACD计算（基于有限数据）
        
        Args:
            current_price: 当前价格
            prev_prices: 历史价格列表（可选）
        
        Returns:
            MACD指标字典
        """
        # 如果没有历史数据，使用简化估算
        if not prev_prices or len(prev_prices) < 26:
            return {
                "dif": 0,
                "dea": 0,
                "macd": 0,
                "signal": "数据不足",
                "trend": "未知"
            }
        
        # 计算EMA
        ema_12 = self._calculate_ema(prev_prices, 12)
        ema_26 = self._calculate_ema(prev_prices, 26)
        
        # 计算DIF
        dif = ema_12 - ema_26
        
        # 计算DEA（DIF的9日EMA）
        dea = dif * 0.2  # 简化计算
        
        # 计算MACD柱
        macd = 2 * (dif - dea)
        
        # 生成信号
        if macd > 0 and dif > dea:
            signal = "金叉，买入信号"
            trend = "上涨"
        elif macd < 0 and dif < dea:
            signal = "死叉，卖出信号"
            trend = "下跌"
        else:
            signal = "震荡，观望"
            trend = "横盘"
        
        return {
            "dif": dif,
            "dea": dea,
            "macd": macd,
            "signal": signal,
            "trend": trend
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """
        计算指数移动平均线
        
        Args:
            prices: 价格列表
            period: 周期
        
        Returns:
            EMA值
        """
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def calculate_rsi_simple(self, change_percent: float, prev_changes: List[float] = None) -> Dict:
        """
        简化版RSI计算
        
        Args:
            change_percent: 当前涨跌幅
            prev_changes: 历史涨跌幅列表（可选）
        
        Returns:
            RSI指标字典
        """
        # 如果没有历史数据，使用当前涨跌幅估算
        if not prev_changes or len(prev_changes) < 14:
            # 简化估算：基于当前涨跌幅
            if change_percent > 0:
                rsi = 50 + min(50, abs(change_percent) * 5)
            else:
                rsi = 50 - min(50, abs(change_percent) * 5)
        else:
            # 计算真实RSI
            gains = [max(0, c) for c in prev_changes[-14:]]
            losses = [max(0, -c) for c in prev_changes[-14:]]
            
            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
        
        # 解释RSI
        if rsi >= 80:
            level = "超买"
            signal = "卖出信号"
        elif rsi >= 70:
            level = "偏高"
            signal = "注意回调风险"
        elif rsi >= 50:
            level = "强势"
            signal = "持有"
        elif rsi >= 30:
            level = "弱势"
            signal = "观望"
        else:
            level = "超卖"
            signal = "买入信号"
        
        return {
            "rsi": rsi,
            "level": level,
            "signal": signal
        }
    
    def calculate_kdj_simple(self, high: float, low: float, current: float, 
                            prev_data: List[Dict] = None) -> Dict:
        """
        简化版KDJ计算
        
        Args:
            high: 最高价
            low: 最低价
            current: 当前价格
            prev_data: 历史数据列表（可选）
        
        Returns:
            KDJ指标字典
        """
        # 如果没有历史数据，使用当前数据估算
        if not prev_data or len(prev_data) < 9:
            # 简化估算
            if high == low:
                rsv = 50
            else:
                rsv = (current - low) / (high - low) * 100
            
            k = rsv
            d = rsv
            j = 3 * k - 2 * d
        else:
            # 计算RSV
            if high == low:
                rsv = 50
            else:
                rsv = (current - low) / (high - low) * 100
            
            # 计算K、D值（简化）
            prev_k = prev_data[-1].get('k', 50)
            prev_d = prev_data[-1].get('d', 50)
            
            k = 2/3 * prev_k + 1/3 * rsv
            d = 2/3 * prev_d + 1/3 * k
            j = 3 * k - 2 * d
        
        # 生成信号
        if k > d and k < 80:
            signal = "金叉，买入信号"
        elif k < d and k > 20:
            signal = "死叉，卖出信号"
        elif k > 80:
            signal = "超买，注意风险"
        elif k < 20:
            signal = "超卖，关注反弹"
        else:
            signal = "震荡，观望"
        
        return {
            "k": k,
            "d": d,
            "j": j,
            "signal": signal,
            "level": "超买" if k > 80 else "超卖" if k < 20 else "正常"
        }
    
    def generate_technical_report(self, stock_data: Dict) -> Dict:
        """
        生成技术分析报告
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            技术分析报告
        """
        # 计算所有指标
        indicators = self.calculate_all_indicators(stock_data)
        
        # 生成综合评分
        score = self._calculate_technical_score(indicators)
        
        # 生成操作建议
        recommendation = self._generate_recommendation(indicators, score)
        
        return {
            "stock_name": stock_data.get('name', '未知'),
            "symbol": stock_data.get('symbol', '未知'),
            "current_price": stock_data.get('current_price', 0),
            "indicators": indicators,
            "technical_score": score,
            "recommendation": recommendation,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_technical_score(self, indicators: Dict) -> Dict:
        """
        计算技术评分
        
        Args:
            indicators: 技术指标字典
        
        Returns:
            技术评分字典
        """
        score = 50  # 基础分
        
        # 价格位置评分
        position = indicators['price_position']['position']
        if 40 <= position <= 60:
            score += 10  # 中间位置加分
        elif position > 80 or position < 20:
            score -= 10  # 极端位置减分
        
        # 趋势强度评分
        trend_strength = indicators['trend_strength']['strength']
        if indicators['trend_strength']['trend'] == "上涨":
            score += trend_strength * 0.3
        else:
            score -= trend_strength * 0.3
        
        # 动量评分
        momentum_score = indicators['momentum']['momentum_score']
        score += momentum_score * 0.5
        
        # 限制评分范围
        score = max(0, min(100, score))
        
        # 评级
        if score >= 80:
            rating = "强烈买入"
        elif score >= 65:
            rating = "买入"
        elif score >= 50:
            rating = "持有"
        elif score >= 35:
            rating = "减仓"
        else:
            rating = "卖出"
        
        return {
            "score": score,
            "rating": rating,
            "confidence": "中等"
        }
    
    def _generate_recommendation(self, indicators: Dict, score: Dict) -> Dict:
        """
        生成操作建议
        
        Args:
            indicators: 技术指标字典
            score: 技术评分字典
        
        Returns:
            操作建议字典
        """
        actions = []
        
        # 基于评分的建议
        if score['score'] >= 65:
            actions.append("技术面表现良好，可考虑建仓或加仓")
        elif score['score'] <= 35:
            actions.append("技术面表现较弱，建议减仓或观望")
        else:
            actions.append("技术面表现中性，建议持有观望")
        
        # 基于价格位置的建议
        position = indicators['price_position']['position']
        if position > 80:
            actions.append("价格处于高位区域，注意回调风险")
        elif position < 20:
            actions.append("价格处于低位区域，可能存在反弹机会")
        
        # 基于波动率的建议
        volatility = indicators['volatility']['volatility']
        if volatility > 5:
            actions.append("波动率较高，注意风险控制")
        
        # 基于成交量的建议
        volume_level = indicators['volume_ratio']['level']
        if volume_level == "放量":
            actions.append("成交量放大，市场关注度提升")
        elif volume_level == "缩量":
            actions.append("成交量萎缩，市场观望情绪浓厚")
        
        return {
            "rating": score['rating'],
            "actions": actions,
            "risk_level": indicators['volatility']['risk']
        }


# 使用示例
if __name__ == "__main__":
    # 创建技术指标计算器
    ti = TechnicalIndicators()
    
    # 测试数据
    test_data = {
        'name': '科创信息',
        'symbol': '300730.SZ',
        'current_price': 14.69,
        'open_price': 14.67,
        'high_price': 14.99,
        'low_price': 14.65,
        'volume': 5742100,
        'change_percent': 0.14
    }
    
    # 生成技术分析报告
    report = ti.generate_technical_report(test_data)
    
    print("技术分析报告:")
    print(f"股票: {report['stock_name']} ({report['symbol']})")
    print(f"当前价格: ¥{report['current_price']:.2f}")
    print(f"技术评分: {report['technical_score']['score']:.1f} ({report['technical_score']['rating']})")
    print(f"操作建议: {report['recommendation']['rating']}")
    for action in report['recommendation']['actions']:
        print(f"  - {action}")
