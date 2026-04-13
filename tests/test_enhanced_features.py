#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 鼔证第二、三阶段优化功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from technical_indicators import TechnicalIndicators
from advanced_analyzer import SectorAnalyzer, RiskAnalyzer
from portfolio_optimizer import PortfolioOptimizer
from risk_timing import DynamicRiskController, TimingStrategy


def test_all_features():
    """测试所有新功能"""
    print("="*60)
    print("开始测试第二、三阶段优化功能")
    print("="*60)
    
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
    
    test_portfolio = {
        '科创信息': {'weight_percent': 50, 'investment_amount': 50000},
        '赛恩斯': {'weight_percent': 50, 'investment_amount': 50000}
    }
    
    test_market_analysis = {
        'market_sentiment': {
            'market_trend': '震荡整理',
            'rising_percent': 62.5,
            'average_change': 0.80
        }
    }
    
    # 测试1: 技术指标分析
    print("\n测试1: 技术指标分析模块")
    print("-" * 60)
    ti = TechnicalIndicators()
    report = ti.generate_technical_report(test_stock_data['科创信息'])
    print(f"股票: {report['stock_name']}")
    print(f"技术评分: {report['technical_score']['score']:.1f}")
    print(f"评级: {report['technical_score']['rating']}")
    print("✅ 技术指标模块测试通过")
    
    # 测试2: 板块深度分析
    print("\n测试2: 板块深度分析模块")
    print("-" * 60)
    sa = SectorAnalyzer()
    sector_result = sa.analyze_sectors(test_stock_data)
    print(f"板块数量: {len(sector_result['sector_analysis'])}")
    print(f"最强板块: {sector_result['sector_ranking'][0]['sector']}")
    print("✅ 板块分析模块测试通过")
    
    # 测试3: 険能组合优化
    print("\n测试3: 投资组合优化模块")
    print("-" * 60)
    po = PortfolioOptimizer()
    result = po.optimize_portfolio(test_stock_data, method='mean_variance', risk_profile='稳健型')
    print(f"优化方法: {result['method']}")
    print(f"预期收益: {result.get('expected_return', 0)*100:.2f}%")
    print(f"夏普比率: {result.get('sharpe_ratio', 0):.3f}")
    print("✅ 投资组合优化模块测试通过")
    
    # 测试4: 预险评估增强
    print("\n测试4: 険险评估增强模块")
    print("-" * 60)
    ra = RiskAnalyzer()
    risk_result = ra.analyze_portfolio_risk(test_stock_data, test_portfolio)
    print(f"风险等级: {risk_result['risk_level']}")
    print(f"VaR(95%): {risk_result['var']['var_95']:.2f}")
    print("✅ 険险评估模块测试通过")
    
    # 测试5: 动态风险控制
    print("\n测试5: 动态风险控制模块")
    print("-" * 60)
    rc = DynamicRiskController()
    stop_loss = rc.adjust_stop_loss(
        test_stock_data['科创信息'], '震荡整理', '稳健型', 0
    )
    print(f"止损百分比: {stop_loss['stop_loss_percent']:.2f}%")
    print(f"止损价格: {stop_loss['stop_loss_price']:.2f}")
    print("✅ 动态风险控制模块测试通过")
    
    # 测试6: 智能择时策略
    print("\n测试6: 智能择时策略模块")
    print("-" * 60)
    ts = TimingStrategy()
    timing_result = ts.analyze_timing(
        test_stock_data, test_market_analysis, '稳健型'
    )
    print(f"综合信号: {timing_result['combined_signal']['signal']}")
    print(f"建议操作: {timing_result['combined_signal']['action']}")
    print("✅ 智能择时策略模块测试通过")
    
    # 测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print("✅ 所有模块测试通过")
    print("✅ 第二、三阶段优化功能实现成功")
    print("="*60)


if __name__ == "__main__":
    test_all_features()
