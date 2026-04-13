#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级分析模块
包含板块深度分析、风险评估、资金流向分析等功能
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict


class SectorAnalyzer:
    """板块分析器"""
    
    def __init__(self):
        """初始化板块分析器"""
        self.sector_history = {}
    
    def analyze_sectors(self, stock_data: Dict) -> Dict:
        """
        分析板块表现
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            板块分析结果
        """
        # 按板块分组
        sectors = defaultdict(list)
        for name, data in stock_data.items():
            sector = data.get('sector', '未知')
            sectors[sector].append({
                'name': name,
                'change_percent': data.get('change_percent', 0),
                'volume': data.get('volume', 0),
                'current_price': data.get('current_price', 0),
                'volatility': abs(data.get('high_price', 0) - data.get('low_price', 0)) / data.get('open_price', 1) * 100 if data.get('open_price', 0) > 0 else 0
            })
        
        # 计算板块指标
        sector_analysis = {}
        for sector, stocks in sectors.items():
            changes = [s['change_percent'] for s in stocks]
            volumes = [s['volume'] for s in stocks]
            volatilities = [s['volatility'] for s in stocks]
            
            sector_analysis[sector] = {
                'stock_count': len(stocks),
                'avg_change': np.mean(changes),
                'max_change': max(changes),
                'min_change': min(changes),
                'total_volume': sum(volumes),
                'avg_volatility': np.mean(volatilities),
                'stocks': [s['name'] for s in stocks],
                'performance_score': self._calculate_sector_score(np.mean(changes), np.mean(volatilities)),
                'strength': self._assess_sector_strength(np.mean(changes), len(stocks))
            }
        
        # 板块排名
        ranked_sectors = self._rank_sectors(sector_analysis)
        
        # 板块相关性分析
        correlation_matrix = self._analyze_sector_correlation(sectors)
        
        # 板块轮动预测
        rotation_prediction = self._predict_sector_rotation(sector_analysis)
        
        return {
            'sector_analysis': sector_analysis,
            'sector_ranking': ranked_sectors,
            'correlation_matrix': correlation_matrix,
            'rotation_prediction': rotation_prediction,
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_sector_score(self, avg_change: float, avg_volatility: float) -> float:
        """计算板块评分"""
        # 基于涨跌幅和波动率计算评分
        score = 50 + avg_change * 5
        
        # 波动率调整
        if avg_volatility > 5:
            score -= 10
        elif avg_volatility < 2:
            score += 5
        
        return max(0, min(100, score))
    
    def _assess_sector_strength(self, avg_change: float, stock_count: int) -> str:
        """评估板块强度"""
        if avg_change > 2:
            return "强势板块"
        elif avg_change > 0.5:
            return "偏强板块"
        elif avg_change > -0.5:
            return "中性板块"
        elif avg_change > -2:
            return "偏弱板块"
        else:
            return "弱势板块"
    
    def _rank_sectors(self, sector_analysis: Dict) -> List[Dict]:
        """板块排名"""
        ranked = []
        for sector, data in sector_analysis.items():
            ranked.append({
                'sector': sector,
                'avg_change': data['avg_change'],
                'performance_score': data['performance_score'],
                'strength': data['strength'],
                'stock_count': data['stock_count']
            })
        
        # 按平均涨跌幅排序
        ranked.sort(key=lambda x: x['avg_change'], reverse=True)
        
        return ranked
    
    def _analyze_sector_correlation(self, sectors: Dict) -> Dict:
        """分析板块相关性"""
        # 简化版相关性分析
        sector_changes = {}
        for sector, stocks in sectors.items():
            changes = [s['change_percent'] for s in stocks]
            sector_changes[sector] = np.mean(changes)
        
        # 计算相关性（简化版）
        correlation = {}
        sectors_list = list(sector_changes.keys())
        
        for i, sector1 in enumerate(sectors_list):
            correlation[sector1] = {}
            for j, sector2 in enumerate(sectors_list):
                if i == j:
                    correlation[sector1][sector2] = 1.0
                else:
                    # 简化计算：基于涨跌幅差异
                    diff = abs(sector_changes[sector1] - sector_changes[sector2])
                    correlation[sector1][sector2] = max(0, 1 - diff / 10)
        
        return {
            'matrix': correlation,
            'interpretation': self._interpret_correlation(correlation, sectors_list)
        }
    
    def _interpret_correlation(self, correlation: Dict, sectors: List[str]) -> List[str]:
        """解释相关性"""
        interpretations = []
        
        for i, sector1 in enumerate(sectors):
            for j, sector2 in enumerate(sectors):
                if i < j:
                    corr_value = correlation[sector1][sector2]
                    if corr_value > 0.8:
                        interpretations.append(f"{sector1}与{sector2}高度正相关，走势趋同")
                    elif corr_value < 0.3:
                        interpretations.append(f"{sector1}与{sector2}相关性较低，可分散风险")
        
        return interpretations[:5]  # 返回前5条
    
    def _predict_sector_rotation(self, sector_analysis: Dict) -> Dict:
        """预测板块轮动"""
        # 获取板块表现
        performances = []
        for sector, data in sector_analysis.items():
            performances.append({
                'sector': sector,
                'avg_change': data['avg_change'],
                'score': data['performance_score']
            })
        
        # 按表现排序
        performances.sort(key=lambda x: x['avg_change'], reverse=True)
        
        # 识别强势和弱势板块
        strong_sectors = [p for p in performances if p['avg_change'] > 0.5]
        weak_sectors = [p for p in performances if p['avg_change'] < -0.5]
        
        # 预测轮动
        predictions = []
        
        # 强势板块可能回调
        for sector in strong_sectors[:2]:
            predictions.append({
                'sector': sector['sector'],
                'current_status': '强势',
                'prediction': '可能面临短期回调',
                'action': '逢高减仓'
            })
        
        # 弱势板块可能反弹
        for sector in weak_sectors[:2]:
            predictions.append({
                'sector': sector['sector'],
                'current_status': '弱势',
                'prediction': '可能迎来反弹机会',
                'action': '关注低吸机会'
            })
        
        return {
            'predictions': predictions,
            'strong_sectors': [s['sector'] for s in strong_sectors],
            'weak_sectors': [s['sector'] for s in weak_sectors],
            'rotation_probability': self._calculate_rotation_probability(performances)
        }
    
    def _calculate_rotation_probability(self, performances: List[Dict]) -> float:
        """计算板块轮动概率"""
        if len(performances) < 2:
            return 0.5
        
        # 计算表现差异
        changes = [p['avg_change'] for p in performances]
        variance = np.var(changes)
        
        # 方差越大，轮动概率越高
        probability = min(0.9, 0.3 + variance * 0.1)
        
        return probability


class RiskAnalyzer:
    """风险分析器"""
    
    def __init__(self):
        """初始化风险分析器"""
        pass
    
    def analyze_portfolio_risk(self, stock_data: Dict, portfolio: Dict) -> Dict:
        """
        分析投资组合风险
        
        Args:
            stock_data: 股票数据字典
            portfolio: 投资组合字典
        
        Returns:
            风险分析结果
        """
        # 计算组合波动率
        portfolio_volatility = self._calculate_portfolio_volatility(stock_data, portfolio)
        
        # 计算VaR
        var = self._calculate_var(stock_data, portfolio)
        
        # 执行压力测试
        stress_test = self._perform_stress_test(stock_data, portfolio)
        
        # 计算风险指标
        risk_metrics = self._calculate_risk_metrics(stock_data, portfolio)
        
        return {
            'portfolio_volatility': portfolio_volatility,
            'var': var,
            'stress_test': stress_test,
            'risk_metrics': risk_metrics,
            'risk_level': self._assess_risk_level(portfolio_volatility, var['var_95']),
            'recommendations': self._generate_risk_recommendations(portfolio_volatility, var, stress_test),
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_portfolio_volatility(self, stock_data: Dict, portfolio: Dict) -> Dict:
        """计算组合波动率"""
        total_volatility = 0
        total_weight = 0
        
        for name, allocation in portfolio.items():
            if name in stock_data:
                data = stock_data[name]
                weight = allocation.get('weight_percent', 0) / 100
                
                # 计算个股波动率
                if data.get('open_price', 0) > 0:
                    stock_volatility = abs(data.get('high_price', 0) - data.get('low_price', 0)) / data.get('open_price', 1) * 100
                else:
                    stock_volatility = 0
                
                total_volatility += stock_volatility * weight
                total_weight += weight
        
        avg_volatility = total_volatility / total_weight if total_weight > 0 else 0
        
        return {
            'portfolio_volatility': avg_volatility,
            'level': '高' if avg_volatility > 5 else '中' if avg_volatility > 3 else '低',
            'interpretation': f"组合平均波动率{avg_volatility:.2f}%，属于{'高' if avg_volatility > 5 else '中' if avg_volatility > 3 else '低'}风险水平"
        }
    
    def _calculate_var(self, stock_data: Dict, portfolio: Dict) -> Dict:
        """计算VaR（风险价值）"""
        # 简化版VaR计算
        total_value = sum(alloc.get('investment_amount', 0) for alloc in portfolio.values())
        
        # 计算组合日收益率分布
        portfolio_changes = []
        for name, allocation in portfolio.items():
            if name in stock_data:
                weight = allocation.get('weight_percent', 0) / 100
                change = stock_data[name].get('change_percent', 0)
                portfolio_changes.append(change * weight)
        
        # 计算VaR
        if portfolio_changes:
            portfolio_return = sum(portfolio_changes)
            portfolio_std = np.std(portfolio_changes) if len(portfolio_changes) > 1 else abs(portfolio_return)
            
            # 95%置信度VaR
            var_95 = total_value * (abs(portfolio_return) + 1.65 * portfolio_std) / 100
            
            # 99%置信度VaR
            var_99 = total_value * (abs(portfolio_return) + 2.33 * portfolio_std) / 100
        else:
            var_95 = 0
            var_99 = 0
        
        return {
            'var_95': var_95,
            'var_99': var_99,
            'var_95_percent': var_95 / total_value * 100 if total_value > 0 else 0,
            'var_99_percent': var_99 / total_value * 100 if total_value > 0 else 0,
            'interpretation': f"95%置信度下，单日最大可能损失¥{var_95:.2f}（{var_95/total_value*100:.2f}%）"
        }
    
    def _perform_stress_test(self, stock_data: Dict, portfolio: Dict) -> Dict:
        """执行压力测试"""
        total_value = sum(alloc.get('investment_amount', 0) for alloc in portfolio.values())
        
        # 定义压力情景
        scenarios = {
            '市场大跌': {'market_change': -5.0, 'volatility_multiplier': 2.0},
            '市场大涨': {'market_change': 5.0, 'volatility_multiplier': 1.5},
            '高波动': {'market_change': 0.0, 'volatility_multiplier': 3.0},
            '板块轮动': {'market_change': 0.0, 'volatility_multiplier': 1.5}
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            loss = 0
            for name, allocation in portfolio.items():
                if name in stock_data:
                    amount = allocation.get('investment_amount', 0)
                    base_change = stock_data[name].get('change_percent', 0)
                    
                    # 应用压力情景
                    stressed_change = base_change + params['market_change']
                    stressed_change *= params['volatility_multiplier']
                    
                    loss += amount * stressed_change / 100
            
            results[scenario_name] = {
                'loss': abs(loss),
                'loss_percent': abs(loss) / total_value * 100 if total_value > 0 else 0,
                'impact': '严重' if abs(loss) / total_value > 0.1 else '中等' if abs(loss) / total_value > 0.05 else '轻微'
            }
        
        return {
            'scenarios': results,
            'worst_case': max(results.items(), key=lambda x: x[1]['loss']),
            'best_case': min(results.items(), key=lambda x: x[1]['loss'])
        }
    
    def _calculate_risk_metrics(self, stock_data: Dict, portfolio: Dict) -> Dict:
        """计算风险指标"""
        # 计算集中度风险
        weights = [alloc.get('weight_percent', 0) for alloc in portfolio.values()]
        max_weight = max(weights) if weights else 0
        herfindahl_index = sum(w**2 for w in weights) / 10000  # 赫芬达尔指数
        
        # 计算板块集中度
        sector_weights = defaultdict(float)
        for name, allocation in portfolio.items():
            if name in stock_data:
                sector = stock_data[name].get('sector', '未知')
                sector_weights[sector] += allocation.get('weight_percent', 0)
        
        max_sector_weight = max(sector_weights.values()) if sector_weights else 0
        
        return {
            'max_single_stock_weight': max_weight,
            'herfindahl_index': herfindahl_index,
            'concentration_level': '高' if herfindahl_index > 0.25 else '中' if herfindahl_index > 0.15 else '低',
            'max_sector_weight': max_sector_weight,
            'sector_concentration': '高' if max_sector_weight > 40 else '中' if max_sector_weight > 25 else '低',
            'diversification_score': 100 - herfindahl_index * 100
        }
    
    def _assess_risk_level(self, volatility: Dict, var_95: float) -> str:
        """评估风险等级"""
        vol_level = volatility.get('portfolio_volatility', 0)
        
        if vol_level > 5 or var_95 > 10000:
            return "高风险"
        elif vol_level > 3 or var_95 > 5000:
            return "中等风险"
        else:
            return "低风险"
    
    def _generate_risk_recommendations(self, volatility: Dict, var: Dict, stress_test: Dict) -> List[str]:
        """生成风险建议"""
        recommendations = []
        
        # 基于波动率的建议
        vol_level = volatility.get('portfolio_volatility', 0)
        if vol_level > 5:
            recommendations.append("组合波动率较高，建议增加低波动股票配置")
        
        # 基于VaR的建议
        var_percent = var.get('var_95_percent', 0)
        if var_percent > 5:
            recommendations.append(f"单日最大可能损失{var_percent:.2f}%，建议设置止损保护")
        
        # 基于压力测试的建议
        worst_case = stress_test.get('worst_case', ())
        if worst_case:
            scenario_name, scenario_data = worst_case
            if scenario_data['loss_percent'] > 10:
                recommendations.append(f"在{scenario_name}情景下可能损失{scenario_data['loss_percent']:.2f}%，建议对冲风险")
        
        if not recommendations:
            recommendations.append("组合风险水平适中，继续保持当前配置")
        
        return recommendations


class CapitalFlowAnalyzer:
    """资金流向分析器"""
    
    def __init__(self):
        """初始化资金流向分析器"""
        pass
    
    def analyze_capital_flow(self, stock_data: Dict) -> Dict:
        """
        分析资金流向
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            资金流向分析结果
        """
        # 计算个股资金流向
        stock_flows = self._calculate_stock_flows(stock_data)
        
        # 计算板块资金流向
        sector_flows = self._calculate_sector_flows(stock_data, stock_flows)
        
        # 识别资金热点
        hotspots = self._identify_capital_hotspots(stock_flows)
        
        return {
            'stock_flows': stock_flows,
            'sector_flows': sector_flows,
            'hotspots': hotspots,
            'flow_trend': self._analyze_flow_trend(stock_flows),
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _calculate_stock_flows(self, stock_data: Dict) -> Dict:
        """计算个股资金流向"""
        flows = {}
        
        for name, data in stock_data.items():
            # 简化版资金流向估算
            volume = data.get('volume', 0)
            price = data.get('current_price', 0)
            change_percent = data.get('change_percent', 0)
            
            # 估算资金流向
            turnover = volume * price  # 成交额
            
            # 根据涨跌幅判断资金流向方向
            if change_percent > 0:
                flow_direction = "流入"
                flow_amount = turnover * abs(change_percent) / 100
            else:
                flow_direction = "流出"
                flow_amount = -turnover * abs(change_percent) / 100
            
            flows[name] = {
                'turnover': turnover,
                'flow_direction': flow_direction,
                'flow_amount': flow_amount,
                'flow_strength': '强' if abs(change_percent) > 2 else '中' if abs(change_percent) > 1 else '弱'
            }
        
        return flows
    
    def _calculate_sector_flows(self, stock_data: Dict, stock_flows: Dict) -> Dict:
        """计算板块资金流向"""
        sector_flows = defaultdict(lambda: {'total_flow': 0, 'stocks': []})
        
        for name, flow in stock_flows.items():
            if name in stock_data:
                sector = stock_data[name].get('sector', '未知')
                sector_flows[sector]['total_flow'] += flow['flow_amount']
                sector_flows[sector]['stocks'].append(name)
        
        # 计算板块流向方向
        for sector, data in sector_flows.items():
            data['flow_direction'] = "流入" if data['total_flow'] > 0 else "流出"
            data['flow_strength'] = '强' if abs(data['total_flow']) > 10000000 else '中' if abs(data['total_flow']) > 5000000 else '弱'
        
        return dict(sector_flows)
    
    def _identify_capital_hotspots(self, stock_flows: Dict) -> List[Dict]:
        """识别资金热点"""
        hotspots = []
        
        # 按资金流向金额排序
        sorted_flows = sorted(stock_flows.items(), key=lambda x: abs(x[1]['flow_amount']), reverse=True)
        
        # 识别前3个热点
        for name, flow in sorted_flows[:3]:
            hotspots.append({
                'stock': name,
                'flow_direction': flow['flow_direction'],
                'flow_amount': flow['flow_amount'],
                'flow_strength': flow['flow_strength'],
                'interpretation': f"{name}资金{flow['flow_direction']}{flow['flow_strength']}"
            })
        
        return hotspots
    
    def _analyze_flow_trend(self, stock_flows: Dict) -> Dict:
        """分析资金流向趋势"""
        inflow_count = sum(1 for flow in stock_flows.values() if flow['flow_direction'] == "流入")
        outflow_count = len(stock_flows) - inflow_count
        
        total_inflow = sum(flow['flow_amount'] for flow in stock_flows.values() if flow['flow_amount'] > 0)
        total_outflow = abs(sum(flow['flow_amount'] for flow in stock_flows.values() if flow['flow_amount'] < 0))
        
        net_flow = total_inflow - total_outflow
        
        if net_flow > 0:
            trend = "净流入"
            interpretation = f"市场资金净流入¥{net_flow:.2f}，市场情绪偏乐观"
        elif net_flow < 0:
            trend = "净流出"
            interpretation = f"市场资金净流出¥{abs(net_flow):.2f}，市场情绪偏谨慎"
        else:
            trend = "平衡"
            interpretation = "市场资金流入流出基本平衡"
        
        return {
            'trend': trend,
            'net_flow': net_flow,
            'inflow_count': inflow_count,
            'outflow_count': outflow_count,
            'total_inflow': total_inflow,
            'total_outflow': total_outflow,
            'interpretation': interpretation
        }


# 使用示例
if __name__ == "__main__":
    # 测试数据
    test_stock_data = {
        '科创信息': {
            'symbol': '300730.SZ',
            'sector': '信息技术',
            'current_price': 14.69,
            'open_price': 14.67,
            'high_price': 14.99,
            'low_price': 14.65,
            'volume': 5742100,
            'change_percent': 0.14
        },
        '赛恩斯': {
            'symbol': '688480.SS',
            'sector': '环保工程',
            'current_price': 75.82,
            'open_price': 75.00,
            'high_price': 76.50,
            'low_price': 74.80,
            'volume': 329000,
            'change_percent': 1.09
        }
    }
    
    # 板块分析
    sector_analyzer = SectorAnalyzer()
    sector_result = sector_analyzer.analyze_sectors(test_stock_data)
    print("板块分析结果:")
    print(f"板块排名: {sector_result['sector_ranking']}")
    
    # 风险分析
    test_portfolio = {
        '科创信息': {'weight_percent': 50, 'investment_amount': 50000},
        '赛恩斯': {'weight_percent': 50, 'investment_amount': 50000}
    }
    
    risk_analyzer = RiskAnalyzer()
    risk_result = risk_analyzer.analyze_portfolio_risk(test_stock_data, test_portfolio)
    print("\n风险分析结果:")
    print(f"风险等级: {risk_result['risk_level']}")
    print(f"VaR(95%): ¥{risk_result['var']['var_95']:.2f}")
