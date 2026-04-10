#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版股票投资决策辅助系统测试
移除pandas依赖，使用纯Python实现
"""

import json
import time
import requests
from datetime import datetime

# 简化的DIKW助手
class SimpleDIKWAssistant:
    def __init__(self, risk_profile="稳健型", amount=100000):
        self.risk_profile = risk_profile
        self.amount = amount
        self.stocks = {
            "科创信息": "300730.SZ",
            "赛恩斯": "688480.SS", 
            "景嘉微": "300474.SZ",
            "深信服": "300454.SZ",
            "科大讯飞": "002230.SZ",
            "万兴科技": "300624.SZ",
            "威胜信息": "688100.SS",
            "超图软件": "300036.SZ"
        }
        
        print(f"🎯 简化版DIKW投资助手启动")
        print(f"📊 风险偏好: {risk_profile} | 投资金额: ¥{amount:,}")
        print("="*60)
    
    def get_stock_price(self, symbol):
        """获取股票价格（简化版）"""
        try:
            if symbol.endswith(".SZ"):
                market = "sz"
                code = symbol.replace(".SZ", "")
            else:
                market = "sh" 
                code = symbol.replace(".SS", "")
            
            url = f"http://hq.sinajs.cn/list={market}{code}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data_str = response.text.split('"')[1]
                if data_str:
                    parts = data_str.split(',')
                    if len(parts) > 3:
                        return float(parts[3])
        except:
            pass
        return None
    
    def analyze(self):
        """执行完整的DIKW分析"""
        print("\n📈 数据层: 获取股票数据...")
        stock_data = {}
        for name, symbol in self.stocks.items():
            price = self.get_stock_price(symbol)
            if price:
                stock_data[name] = {"symbol": symbol, "price": price, "time": datetime.now().strftime("%H:%M:%S")}
                print(f"  ✓ {name}: ¥{price:.2f}")
            else:
                # 使用模拟数据
                import random
                mock_price = random.uniform(10, 150)
                stock_data[name] = {"symbol": symbol, "price": mock_price, "time": "模拟数据", "is_mock": True}
                print(f"  ⚠ {name}: ¥{mock_price:.2f} (模拟)")
        
        print("\n📊 信息层: 市场分析...")
        if stock_data:
            prices = [data["price"] for data in stock_data.values()]
            avg_price = sum(prices) / len(prices)
            print(f"  • 平均股价: ¥{avg_price:.2f}")
            print(f"  • 最高价: ¥{max(prices):.2f}")
            print(f"  • 最低价: ¥{min(prices):.2f}")
        
        print("\n🧠 知识层: 投资策略生成...")
        strategies = {
            "激进型": {"核心股票": ["深信服", "科大讯飞", "景嘉微"], "仓位": "80%股票+20%现金"},
            "稳健型": {"核心股票": ["赛恩斯", "威胜信息", "万兴科技"], "仓位": "60%股票+40%现金"},
            "保守型": {"核心股票": ["科创信息", "超图软件"], "仓位": "40%股票+60%现金"}
        }
        
        strategy = strategies.get(self.risk_profile, strategies["稳健型"])
        print(f"  • 适用策略: {self.risk_profile}")
        print(f"  • 核心股票: {', '.join(strategy['核心股票'])}")
        print(f"  • 建议仓位: {strategy['仓位']}")
        
        print("\n🌟 智慧层: 投资决策建议...")
        wisdom = {
            "系统理解": "股票投资是基本面、技术面、情绪面的多维度系统",
            "核心判断": "科技主线 + 政策受益 + 稳健增长",
            "短期重点": f"{strategy['核心股票'][0]}和{strategy['核心股票'][1]}",
            "操作建议": "分批建仓，控制成本，严格执行止损"
        }
        
        for key, value in wisdom.items():
            print(f"  • {key}: {value}")
        
        print("\n💰 具体投资建议:")
        stock_count = len(strategy['核心股票'])
        base_amount = self.amount * 0.6 / stock_count  # 60%资金分配给核心股票
        
        for i, stock in enumerate(strategy['核心股票'], 1):
            if stock in stock_data:
                price = stock_data[stock]["price"]
                shares = int(base_amount / price)
                amount = shares * price
                print(f"  {i}. {stock}: {shares}股 (¥{amount:.0f}) @ ¥{price:.2f}")
        
        cash = self.amount * 0.4
        print(f"  💵 现金储备: ¥{cash:.0f} (40%)")
        
        print("\n🛡️ 风险控制:")
        risk_rules = {
            "激进型": "止损8%，止盈20%，单股≤20%",
            "稳健型": "止损6%，止盈15%，单股≤15%", 
            "保守型": "止损4%，止盈10%，单股≤10%"
        }
        print(f"  • {risk_rules.get(self.risk_profile, '未知')}")
        
        print("\n⏰ 择时建议:")
        hour = datetime.now().hour
        if 9 <= hour < 11:
            timing = "上午交易时段，可分批建仓"
        elif 13 <= hour < 15:
            timing = "下午交易时段，寻找回调机会"
        else:
            timing = "非交易时间，复盘分析"
        print(f"  • {timing}")
        
        print("\n" + "="*60)
        print("✅ 分析完成! 建议保存报告并定期更新分析")
        
        # 返回分析结果
        return {
            "stock_data": stock_data,
            "strategy": strategy,
            "wisdom": wisdom,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """主函数"""
    print("🚀 简化版股票投资决策辅助系统")
    print("="*60)
    
    # 默认配置
    risk_profile = "稳健型"
    amount = 100000
    
    print(f"\n📝 使用默认配置:")
    print(f"  • 风险偏好: {risk_profile}")
    print(f"  • 投资金额: ¥{amount:,}")
    print("\n" + "="*60)
    
    # 创建助手并分析
    assistant = SimpleDIKWAssistant(risk_profile, amount)
    result = assistant.analyze()
    
    # 保存结果
    filename = f"stock_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 分析结果已保存到: {filename}")
    print("👋 程序执行完成!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")