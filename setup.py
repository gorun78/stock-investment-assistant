#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业股票投资辅助工具 - 安装脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 8):
        print(f"❌ 需要Python 3.8+，当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")
    
    dependencies = [
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "pandas>=2.0.0",  # 可选，用于高级分析
        "numpy>=1.24.0",   # 可选，用于数值计算
    ]
    
    try:
        # 使用pip安装
        for dep in dependencies:
            print(f"  安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def create_config_directory():
    """创建配置目录"""
    print("\n⚙️  创建配置目录...")
    
    config_dir = Path.home() / ".stock_pro_tool"
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 配置目录: {config_dir}")
        
        # 复制配置文件模板
        config_template = Path("config_template.json")
        if config_template.exists():
            config_file = config_dir / "config.json"
            if not config_file.exists():
                shutil.copy(config_template, config_file)
                print(f"✅ 配置文件已创建: {config_file}")
            else:
                print(f"⚠️  配置文件已存在: {config_file}")
        
        return True
    except Exception as e:
        print(f"❌ 创建配置目录失败: {e}")
        return False

def create_example_scripts():
    """创建示例脚本"""
    print("\n📝 创建示例脚本...")
    
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    # 示例1: 基本分析
    example1 = examples_dir / "basic_analysis.py"
    example1.write_text("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本分析示例
"""

import asyncio
import json
from datetime import datetime
from stock_pro_tool import ConfigManager, DataFetcher, DIKWEngine

async def main():
    # 初始化
    config = ConfigManager()
    data_fetcher = DataFetcher(config)
    engine = DIKWEngine(config, data_fetcher)
    
    # 分析股票
    symbols = ["300730.SZ", "688480.SS", "300474.SZ"]
    report = await engine.analyze(
        symbols=symbols,
        user_profile="稳健型",
        investment_amount=100000
    )
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_report_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析报告已保存: {filename}")
    
    # 显示摘要
    print("\\n📊 分析摘要:")
    print(f"  股票数量: {len(symbols)}")
    print(f"  投资金额: ¥{report['metadata']['investment_amount']:,}")
    print(f"  风险偏好: {report['metadata']['user_profile']}")

if __name__ == "__main__":
    asyncio.run(main())
""")
    print(f"✅ 创建示例1: {example1}")
    
    # 示例2: 批量分析
    example2 = examples_dir / "batch_analysis.py"
    example2.write_text("""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分析示例 - 分析多个风险偏好
"""

import asyncio
import json
from datetime import datetime
from stock_pro_tool import ConfigManager, DataFetcher, DIKWEngine

async def analyze_profile(symbols, profile, amount):
    """分析特定风险偏好"""
    config = ConfigManager()
    data_fetcher = DataFetcher(config)
    engine = DIKWEngine(config, data_fetcher)
    
    print(f"📊 分析 {profile} 策略...")
    report = await engine.analyze(symbols, profile, amount)
    
    # 保存报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{profile}_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 报告已保存: {filename}")
    
    # 显示关键信息
    portfolio = report['knowledge_layer']['portfolio_allocation']
    total_invested = sum(alloc['target_amount'] for alloc in portfolio.values())
    cash_reserve = amount - total_invested
    
    print(f"  投资组合: {len(portfolio)} 只股票")
    print(f"  现金储备: ¥{cash_reserve:.0f} ({cash_reserve/amount*100:.1f}%)")
    
    return report

async def main():
    symbols = ["300730.SZ", "688480.SS", "300474.SZ", "300454.SZ"]
    amount = 100000
    
    print("🚀 批量分析不同风险偏好")
    print("="*60)
    
    profiles = ["激进型", "稳健型", "保守型"]
    
    for profile in profiles:
        await analyze_profile(symbols, profile, amount)
        print()
    
    print("✅ 批量分析完成!")

if __name__ == "__main__":
    asyncio.run(main())
""")
    print(f"✅ 创建示例2: {example2}")
    
    # 示例3: 命令行使用
    example3 = examples_dir / "cli_usage.sh"
    example3.write_text("""#!/bin/bash
# 命令行使用示例

echo "🚀 专业股票投资辅助工具 - 命令行示例"
echo "="*60

# 1. 显示帮助
echo "1. 显示帮助:"
python stock_pro_tool.py --help
echo

# 2. 列出配置
echo "2. 列出当前配置:"
python stock_pro_tool.py config --list
echo

# 3. 分析股票
echo "3. 分析股票 (稳健型策略):"
python stock_pro_tool.py analyze \\
  --symbols "300730.SZ,688480.SS,300474.SZ" \\
  --profile 稳健型 \\
  --amount 50000 \\
  --output analysis_report.json
echo

# 4. 更新配置
echo "4. 更新监控设置:"
python stock_pro_tool.py config --set monitoring.interval_minutes 10
python stock_pro_tool.py config --set monitoring.alert_threshold_percent 1.5
echo

echo "✅ 示例命令完成!"
echo "💡 提示: 实际使用时请根据需求调整参数"
""")
    # 设置执行权限
    example3.chmod(0o755)
    print(f"✅ 创建示例3: {example3}")
    
    return True

def create_requirements_file():
    """创建requirements.txt文件"""
    print("\n📄 创建requirements.txt...")
    
    requirements = """# 专业股票投资辅助工具 - 依赖包
# 基础依赖
requests>=2.31.0
aiohttp>=3.9.0

# 可选依赖 - 用于高级分析
# pandas>=2.0.0
# numpy>=1.24.0
# matplotlib>=3.7.0  # 用于图表生成

# 专业数据源
# tushare>=1.2.89  # 需要token，取消注释启用

# AI分析
# openai>=1.0.0  # 需要API key，取消注释启用

# 安装命令: pip install -r requirements.txt
# 最小安装: pip install requests aiohttp
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    
    print("✅ requirements.txt 已创建")
    return True

def main():
    """主安装函数"""
    print("🚀 专业股票投资辅助工具 - 安装程序")
    print("="*60)
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"📁 安装目录: {current_dir}")
    
    # 检查必要文件
    required_files = ["stock_pro_tool.py", "config_template.json"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        print("请确保在项目根目录运行安装脚本")
        return False
    
    # 执行安装步骤
    steps = [
        ("检查Python版本", check_python_version),
        ("安装依赖包", install_dependencies),
        ("创建配置目录", create_config_directory),
        ("创建示例脚本", create_example_scripts),
        ("创建依赖文件", create_requirements_file),
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} 失败")
            success = False
            # 继续执行其他步骤
    
    print("\n" + "="*60)
    
    if success:
        print("🎉 安装完成!")
        print("\n📋 下一步:")
        print("1. 测试安装: python test_pro_tool.py")
        print("2. 查看示例: ls examples/")
        print("3. 运行分析: python stock_pro_tool.py analyze --help")
        print("4. 配置数据源: 编辑 ~/.stock_pro_tool/config.json")
        print("\n💡 提示:")
        print("  • 首次使用建议运行测试脚本")
        print("  • 配置Tushare token获取更稳定数据")
        print("  • 查看README_PRO_TOOL.md获取详细说明")
    else:
        print("⚠️  安装过程中遇到问题")
        print("\n🔧 故障排除:")
        print("1. 确保Python版本 ≥ 3.8")
        print("2. 检查网络连接")
        print("3. 手动安装依赖: pip install requests aiohttp")
        print("4. 手动创建配置目录: mkdir -p ~/.stock_pro_tool")
    
    print("\n👋 安装程序结束")
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)