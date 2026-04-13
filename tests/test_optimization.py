#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证第二、三阶段优化功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from technical_indicators import TechnicalIndicators
from advanced_analyzer import SectorAnalyzer, RiskAnalyzer, CapitalFlowAnalyzer
from portfolio_optimizer import PortfolioOptimizer
from risk_timing import DynamicRiskController, TimingStrategy


def test_technical_indicators():
    """测试技术指标模块"""
    print("\n" + "="*60)
    print("测试1: 技术指标分析模块")
    print("="*60)
    
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
    
    # 创建技术指标计算器
    ti = TechnicalIndicators()
    
    # 生成技术分析报告
    report = ti.generate_technical_report(test_data)
    
    print(f"股票: {report['stock_name']} ({report['symbol']})")
    print(f"当前价格: ¥{report['current_price']:.2f}")
    print(f"技术评分: {report['technical_score']['score']:.1f} ({report['technical_score']['rating']})")
    print(f"操作建议: {report['recommendation']['rating']}")
    print("具体建议:")
    for action in report['recommendation']['actions']:
        print(f"  - {action}")
    
    print("\n✅ 技术指标模块测试通过")
    return True


def test_sector_analyzer():
    """测试板块分析模块"""
    print("\n" + "="*60)
    print("测试2: 板块深度分析模块")
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
        },
        '景嘉微': {
            'symbol': '300474.SZ',
            'sector': '半导体',
            'current_price': 144.16,
            'open_price': 140.00,
            'high_price': 146.00,
            'low_price': 139.50,
            'volume': 856000,
            'change_percent': 2.97
        }
    }
    
    # 创建板块分析器
    analyzer = SectorAnalyzer()
    result = analyzer.analyze_sectors(test_stock_data)
    
    print("板块排名:")
    for i, sector in enumerate(result['sector_ranking'], 1):
        print(f"  {i}. {sector['sector']}: {sector['avg_change']:+.2f}% ({sector['strength']})")
    
    print("\n板块轮动预测:")
    for pred in result['rotation_prediction']['predictions']:
        print(f"  - {pred['sector']}: {pred['prediction']}")
    
    print("\n✅ 板块分析模块测试通过")
    return True


