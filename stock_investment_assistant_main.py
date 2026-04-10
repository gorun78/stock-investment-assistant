#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资决策辅助系统 - 主程序入口
"""

import sys
import os
# 设置系统编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stock_investment_assistant import DIKWStockAssistant

def main():
    """主程序入口"""
    print("🚀 股票投资决策辅助系统 v1.0")
    print("基于DIKW框架: 数据→信息→知识→智慧")
    print("="*60)
    
    # 用户配置
    print("\n📝 请配置您的投资偏好:")
    print("1. 激进型 (高风险高收益)")
    print("2. 稳健型 (中等风险稳健增长)")
    print("3. 保守型 (低风险保值增值)")
    
    while True:
        try:
            choice = input("请选择(1/2/3, 默认2): ").strip()
            if choice == "":
                choice = "2"
            if choice in ["1", "2", "3"]:
                break
            print("请输入1、2或3")
        except KeyboardInterrupt:
            print("\n👋 程序已退出")
            return
    
    risk_profiles = {"1": "激进型", "2": "稳健型", "3": "保守型"}
    risk_profile = risk_profiles[choice]
    
    # 投资金额
    while True:
        try:
            amount_str = input(f"请输入投资金额(元, 默认100000): ").strip()
            if amount_str == "":
                investment_amount = 100000
                break
            investment_amount = float(amount_str)
            if investment_amount <= 0:
                print("投资金额必须大于0")
                continue
            break
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            print("\n👋 程序已退出")
            return
    
    print("\n" + "="*60)
    
    # 创建投资助手实例
    assistant = DIKWStockAssistant(
        user_risk_profile=risk_profile,
        investment_amount=investment_amount
    )
    
    # 生成完整报告
    try:
        report = assistant.generate_complete_report()
        
        # 显示摘要报告
        assistant.display_summary_report()
        
        # 保存报告
        save_choice = input("\n💾 是否保存完整报告到文件? (y/n, 默认y): ").strip().lower()
        if save_choice != "n":
            filename = assistant.save_report_to_file(report)
            print(f"✅ 完整报告已保存到: {filename}")
        
        # 提供后续操作建议
        print("\n🎯 后续操作建议:")
        print("1. 根据投资组合建议分批建仓")
        print("2. 设置价格预警监控")
        print("3. 定期运行本程序更新分析")
        print("4. 关注公司基本面和行业政策变化")
        
        print("\n👋 分析完成! 祝您投资顺利!")
        
    except Exception as e:
        print(f"\n❌ 程序执行出错: {str(e)}")
        print("请检查网络连接或稍后重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {str(e)}")
        import traceback
        traceback.print_exc()