#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业股票投资辅助工具 - 演示脚本
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n🔧 {description}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ 命令执行成功")
            if result.stdout.strip():
                print(f"输出:\n{result.stdout}")
        else:
            print(f"❌ 命令执行失败 (返回码: {result.returncode})")
            if result.stderr.strip():
                print(f"错误:\n{result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 命令执行异常: {e}")
        return False

def demo_basic_analysis():
    """演示基本分析功能"""
    print("\n" + "="*60)
    print("🎯 演示1: 基本股票分析")
    print("="*60)
    
    # 创建测试配置文件
    config_content = {
        "version": "2.0",
        "data_sources": {
            "sina": {"enabled": True, "priority": 1},
            "eastmoney": {"enabled": False, "priority": 2},
            "tushare": {"enabled": False, "priority": 3, "token": ""}
        },
        "analysis": {
            "technical": True,
            "fundamental": True,
            "sentiment": True,
            "ai_analysis": False
        }
    }
    
    config_path = Path("demo_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_content, f, indent=2)
    
    print(f"📁 创建演示配置文件: {config_path}")
    
    # 运行分析命令
    symbols = "300730.SZ,688480.SS"  # 只分析2只股票，避免网络请求过多
    cmd = f"{sys.executable} stock_pro_tool.py analyze --symbols {symbols} --profile 稳健型 --amount 50000 --format console"
    
    return run_command(cmd, f"分析股票 {symbols}")

def demo_config_management():
    """演示配置管理功能"""
    print("\n" + "="*60)
    print("⚙️  演示2: 配置管理")
    print("="*60)
    
    steps = [
        ("查看当前配置", f"{sys.executable} stock_pro_tool.py config --list"),
        ("更新监控间隔", f"{sys.executable} stock_pro_tool.py config --set monitoring.interval_minutes 10"),
        ("更新预警阈值", f"{sys.executable} stock_pro_tool.py config --set monitoring.alert_threshold_percent 1.5"),
        ("验证更新结果", f"{sys.executable} stock_pro_tool.py config --get monitoring.interval_minutes"),
    ]
    
    success = True
    for desc, cmd in steps:
        if not run_command(cmd, desc):
            success = False
    
    return success

def demo_help_system():
    """演示帮助系统"""
    print("\n" + "="*60)
    print("📖 演示3: 帮助系统")
    print("="*60)
    
    steps = [
        ("主帮助", f"{sys.executable} stock_pro_tool.py --help"),
        ("分析命令帮助", f"{sys.executable} stock_pro_tool.py analyze --help"),
        ("配置命令帮助", f"{sys.executable} stock_pro_tool.py config --help"),
    ]
    
    success = True
    for desc, cmd in steps:
        if not run_command(cmd, desc):
            success = False
    
    return success

def create_sample_report():
    """创建示例报告"""
    print("\n" + "="*60)
    print("📄 演示4: 创建示例报告")
    print("="*60)
    
    # 创建示例报告数据
    sample_report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "user_profile": "稳健型",
            "investment_amount": 100000,
            "stocks_analyzed": 2,
            "framework": "DIKW (数据-信息-知识-智慧)"
        },
        "summary": {
            "market_overview": {
                "trend": "温和上涨",
                "rising_stocks": 1,
                "falling_stocks": 1,
                "average_change": 0.75
            },
            "investment_strategy": {
                "risk_tolerance": "中等",
                "target_return": "年化10-15%",
                "max_drawdown": "10%"
            },
            "portfolio_recommendation": {
                "科创信息": {"weight": 35, "amount": 35000},
                "赛恩斯": {"weight": 25, "amount": 25000},
                "cash_reserve": {"weight": 40, "amount": 40000}
            }
        }
    }
    
    report_path = Path("demo_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(sample_report, f, ensure_ascii=False, indent=2)
    
    print(f"📁 创建示例报告: {report_path}")
    print("报告内容预览:")
    print(json.dumps(sample_report["summary"], ensure_ascii=False, indent=2))
    
    return True

def show_tool_structure():
    """显示工具结构"""
    print("\n" + "="*60)
    print("🏗️  工具结构概览")
    print("="*60)
    
    files = [
        ("stock_pro_tool.py", "主程序，包含核心框架"),
        ("config_template.json", "配置文件模板"),
        ("README_PRO_TOOL.md", "完整使用文档"),
        ("test_pro_tool.py", "功能测试脚本"),
        ("setup.py", "安装脚本"),
        ("requirements.txt", "依赖清单"),
        ("examples/", "示例脚本目录"),
        ("PROFESSIONAL_STOCK_TOOL_PLAN.md", "项目计划"),
        ("UPDATE_SUMMARY.md", "更新总结")
    ]
    
    print("📁 项目文件结构:")
    for filename, description in files:
        print(f"  • {filename:30} - {description}")
    
    print("\n🎯 核心模块:")
    modules = [
        "ConfigManager - 配置管理",
        "DataFetcher - 数据获取",
        "DIKWEngine - DIKW分析引擎", 
        "CLI - 命令行界面",
        "Stock/PortfolioAllocation - 数据模型"
    ]
    
    for module in modules:
        print(f"  • {module}")
    
    return True

def main():
    """主演示函数"""
    print("🚀 专业股票投资辅助工具 - 功能演示")
    print("="*60)
    print("作者: DT老炮 | 版本: 2.0 | 日期: 2026-04-14")
    print("="*60)
    
    # 检查Python版本
    print(f"🐍 Python版本: {sys.version}")
    
    # 执行演示
    demos = [
        ("工具结构", show_tool_structure),
        ("帮助系统", demo_help_system),
        ("配置管理", demo_config_management),
        ("基本分析", demo_basic_analysis),
        ("示例报告", create_sample_report),
    ]
    
    results = []
    for demo_name, demo_func in demos:
        print(f"\n▶️  开始演示: {demo_name}")
        try:
            success = demo_func()
            results.append((demo_name, success))
            if success:
                print(f"✅ {demo_name} 演示成功")
            else:
                print(f"⚠️  {demo_name} 演示部分成功")
        except Exception as e:
            print(f"❌ {demo_name} 演示失败: {e}")
            results.append((demo_name, False))
    
    # 显示演示结果
    print("\n" + "="*60)
    print("📊 演示结果汇总")
    print("="*60)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for demo_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{demo_name:20} {status}")
    
    print(f"\n🎯 成功率: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
    
    # 清理临时文件
    print("\n🧹 清理临时文件...")
    temp_files = ["demo_config.json", "demo_report.json"]
    for temp_file in temp_files:
        if Path(temp_file).exists():
            Path(temp_file).unlink()
            print(f"  删除: {temp_file}")
    
    print("\n" + "="*60)
    print("🎉 演示完成!")
    print("\n📝 下一步建议:")
    print("1. 完整测试: python test_pro_tool.py")
    print("2. 查看文档: cat README_PRO_TOOL.md")
    print("3. 运行示例: cd examples && python basic_analysis.py")
    print("4. 实际使用: python stock_pro_tool.py analyze --help")
    print("\n💡 提示: 实际股票分析需要网络连接获取实时数据")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断演示")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 演示异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)