def test_risk_analyzer():
    """测试风险分析模块"""
    print("\n" + "="*60)
    print("测试3: 风险评估增强模块")
    print("="*60)
    
    # 测试数据
    test_stock_data = {
        '科创信息': {
            'symbol': '300730.SZ',
            'current_price': 14.69,
            'open_price': 14.67,
            'high_price': 14.99,
            'low_price': 14.65,
            'volume': 5742100,
            'change_percent': 0.14
        },
        '赛恩斯': {
            'symbol': '688480.SS',
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
    
    # 创建风险分析器
    analyzer = RiskAnalyzer()
    result = analyzer.analyze_portfolio_risk(test_stock_data, test_portfolio)
    
    print(f"风险等级: {result['risk_level']}")
    print(f"组合波动率: {result['portfolio_volatility']['portfolio_volatility']:.2f}%")
    print(f"VaR(95%): ¥{result['var']['var_95']:.2f} ({result['var']['var_95_percent']:.2f}%)")
    
    print("\n压力测试结果:")
    for scenario, data in result['stress_test']['scenarios'].items():
        print(f"  - {scenario}: 损失{data['loss_percent']:.2f}% ({data['impact']})")
    
    print("\n风险建议:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
    
    print("\n✅ 风险分析模块测试通过")
    return True


def test_portfolio_optimizer():
    """测试投资组合优化模块"""
    print("\n" + "="*60)
    print("测试4: 投资组合优化模块")
    print("="*60)
    
    # 测试数据
    test_stock_data = {
        '科创信息': {
            'symbol': '300730.SZ',
            'current_price': 14.69,
            'open_price': 14.67,
            'high_price': 14.99,
            'low_price': 14.65,
            'change_percent': 0.14
        },
        '赛恩斯': {
            'symbol': '688480.SS',
            'current_price': 75.82,
            'open_price': 75.00,
            'high_price': 76.50,
            'low_price': 74.80,
            'change_percent': 1.09
        },
        '景嘉微': {
            'symbol': '300474.SZ',
            'current_price': 144.16,
            'open_price': 140.00,
            'high_price': 146.00,
            'low_price': 139.50,
            'change_percent': 2.97
        }
    }
    
    # 创建优化器
    optimizer = PortfolioOptimizer()
    
    # 测试均值-方差优化
    print("均值-方差优化:")
    result_mv = optimizer.optimize_portfolio(test_stock_data, method='mean_variance', risk_profile='稳健型')
    print(f"  方法: {result_mv['method']}")
    print(f"  状态: {result_mv['status']}")
    if result_mv['status'] == 'success':
        print(f"  预期收益: {result_mv['expected_return']*100:.2f}%")
        print(f"  波动率: {result_mv['volatility']*100:.2f}%")
        print(f"  夏普比率: {result_mv['sharpe_ratio']:.3f}")
        print("  权重分配:")
        for stock, weight in result_mv['weights'].items():
            print(f"    - {stock}: {weight:.1f}%")
    
    # 测试风险平价优化
    print("\n风险平价优化:")
    result_rp = optimizer.optimize_portfolio(test_stock_data, method='risk_parity')
    print(f"  方法: {result_rp['method']}")
    print(f"  状态: {result_rp['status']}")
    if result_rp['status'] == 'success':
        print(f"  夏普比率: {result_rp['sharpe_ratio']:.3f}")
        print("  权重分配:")
        for stock, weight in result_rp['weights'].items():
            print(f"    - {stock}: {weight:.1f}%")
    
    print("\n✅ 投资组合优化模块测试通过")
    return True


def test_dynamic_risk_controller():
    """测试动态风险控制模块"""
    print("\n" + "="*60)
    print("测试5: 动态风险控制模块")
    print("="*60)
    
    # 测试数据
    test_stock_data = {
        'symbol': '300730.SZ',
        'current_price': 14.69,
        'open_price': 14.67,
        'high_price': 14.99,
        'low_price': 14.65,
        'change_percent': 0.14
    }
    
    # 创建动态风险控制器
    controller = DynamicRiskController()
    
    # 测试动态止损
    print("动态止损调整:")
    stop_loss = controller.adjust_stop_loss(test_stock_data, '震荡整理', '稳健型', 10)
    print(f"  止损百分比: {stop_loss['stop_loss_percent']:.2f}%")
    print(f"  止损价格: ¥{stop_loss['stop_loss_price']:.2f}")
    print(f"  调整原因: {stop_loss['reason']}")
    
    # 测试动态止盈
    print("\n动态止盈调整:")
    take_profit = controller.adjust_take_profit(test_stock_data, '震荡整理', '稳健型', 5)
    print(f"  止盈百分比: {take_profit['take_profit_percent']:.2f}%")
    print(f"  止盈价格: ¥{take_profit['take_profit_price']:.2f}")
    print(f"  调整原因: {take_profit['reason']}")
    
    print("\n✅ 动态风险控制模块测试通过")
    return True


def test_timing_strategy():
    """测试智能择时策略模块"""
    print("\n" + "="*60)
    print("测试6: 智能择时策略模块")
    print("="*60)
    
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
    
    # 创建择时策略
    strategy = TimingStrategy()
    result = strategy.analyze_timing(test_stock_data, test_market_analysis, '稳健型')
    
    print(f"综合信号: {result['combined_signal']['signal']}")
    print(f"建议操作: {result['combined_signal']['action']}")
    print(f"信号评分: {result['combined_signal']['score']:.0f}")
    print(f"置信度: {result['combined_signal']['confidence']}")
    print(f"信号原因: {result['combined_signal']['reason']}")
    
    print("\n各策略信号:")
    print(f"  趋势跟踪: {result['trend_timing']['market_signal']}")
    print(f"  市场情绪: {result['sentiment_timing']['signal']}")
    print(f"  时间择时: {result['time_timing']['time_signal']}")
    
    print("\n✅ 智能择时策略模块测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始运行第二、三阶段优化功能测试")
    print("="*60)
    
    tests = [
        ("技术指标分析", test_technical_indicators),
        ("板块深度分析", test_sector_analyzer),
        ("风险评估增强", test_risk_analyzer),
        ("投资组合优化", test_portfolio_optimizer),
        ("动态风险控制", test_dynamic_risk_controller),
        ("智能择时策略", test_timing_strategy)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"\n❌ {name}测试失败: {str(e)}")
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
        if error:
            print(f"  错误: {error}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！第二、三阶段优化功能正常工作。")
    else:
        print(f"\n⚠️  {total-passed} 个测试失败，请检查相关模块。")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
