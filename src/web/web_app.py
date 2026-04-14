#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资决策辅助系统 - Web端
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.stock_investment_assistant_v2 import EnhancedDIKWStockAssistant, STOCK_CONFIG
from web.data_storage import data_storage

# 设置系统编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__, template_folder='templates')
app.config['JSON_AS_ASCII'] = False

# 确保reports目录存在
reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)

# 全局变量，存储投资助手实例
investment_assistant = EnhancedDIKWStockAssistant(
    user_risk_profile='稳健型',
    investment_amount=100000
)

# 当前股票配置（可修改）
current_stock_config = STOCK_CONFIG.copy()

# ==================== 模拟炒股账户 ====================
class MockTradingAccount:
    def __init__(self):
        self.balance = 100000.0  # 初始资金10万元
        self.initial_balance = 100000.0  # 初始资金（用于计算收益）
        self.positions = {}  # 持仓 {stock_name: {'quantity': int, 'avg_cost': float}}
        self.transaction_history = []  # 交易记录
        self.last_update = datetime.now()
    
    def buy_stock(self, stock_name, price, quantity):
        """买入股票"""
        total_cost = price * quantity
        if total_cost > self.balance:
            return {'success': False, 'message': '余额不足'}
        
        self.balance -= total_cost
        
        if stock_name in self.positions:
            # 计算加权平均成本
            total_quantity = self.positions[stock_name]['quantity'] + quantity
            total_spent = self.positions[stock_name]['avg_cost'] * self.positions[stock_name]['quantity'] + total_cost
            self.positions[stock_name] = {
                'quantity': total_quantity,
                'avg_cost': total_spent / total_quantity
            }
        else:
            self.positions[stock_name] = {
                'quantity': quantity,
                'avg_cost': price
            }
        
        # 记录交易
        self.transaction_history.append({
            'type': 'buy',
            'stock_name': stock_name,
            'price': price,
            'quantity': quantity,
            'total_cost': total_cost,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return {'success': True, 'message': '买入成功', 'balance': self.balance}
    
    def sell_stock(self, stock_name, price, quantity):
        """卖出股票"""
        if stock_name not in self.positions:
            return {'success': False, 'message': '未持有该股票'}
        
        if self.positions[stock_name]['quantity'] < quantity:
            return {'success': False, 'message': '持仓数量不足'}
        
        total_revenue = price * quantity
        self.balance += total_revenue
        
        self.positions[stock_name]['quantity'] -= quantity
        
        if self.positions[stock_name]['quantity'] == 0:
            del self.positions[stock_name]
        
        # 记录交易
        self.transaction_history.append({
            'type': 'sell',
            'stock_name': stock_name,
            'price': price,
            'quantity': quantity,
            'total_revenue': total_revenue,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        return {'success': True, 'message': '卖出成功', 'balance': self.balance}
    
    def get_portfolio(self, current_prices):
        """获取当前持仓和收益"""
        portfolio = []
        total_value = self.balance
        
        for stock_name, pos in self.positions.items():
            current_price = current_prices.get(stock_name, pos['avg_cost'])
            market_value = current_price * pos['quantity']
            cost_value = pos['avg_cost'] * pos['quantity']
            profit = market_value - cost_value
            profit_percent = (profit / cost_value) * 100 if cost_value > 0 else 0
            
            total_value += market_value
            
            portfolio.append({
                'stock_name': stock_name,
                'quantity': pos['quantity'],
                'avg_cost': round(pos['avg_cost'], 2),
                'current_price': round(current_price, 2),
                'market_value': round(market_value, 2),
                'cost_value': round(cost_value, 2),
                'profit': round(profit, 2),
                'profit_percent': round(profit_percent, 2)
            })
        
        total_profit = total_value - self.initial_balance
        total_profit_percent = (total_profit / self.initial_balance) * 100
        
        return {
            'balance': round(self.balance, 2),
            'total_value': round(total_value, 2),
            'total_profit': round(total_profit, 2),
            'total_profit_percent': round(total_profit_percent, 2),
            'portfolio': portfolio,
            'initial_balance': self.initial_balance
        }
    
    def get_transaction_history(self, limit=50):
        """获取交易历史"""
        return sorted(self.transaction_history, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def reset_account(self):
        """重置账户"""
        self.balance = 100000.0
        self.positions = {}
        self.transaction_history = []
        self.last_update = datetime.now()

# 创建模拟交易账户实例
trading_account = MockTradingAccount()

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/config', methods=['POST'])
def config():
    """配置投资参数"""
    global investment_assistant
    
    data = request.json
    risk_profile = data.get('risk_profile', '稳健型')
    investment_amount = float(data.get('investment_amount', 100000))
    
    investment_assistant = EnhancedDIKWStockAssistant(
        user_risk_profile=risk_profile,
        investment_amount=investment_amount,
        stock_config=current_stock_config.copy()
    )
    
    data_storage.log_operation(
        operation_type='config',
        module='投资配置',
        description=f'设置投资参数：{risk_profile} | ¥{investment_amount:,.0f}',
        details={'risk_profile': risk_profile, 'investment_amount': investment_amount}
    )
    
    return jsonify({
        'status': 'success',
        'message': f'配置成功：{risk_profile} | ¥{investment_amount:,.0f}'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """执行分析"""
    global investment_assistant
    
    try:
        report = investment_assistant.generate_complete_report()
        
        summary = {
            'market_overview': {
                'market_trend': investment_assistant.market_analysis.get('market_sentiment', {}).get('market_trend', '未知'),
                'rising_count': investment_assistant.market_analysis.get('market_sentiment', {}).get('rising_count', 0),
                'falling_count': investment_assistant.market_analysis.get('market_sentiment', {}).get('falling_count', 0),
                'average_change': investment_assistant.market_analysis.get('market_sentiment', {}).get('average_change', 0)
            },
            'top_sectors': investment_assistant.market_analysis.get('sector_analysis', {}).get('sector_ranking', [])[:3],
            'portfolio_summary': {
                'total_investment': investment_assistant.investment_amount,
                'allocated_stocks': len(investment_assistant.investment_knowledge.get('portfolio_allocation', {})),
                'sharpe_ratio': investment_assistant.investment_knowledge.get('optimized_portfolio', {}).get('sharpe_ratio', 0),
                'expected_return': investment_assistant.investment_knowledge.get('optimized_portfolio', {}).get('expected_return', 0) * 100
            },
            'timing_recommendation': {
                'signal': investment_assistant.investment_wisdom.get('timing_recommendations', {}).get('overall_signal', '未知'),
                'action': investment_assistant.investment_wisdom.get('timing_recommendations', {}).get('action', '未知'),
                'confidence': investment_assistant.investment_wisdom.get('timing_recommendations', {}).get('confidence', '中')
            },
            'risk_analysis': {
                'risk_level': investment_assistant.investment_knowledge.get('risk_analysis', {}).get('risk_level', '未知'),
                'var_95': investment_assistant.investment_knowledge.get('risk_analysis', {}).get('var', {}).get('var_95', 0),
                'risk_alerts': len(investment_assistant.investment_wisdom.get('dynamic_risk_control', {}).get('risk_alerts', []))
            },
            'immediate_actions': investment_assistant.investment_wisdom.get('personalized_advice', {}).get('immediate_actions', [])
        }
        
        data_storage.log_analysis(
            analysis_type='投资分析',
            market_trend=summary['market_overview']['market_trend'],
            top_sectors=summary['top_sectors'],
            portfolio_summary=summary['portfolio_summary'],
            timing_signal=summary['timing_recommendation']['signal'],
            risk_level=summary['risk_analysis']['risk_level']
        )
        
        data_storage.log_operation(
            operation_type='analyze',
            module='投资分析',
            description='执行投资分析',
            details=summary
        )
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'分析失败：{str(e)}'
        })

@app.route('/api/stock_data', methods=['GET'])
def stock_data():
    """获取股票数据"""
    global investment_assistant
    
    return jsonify({
        'status': 'success',
        'data': investment_assistant.stock_data
    })

@app.route('/api/generate_reports', methods=['POST'])
def generate_reports():
    """生成报告"""
    global investment_assistant
    
    try:
        # 生成报告
        generated_files = investment_assistant.generate_reports()
        
        # 提取报告文件名
        report_files = [os.path.basename(file) for file in generated_files]
        
        return jsonify({
            'status': 'success',
            'message': f'报告生成成功，共生成{len(generated_files)}个文件',
            'files': report_files
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'报告生成失败：{str(e)}'
        })

@app.route('/api/download_report/<filename>', methods=['GET'])
def download_report(filename):
    """下载报告"""
    file_path = os.path.join(reports_dir, filename)
    
    if not os.path.exists(file_path):
        return jsonify({
            'status': 'error',
            'message': '文件不存在'
        })
    
    return send_file(file_path, as_attachment=True)

# ==================== 股票维护API ====================

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表"""
    global current_stock_config
    
    stocks = []
    for name, config in current_stock_config.items():
        stocks.append({
            'name': name,
            'symbol': config['symbol'],
            'sector': config['sector'],
            'risk_level': config['risk_level']
        })
    
    return jsonify({
        'status': 'success',
        'data': stocks
    })

@app.route('/api/stocks', methods=['POST'])
def add_stock():
    """添加股票"""
    global current_stock_config
    
    data = request.json
    name = data.get('name')
    symbol = data.get('symbol')
    sector = data.get('sector', '未知')
    risk_level = data.get('risk_level', '中等')
    
    if not name or not symbol:
        return jsonify({
            'status': 'error',
            'message': '股票名称和代码不能为空'
        })
    
    # 验证股票代码格式
    if not (symbol.endswith('.SZ') or symbol.endswith('.SS')):
        return jsonify({
            'status': 'error',
            'message': '股票代码格式错误，应为XXX.SZ或XXX.SS'
        })
    
    current_stock_config[name] = {
        'symbol': symbol,
        'sector': sector,
        'risk_level': risk_level
    }
    
    return jsonify({
        'status': 'success',
        'message': f'股票 {name} 添加成功'
    })

@app.route('/api/stocks/<name>', methods=['PUT'])
def update_stock(name):
    """更新股票信息"""
    global current_stock_config
    
    if name not in current_stock_config:
        return jsonify({
            'status': 'error',
            'message': '股票不存在'
        })
    
    data = request.json
    symbol = data.get('symbol')
    sector = data.get('sector')
    risk_level = data.get('risk_level')
    
    if symbol:
        # 验证股票代码格式
        if not (symbol.endswith('.SZ') or symbol.endswith('.SS')):
            return jsonify({
                'status': 'error',
                'message': '股票代码格式错误，应为XXX.SZ或XXX.SS'
            })
        current_stock_config[name]['symbol'] = symbol
    
    if sector:
        current_stock_config[name]['sector'] = sector
    
    if risk_level:
        current_stock_config[name]['risk_level'] = risk_level
    
    return jsonify({
        'status': 'success',
        'message': f'股票 {name} 更新成功'
    })

@app.route('/api/stocks/<name>', methods=['DELETE'])
def delete_stock(name):
    """删除股票"""
    global current_stock_config
    
    if name not in current_stock_config:
        return jsonify({
            'status': 'error',
            'message': '股票不存在'
        })
    
    del current_stock_config[name]
    
    return jsonify({
        'status': 'success',
        'message': f'股票 {name} 删除成功'
    })

@app.route('/api/stocks/<name>/indicators', methods=['GET'])
def get_stock_indicators(name):
    """获取股票技术指标"""
    global investment_assistant
    
    if name not in investment_assistant.stock_data:
        return jsonify({
            'status': 'error',
            'message': '股票数据不存在'
        })
    
    stock_data = investment_assistant.stock_data[name]
    
    # 计算技术指标
    indicators = investment_assistant.technical_indicators.calculate_all_indicators(stock_data)
    
    return jsonify({
        'status': 'success',
        'data': {
            'stock_name': name,
            'current_price': stock_data.get('current_price', 0),
            'change_percent': stock_data.get('change_percent', 0),
            'indicators': indicators
        }
    })

@app.route('/api/stock_config', methods=['GET'])
def get_stock_config():
    """获取当前股票配置"""
    global current_stock_config
    return jsonify({
        'status': 'success',
        'data': current_stock_config
    })

# ==================== 智能选股API ====================

# 预设热门股票池
HOT_STOCKS = [
    {'name': '贵州茅台', 'symbol': '600519.SS', 'sector': '白酒', 'risk_level': '高', 'pe': 35.2, 'roe': 28.5, 'trend': '上升'},
    {'name': '比亚迪', 'symbol': '002594.SZ', 'sector': '新能源汽车', 'risk_level': '高', 'pe': 85.3, 'roe': 18.2, 'trend': '上升'},
    {'name': '宁德时代', 'symbol': '300750.SZ', 'sector': '锂电池', 'risk_level': '高', 'pe': 45.8, 'roe': 15.6, 'trend': '横盘'},
    {'name': '招商银行', 'symbol': '600036.SS', 'sector': '银行', 'risk_level': '低', 'pe': 8.5, 'roe': 16.2, 'trend': '上升'},
    {'name': '中国平安', 'symbol': '601318.SS', 'sector': '保险', 'risk_level': '低', 'pe': 10.2, 'roe': 12.5, 'trend': '横盘'},
    {'name': '五粮液', 'symbol': '000858.SZ', 'sector': '白酒', 'risk_level': '高', 'pe': 25.6, 'roe': 22.3, 'trend': '上升'},
    {'name': '隆基绿能', 'symbol': '601012.SS', 'sector': '光伏', 'risk_level': '中等', 'pe': 20.5, 'roe': 14.8, 'trend': '下跌'},
    {'name': '阳光电源', 'symbol': '300274.SZ', 'sector': '光伏', 'risk_level': '高', 'pe': 38.5, 'roe': 19.2, 'trend': '上升'},
    {'name': '迈瑞医疗', 'symbol': '300760.SZ', 'sector': '医疗器械', 'risk_level': '高', 'pe': 42.8, 'roe': 25.6, 'trend': '横盘'},
    {'name': '药明康德', 'symbol': '603259.SS', 'sector': '医药研发', 'risk_level': '高', 'pe': 32.5, 'roe': 16.8, 'trend': '上升'},
    {'name': '长江电力', 'symbol': '600900.SS', 'sector': '电力', 'risk_level': '低', 'pe': 18.2, 'roe': 12.8, 'trend': '横盘'},
    {'name': '美的集团', 'symbol': '000333.SZ', 'sector': '家电', 'risk_level': '中等', 'pe': 12.5, 'roe': 20.1, 'trend': '上升'},
    {'name': '格力电器', 'symbol': '000651.SZ', 'sector': '家电', 'risk_level': '中等', 'pe': 11.8, 'roe': 23.5, 'trend': '横盘'},
    {'name': '海天味业', 'symbol': '603288.SS', 'sector': '食品饮料', 'risk_level': '中等', 'pe': 35.2, 'roe': 28.2, 'trend': '下跌'},
    {'name': '伊利股份', 'symbol': '600887.SS', 'sector': '乳制品', 'risk_level': '低', 'pe': 22.5, 'roe': 19.8, 'trend': '上升'},
    {'name': '中信证券', 'symbol': '600030.SS', 'sector': '证券', 'risk_level': '中等', 'pe': 15.2, 'roe': 13.5, 'trend': '上升'},
    {'name': '东方财富', 'symbol': '300059.SZ', 'sector': '证券', 'risk_level': '高', 'pe': 28.5, 'roe': 18.6, 'trend': '上升'},
    {'name': '汇川技术', 'symbol': '300124.SZ', 'sector': '工业自动化', 'risk_level': '高', 'pe': 32.8, 'roe': 17.2, 'trend': '上升'},
    {'name': '万华化学', 'symbol': '600309.SS', 'sector': '化工', 'risk_level': '中等', 'pe': 18.5, 'roe': 25.2, 'trend': '横盘'},
    {'name': '紫金矿业', 'symbol': '601899.SS', 'sector': '有色金属', 'risk_level': '中等', 'pe': 16.8, 'roe': 19.5, 'trend': '上升'},
]

# 预设选股策略
SELECTION_STRATEGIES = [
    {'id': 'growth', 'name': '成长股策略', 'description': '高ROE、高增长潜力的成长型股票', 'risk': '高'},
    {'id': 'value', 'name': '价值股策略', 'description': '低PE、估值合理的价值型股票', 'risk': '低'},
    {'id': 'dividend', 'name': '高股息策略', 'description': '稳定分红、现金流充沛的股票', 'risk': '低'},
    {'id': 'momentum', 'name': '趋势动量策略', 'description': '近期表现强势的股票', 'risk': '高'},
    {'id': 'balanced', 'name': '均衡配置策略', 'description': '兼顾成长与价值的均衡组合', 'risk': '中等'},
]

@staticmethod
def apply_selection_strategy(stocks, strategy_id, risk_profile):
    """应用选股策略"""
    filtered = stocks.copy()
    
    if strategy_id == 'growth':
        # 成长股：高ROE、上升趋势
        filtered = [s for s in filtered if s['roe'] >= 18 and s['trend'] == '上升']
    elif strategy_id == 'value':
        # 价值股：低PE
        filtered = [s for s in filtered if s['pe'] < 20]
    elif strategy_id == 'dividend':
        # 高股息：低风险、稳定行业
        filtered = [s for s in filtered if s['risk_level'] in ['低', '中等'] and s['sector'] in ['银行', '电力', '食品饮料']]
    elif strategy_id == 'momentum':
        # 趋势动量：上升趋势
        filtered = [s for s in filtered if s['trend'] == '上升']
    elif strategy_id == 'balanced':
        # 均衡配置：各风险等级均衡
        filtered = filtered[:8]
    
    # 根据风险偏好过滤
    if risk_profile == '保守型':
        filtered = [s for s in filtered if s['risk_level'] == '低'][:5]
    elif risk_profile == '稳健型':
        filtered = [s for s in filtered if s['risk_level'] in ['低', '中等']][:8]
    else: # 激进型
        filtered = filtered[:10]
    
    return filtered

@staticmethod
def analyze_stock_potential(stock):
    """分析股票潜力"""
    score = 0
    reasons = []
    
    # ROE评分
    if stock['roe'] >= 20:
        score += 30
        reasons.append(f"ROE {stock['roe']}%，盈利能力优秀")
    elif stock['roe'] >= 15:
        score += 20
        reasons.append(f"ROE {stock['roe']}%，盈利能力良好")
    
    # PE评分
    if stock['pe'] < 20:
        score += 25
        reasons.append(f"PE {stock['pe']}，估值偏低")
    elif stock['pe'] < 30:
        score += 15
        reasons.append(f"PE {stock['pe']}，估值合理")
    
    # 趋势评分
    if stock['trend'] == '上升':
        score += 25
        reasons.append(f"趋势向上，技术面良好")
    elif stock['trend'] == '横盘':
        score += 15
        reasons.append(f"趋势横盘，等待突破")
    
    # 风险评分
    if stock['risk_level'] == '低':
        score += 20
        reasons.append("风险等级低，适合稳健投资")
    elif stock['risk_level'] == '中等':
        score += 10
        reasons.append("风险等级中等")
    
    # 评级
    if score >= 80:
        rating = '强烈推荐'
    elif score >= 60:
        rating = '推荐'
    elif score >= 40:
        rating = '关注'
    else:
        rating = '谨慎'
    
    return {
        'score': score,
        'rating': rating,
        'reasons': reasons
    }

@staticmethod
def get_sector_list():
    """获取板块列表"""
    sectors = set()
    for stock in HOT_STOCKS:
        sectors.add(stock['sector'])
    return sorted(list(sectors))

@staticmethod
def get_risk_levels():
    """获取风险等级列表"""
    return ['低', '中等', '高']

# ==================== 模拟炒股API ====================

@app.route('/api/trading/portfolio', methods=['GET'])
def get_portfolio():
    """获取当前持仓组合"""
    global investment_assistant, trading_account
    
    # 获取当前股票价格
    current_prices = {}
    if investment_assistant and investment_assistant.stock_data:
        for stock_name, data in investment_assistant.stock_data.items():
            current_prices[stock_name] = data.get('current_price', 0)
    
    # 获取持仓信息
    portfolio = trading_account.get_portfolio(current_prices)
    
    return jsonify({
        'status': 'success',
        'data': portfolio
    })

@app.route('/api/trading/buy', methods=['POST'])
def buy_stock():
    """买入股票"""
    global trading_account
    
    data = request.json
    stock_name = data.get('stock_name')
    price = float(data.get('price', 0))
    quantity = int(data.get('quantity', 0))
    
    if not stock_name or price <= 0 or quantity <= 0:
        return jsonify({
            'status': 'error',
            'message': '参数错误'
        })
    
    result = trading_account.buy_stock(stock_name, price, quantity)
    total_amount = price * quantity
    
    if result['success']:
        data_storage.log_trade(
            trade_type='buy',
            stock_name=stock_name,
            price=price,
            quantity=quantity,
            total_amount=total_amount,
            balance_after=result['balance']
        )
        
        data_storage.log_operation(
            operation_type='buy',
            module='模拟交易',
            description=f'买入 {stock_name} {quantity}股 @ ¥{price}',
            details={'stock_name': stock_name, 'price': price, 'quantity': quantity, 'total': total_amount}
        )
        
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'balance': result['balance']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': result['message']
        })

@app.route('/api/trading/sell', methods=['POST'])
def sell_stock():
    """卖出股票"""
    global trading_account
    
    data = request.json
    stock_name = data.get('stock_name')
    price = float(data.get('price', 0))
    quantity = int(data.get('quantity', 0))
    
    if not stock_name or price <= 0 or quantity <= 0:
        return jsonify({
            'status': 'error',
            'message': '参数错误'
        })
    
    result = trading_account.sell_stock(stock_name, price, quantity)
    total_revenue = price * quantity
    
    if result['success']:
        data_storage.log_trade(
            trade_type='sell',
            stock_name=stock_name,
            price=price,
            quantity=quantity,
            total_amount=total_revenue,
            profit=result.get('profit', 0),
            balance_after=result['balance']
        )
        
        data_storage.log_operation(
            operation_type='sell',
            module='模拟交易',
            description=f'卖出 {stock_name} {quantity}股 @ ¥{price}',
            details={'stock_name': stock_name, 'price': price, 'quantity': quantity, 'total': total_revenue}
        )
        
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'balance': result['balance']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': result['message']
        })

@app.route('/api/trading/history', methods=['GET'])
def get_transaction_history():
    """获取交易历史"""
    global trading_account
    
    history = trading_account.get_transaction_history()
    
    return jsonify({
        'status': 'success',
        'data': history
    })

@app.route('/api/trading/reset', methods=['POST'])
def reset_trading_account():
    """重置模拟账户"""
    global trading_account
    
    trading_account.reset_account()
    
    return jsonify({
        'status': 'success',
        'message': '账户已重置',
        'balance': trading_account.balance
    })

@app.route('/api/realtime_quotes', methods=['POST'])
def get_realtime_quotes():
    """获取实时股票行情"""
    data = request.json
    stocks = data.get('stocks', [])
    
    if not stocks:
        stocks = list(current_stock_config.keys())
    
    quotes = []
    for name in stocks:
        if name not in current_stock_config:
            continue
        
        config = current_stock_config[name]
        symbol = config['symbol']
        
        try:
            if symbol.endswith('.SZ'):
                market = 'sz'
                code = symbol.replace('.SZ', '')
            else:
                market = 'sh'
                code = symbol.replace('.SS', '')
            
            url = f"http://hq.sinajs.cn/list={market}{code}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://finance.sina.com.cn/"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                content = response.text
                if '"' in content:
                    data_str = content.split('"')[1]
                    if data_str and len(data_str.split(',')) > 30:
                        parts = data_str.split(',')
                        current_price = float(parts[3]) if parts[3] else 0
                        open_price = float(parts[1]) if parts[1] else current_price
                        high_price = float(parts[4]) if parts[4] else current_price
                        low_price = float(parts[5]) if parts[5] else current_price
                        volume = float(parts[8]) if parts[8] else 0
                        amount = float(parts[9]) if parts[9] else 0
                        prev_close = float(parts[2]) if parts[2] else current_price
                        
                        change = current_price - prev_close
                        change_percent = (change / prev_close * 100) if prev_close > 0 else 0
                        
                        quotes.append({
                            'name': name,
                            'symbol': symbol,
                            'current_price': round(current_price, 2),
                            'open_price': round(open_price, 2),
                            'high_price': round(high_price, 2),
                            'low_price': round(low_price, 2),
                            'prev_close': round(prev_close, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'volume': int(volume),
                            'amount': amount,
                            'sector': config.get('sector', '未知'),
                            'risk_level': config.get('risk_level', '中等'),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'is_realtime': True
                        })
                        continue
        except Exception as e:
            print(f"获取 {name} 实时数据失败: {e}")
        
        import random
        base_price = random.uniform(10, 150)
        change_percent = random.uniform(-5, 5)
        quotes.append({
            'name': name,
            'symbol': symbol,
            'current_price': round(base_price * (1 + change_percent/100), 2),
            'open_price': round(base_price, 2),
            'high_price': round(base_price * 1.03, 2),
            'low_price': round(base_price * 0.97, 2),
            'prev_close': round(base_price, 2),
            'change': round(base_price * change_percent/100, 2),
            'change_percent': round(change_percent, 2),
            'volume': random.randint(10000, 1000000),
            'amount': random.uniform(1000000, 10000000),
            'sector': config.get('sector', '未知'),
            'risk_level': config.get('risk_level', '中等'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_realtime': False
        })
    
    return jsonify({
        'status': 'success',
        'data': quotes,
        'count': len(quotes)
    })

@app.route('/api/stock_pool', methods=['GET'])
def get_stock_pool():
    """获取热门股票池"""
    return jsonify({
        'status': 'success',
        'data': HOT_STOCKS
    })

@app.route('/api/selection_strategies', methods=['GET'])
def get_selection_strategies():
    """获取选股策略列表"""
    return jsonify({
        'status': 'success',
        'data': SELECTION_STRATEGIES
    })

@app.route('/api/select_stocks', methods=['POST'])
def select_stocks():
    """智能选股"""
    data = request.json
    strategy_id = data.get('strategy', 'balanced')
    risk_profile = data.get('risk_profile', '稳健型')
    sector_filter = data.get('sector', None)
    count = data.get('count', 5)
    
    stocks = HOT_STOCKS.copy()
    
    if sector_filter and sector_filter != '全部':
        stocks = [s for s in stocks if s['sector'] == sector_filter]
    
    selected = apply_selection_strategy(stocks, strategy_id, risk_profile)
    
    result = []
    for stock in selected[:count]:
        analysis = analyze_stock_potential(stock)
        result.append({
            **stock,
            'potential_score': analysis['score'],
            'rating': analysis['rating'],
            'reasons': analysis['reasons']
        })
    
    data_storage.log_selection(
        strategy=strategy_id,
        sector=sector_filter or '全部',
        results=result
    )
    
    data_storage.log_operation(
        operation_type='select_stocks',
        module='智能选股',
        description=f'执行{SELECTION_STRATEGIES.get(strategy_id, {}).get("name", strategy_id)}策略，选出{len(result)}只股票',
        details={'strategy': strategy_id, 'sector': sector_filter, 'count': len(result)}
    )
    
    return jsonify({
        'status': 'success',
        'data': result,
        'strategy': strategy_id,
        'count': len(result)
    })

@app.route('/api/sectors', methods=['GET'])
def get_sectors():
    """获取板块列表"""
    return jsonify({
        'status': 'success',
        'data': get_sector_list()
    })

# ==================== 政策消息分析 ====================

POLICY_NEWS = [
    {
        'id': 1,
        'type': 'policy',
        'title': '央行宣布降准0.5个百分点',
        'source': '中国人民银行',
        'date': '2026-04-13',
        'importance': 'high',
        'summary': '为支持实体经济发展，降低社会融资成本，中国人民银行决定下调金融机构存款准备金率0.5个百分点。',
        'impact_sectors': ['银行', '证券', '保险', '房地产'],
        'sentiment': 'positive',
        'analysis': '降准将释放约1.2万亿元长期资金，利好银行、券商等金融板块，对房地产也有一定支撑作用。'
    },
    {
        'id': 2,
        'type': 'policy',
        'title': '国务院发布新能源汽车产业规划',
        'source': '国务院',
        'date': '2026-04-12',
        'importance': 'high',
        'summary': '到2030年，新能源汽车销量占汽车总销量比重达到40%，公共领域车辆全面电动化。',
        'impact_sectors': ['新能源汽车', '锂电池', '充电桩', '汽车零部件'],
        'sentiment': 'positive',
        'analysis': '政策持续加码新能源汽车产业链，利好宁德时代、比亚迪等龙头企业。'
    },
    {
        'id': 3,
        'type': 'news',
        'title': '美联储暗示年内可能降息',
        'source': '美联储',
        'date': '2026-04-11',
        'importance': 'medium',
        'summary': '美联储会议纪要显示，多数官员认为如果通胀继续放缓，年内降息是合适的。',
        'impact_sectors': ['有色金属', '黄金', '半导体'],
        'sentiment': 'positive',
        'analysis': '美联储降息预期升温，利好大宗商品和成长股，对A股市场情绪有提振作用。'
    },
    {
        'id': 4,
        'type': 'policy',
        'title': '证监会优化IPO审核机制',
        'source': '证监会',
        'date': '2026-04-10',
        'importance': 'medium',
        'summary': '证监会发布新规，优化IPO审核流程，提高审核效率，同时加强信息披露要求。',
        'impact_sectors': ['证券', '创投'],
        'sentiment': 'neutral',
        'analysis': 'IPO审核优化有利于券商投行业务，但需关注市场资金分流影响。'
    },
    {
        'id': 5,
        'type': 'news',
        'title': 'AI大模型应用加速落地',
        'source': '行业资讯',
        'date': '2026-04-09',
        'importance': 'high',
        'summary': '多家科技公司发布AI大模型应用产品，涵盖办公、教育、医疗等领域，商业化进程加快。',
        'impact_sectors': ['人工智能', '软件服务', '半导体'],
        'sentiment': 'positive',
        'analysis': 'AI应用落地加速，利好科大讯飞、百度等AI概念股，半导体需求也将受益。'
    },
    {
        'id': 6,
        'type': 'policy',
        'title': '多地出台房地产优化政策',
        'source': '地方政府',
        'date': '2026-04-08',
        'importance': 'medium',
        'summary': '多个一二线城市调整限购政策，降低首付比例，支持刚性和改善性住房需求。',
        'impact_sectors': ['房地产', '家电', '建材'],
        'sentiment': 'positive',
        'analysis': '房地产政策持续优化，有助于稳定房地产市场，利好地产链相关板块。'
    },
    {
        'id': 7,
        'type': 'news',
        'title': '光伏行业产能过剩风险加剧',
        'source': '行业研究',
        'date': '2026-04-07',
        'importance': 'medium',
        'summary': '光伏行业产能快速扩张，供需失衡风险上升，部分企业开始降价去库存。',
        'impact_sectors': ['光伏', '新能源'],
        'sentiment': 'negative',
        'analysis': '产能过剩可能导致行业整合加速，短期利空光伏板块，关注龙头企业竞争优势。'
    },
    {
        'id': 8,
        'type': 'policy',
        'title': '医保目录调整方案公布',
        'source': '国家医保局',
        'date': '2026-04-06',
        'importance': 'medium',
        'summary': '新版医保目录调整方案公布，新增多种创新药，谈判药品价格降幅收窄。',
        'impact_sectors': ['医药研发', '医疗器械', '中药'],
        'sentiment': 'positive',
        'analysis': '医保目录调整利好创新药企业，降价幅度收窄有助于保护企业利润。'
    }
]

MARKET_EVENTS = [
    {
        'id': 1,
        'event_type': 'economic',
        'title': '3月CPI同比上涨0.3%',
        'date': '2026-04-10',
        'importance': 'high',
        'actual': '0.3%',
        'forecast': '0.4%',
        'previous': '0.2%',
        'impact': '通胀温和，货币政策空间较大',
        'sentiment': 'neutral'
    },
    {
        'id': 2,
        'event_type': 'economic',
        'title': '3月PMI为51.2%',
        'date': '2026-04-01',
        'importance': 'high',
        'actual': '51.2%',
        'forecast': '50.8%',
        'previous': '50.6%',
        'impact': '制造业景气度回升，经济复苏态势良好',
        'sentiment': 'positive'
    },
    {
        'id': 3,
        'event_type': 'economic',
        'title': '一季度GDP同比增长5.2%',
        'date': '2026-04-15',
        'importance': 'high',
        'actual': '5.2%',
        'forecast': '5.0%',
        'previous': '4.8%',
        'impact': '经济增长超预期，消费和投资双轮驱动',
        'sentiment': 'positive'
    },
    {
        'id': 4,
        'event_type': 'corporate',
        'title': '年报披露高峰期',
        'date': '2026-04-30',
        'importance': 'medium',
        'actual': '--',
        'forecast': '--',
        'previous': '--',
        'impact': '关注业绩超预期个股机会',
        'sentiment': 'neutral'
    }
]

@app.route('/api/policy_news', methods=['GET'])
def get_policy_news():
    """获取政策消息列表"""
    news_type = request.args.get('type', None)
    limit = request.args.get('limit', 10, type=int)
    
    news_list = POLICY_NEWS.copy()
    
    if news_type:
        news_list = [n for n in news_list if n['type'] == news_type]
    
    return jsonify({
        'status': 'success',
        'data': news_list[:limit]
    })

@app.route('/api/market_events', methods=['GET'])
def get_market_events():
    """获取市场事件日历"""
    return jsonify({
        'status': 'success',
        'data': MARKET_EVENTS
    })

@app.route('/api/policy_analysis', methods=['GET'])
def get_policy_analysis():
    """获取政策影响分析"""
    sector = request.args.get('sector', None)
    
    analysis_result = {
        'overall_sentiment': '偏多',
        'sentiment_score': 65,
        'key_policies': [],
        'sector_impact': {},
        'recommendations': []
    }
    
    for news in POLICY_NEWS[:5]:
        if news['importance'] == 'high':
            analysis_result['key_policies'].append({
                'title': news['title'],
                'impact': news['analysis'],
                'sectors': news['impact_sectors']
            })
    
    sector_sentiment = {}
    for news in POLICY_NEWS:
        for s in news['impact_sectors']:
            if s not in sector_sentiment:
                sector_sentiment[s] = {'positive': 0, 'negative': 0, 'neutral': 0}
            sector_sentiment[s][news['sentiment']] += 1
    
    for s, counts in sector_sentiment.items():
        total = sum(counts.values())
        if counts['positive'] > counts['negative']:
            sentiment = '利好'
            score = int(counts['positive'] / total * 100)
        elif counts['negative'] > counts['positive']:
            sentiment = '利空'
            score = -int(counts['negative'] / total * 100)
        else:
            sentiment = '中性'
            score = 50
        
        analysis_result['sector_impact'][s] = {
            'sentiment': sentiment,
            'score': score,
            'news_count': total
        }
    
    analysis_result['recommendations'] = [
        {'sector': '新能源汽车', 'action': '关注', 'reason': '政策持续加码，产业链景气度高'},
        {'sector': '人工智能', 'action': '关注', 'reason': 'AI应用加速落地，商业化进程加快'},
        {'sector': '光伏', 'action': '谨慎', 'reason': '产能过剩风险，等待行业整合'},
        {'sector': '银行', 'action': '关注', 'reason': '降准释放流动性，估值修复空间大'}
    ]
    
    if sector and sector in analysis_result['sector_impact']:
        analysis_result['filtered_sector'] = sector
        analysis_result['filtered_impact'] = analysis_result['sector_impact'][sector]
    
    return jsonify({
        'status': 'success',
        'data': analysis_result
    })

# ==================== 历史数据API ====================

import random
import hashlib
from datetime import datetime, timedelta

STOCK_PRICE_CONFIG = {
    '科创信息': {'base_min': 15, 'base_max': 25, 'volatility': 0.04, 'sector': '信息技术'},
    '赛恩斯': {'base_min': 25, 'base_max': 40, 'volatility': 0.03, 'sector': '环保'},
    '景嘉微': {'base_min': 60, 'base_max': 90, 'volatility': 0.05, 'sector': '半导体'},
    '深信服': {'base_min': 80, 'base_max': 120, 'volatility': 0.045, 'sector': '网络安全'},
    '科大讯飞': {'base_min': 35, 'base_max': 55, 'volatility': 0.04, 'sector': '人工智能'},
    '万兴科技': {'base_min': 40, 'base_max': 65, 'volatility': 0.05, 'sector': '软件服务'},
    '威胜信息': {'base_min': 20, 'base_max': 35, 'volatility': 0.03, 'sector': '智能电网'},
    '超图软件': {'base_min': 12, 'base_max': 22, 'volatility': 0.04, 'sector': '地理信息'},
}

def generate_historical_data(stock_name, days=60):
    """生成模拟历史数据 - 根据股票名称生成一致的数据"""
    config = STOCK_PRICE_CONFIG.get(stock_name, {'base_min': 30, 'base_max': 80, 'volatility': 0.04})
    
    seed_value = int(hashlib.md5(stock_name.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed_value)
    
    base_price = rng.uniform(config['base_min'], config['base_max'])
    volatility = config['volatility']
    data = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        change = rng.uniform(-volatility, volatility)
        base_price = base_price * (1 + change)
        
        high = base_price * (1 + rng.uniform(0, 0.02))
        low = base_price * (1 - rng.uniform(0, 0.02))
        open_price = base_price * (1 + rng.uniform(-0.015, 0.015))
        close = base_price
        volume = rng.randint(500000, 8000000)
        
        ma5 = base_price * (1 + rng.uniform(-0.015, 0.015))
        ma10 = base_price * (1 + rng.uniform(-0.025, 0.025))
        ma20 = base_price * (1 + rng.uniform(-0.04, 0.04))
        
        data.append({
            'date': date,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume,
            'ma5': round(ma5, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2)
        })
    
    return data

def calculate_technical_indicators(data):
    """计算技术指标"""
    if len(data) < 2:
        return {}
    
    closes = [d['close'] for d in data]
    highs = [d['high'] for d in data]
    lows = [d['low'] for d in data]
    volumes = [d['volume'] for d in data]
    
    current_price = closes[-1]
    prev_price = closes[-2] if len(closes) > 1 else closes[-0]
    
    sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else sum(closes) / len(closes)
    sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else sum(closes) / len(closes)
    
    highest_20 = max(highs[-20:]) if len(highs) >= 20 else max(highs)
    lowest_20 = min(lows[-20:]) if len(lows) >= 20 else min(lows)
    
    price_position = ((current_price - lowest_20) / (highest_20 - lowest_20) * 100) if highest_20 != lowest_20 else 50
    
    returns = [(closes[i] - closes[i-1]) / closes[i-1] * 100 for i in range(1, len(closes))]
    volatility = (sum(r**2 for r in returns[-20:]) / 20) ** 0.5 if len(returns) >= 20 else 0
    
    avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else sum(volumes) / len(volumes)
    volume_ratio = volumes[-1] / avg_volume if avg_volume > 0 else 1
    
    trend_strength = 0
    if current_price > sma_20 > sma_50:
        trend_strength = min(100, (current_price - sma_20) / sma_20 * 500 + 50)
    elif current_price < sma_20 < sma_50:
        trend_strength = max(0, 50 - (sma_20 - current_price) / sma_20 * 500)
    else:
        trend_strength = 50
    
    momentum = (current_price - closes[-10]) / closes[-10] * 100 if len(closes) >= 10 else 0
    
    rsi_period = 14
    if len(closes) >= rsi_period + 1:
        gains = []
        losses = []
        for i in range(-rsi_period, 0):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        avg_gain = sum(gains) / rsi_period
        avg_loss = sum(losses) / rsi_period
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
    else:
        rsi = 50
    
    macd = None
    signal = None
    if len(closes) >= 26:
        ema_12 = sum(closes[-12:]) / 12
        ema_26 = sum(closes[-26:]) / 26
        macd = ema_12 - ema_26
        signal = macd * 0.8
    
    resistance_1 = current_price * 1.05
    resistance_2 = current_price * 1.10
    support_1 = current_price * 0.95
    support_2 = current_price * 0.90
    
    return {
        'current_price': round(current_price, 2),
        'price_change': round((current_price - prev_price) / prev_price * 100, 2),
        'sma_20': round(sma_20, 2),
        'sma_50': round(sma_50, 2),
        'price_position': round(price_position, 1),
        'volatility': round(volatility, 2),
        'volume_ratio': round(volume_ratio, 2),
        'trend_strength': round(trend_strength, 1),
        'momentum': round(momentum, 2),
        'rsi': round(rsi, 1),
        'macd': round(macd, 4) if macd else None,
        'signal': round(signal, 4) if signal else None,
        'resistance_1': round(resistance_1, 2),
        'resistance_2': round(resistance_2, 2),
        'support_1': round(support_1, 2),
        'support_2': round(support_2, 2),
        'highest_20': round(highest_20, 2),
        'lowest_20': round(lowest_20, 2)
    }

@app.route('/api/history/<stock_name>', methods=['GET'])
def get_stock_history(stock_name):
    """获取股票历史数据"""
    days = request.args.get('days', 60, type=int)
    days = min(days, 365)
    
    historical_data = generate_historical_data(stock_name, days)
    indicators = calculate_technical_indicators(historical_data)
    
    return jsonify({
        'status': 'success',
        'data': {
            'stock_name': stock_name,
            'history': historical_data,
            'indicators': indicators
        }
    })

@app.route('/api/technical_analysis/<stock_name>', methods=['GET'])
def get_technical_analysis(stock_name):
    """获取技术分析结果"""
    days = request.args.get('days', 60, type=int)
    
    config = STOCK_PRICE_CONFIG.get(stock_name, {'base_min': 30, 'base_max': 80, 'volatility': 0.04})
    print(f"DEBUG: stock_name={stock_name}, config={config}")
    
    historical_data = generate_historical_data(stock_name, days)
    print(f"DEBUG: first_close={historical_data[0]['close'] if historical_data else 'N/A'}")
    
    indicators = calculate_technical_indicators(historical_data)
    
    analysis = {
        'trend': '上涨' if indicators['trend_strength'] > 60 else '下跌' if indicators['trend_strength'] < 40 else '震荡',
        'trend_confidence': '高' if abs(indicators['trend_strength'] - 50) > 30 else '中' if abs(indicators['trend_strength'] - 50) > 15 else '低',
        'signal': '买入' if indicators['rsi'] < 30 and indicators['momentum'] > 0 else '卖出' if indicators['rsi'] > 70 and indicators['momentum'] < 0 else '持有',
        'risk_level': '高' if indicators['volatility'] > 3 else '中' if indicators['volatility'] > 1.5 else '低',
        'position_suggestion': '建议加仓' if indicators['price_position'] < 30 and indicators['trend_strength'] > 50 else '建议减仓' if indicators['price_position'] > 70 and indicators['trend_strength'] < 50 else '维持仓位'
    }
    
    return jsonify({
        'status': 'success',
        'data': {
            'stock_name': stock_name,
            'history': historical_data[-30:],
            'indicators': indicators,
            'analysis': analysis,
            'debug_config': config,
            'debug_first_close': historical_data[0]['close'] if historical_data else None
        }
    })

@app.route('/api/stocks/search', methods=['GET'])
def search_stocks():
    """模糊搜索股票"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({
            'status': 'success',
            'data': []
        })
    
    results = []
    query_lower = query.lower()
    
    for stock in HOT_STOCKS:
        name_match = query_lower in stock['name'].lower()
        symbol_match = query_lower in stock['symbol'].lower()
        pinyin_match = False
        
        if name_match or symbol_match or pinyin_match:
            results.append({
                'name': stock['name'],
                'symbol': stock['symbol'],
                'sector': stock['sector'],
                'risk_level': stock['risk_level']
            })
    
    for name, config in current_stock_config.items():
        if name not in [s['name'] for s in results]:
            name_match = query_lower in name.lower()
            symbol_match = query_lower in config['symbol'].lower()
            
            if name_match or symbol_match:
                results.append({
                    'name': name,
                    'symbol': config['symbol'],
                    'sector': config['sector'],
                    'risk_level': config['risk_level']
                })
    
    return jsonify({
        'status': 'success',
        'data': results[:10]
    })

# ==================== 数据存储API ====================

@app.route('/api/history/operations', methods=['GET'])
def get_operation_history():
    """获取操作历史"""
    limit = request.args.get('limit', 50, type=int)
    module = request.args.get('module', None)
    
    operations = data_storage.get_recent_operations(limit=limit, module=module)
    
    for op in operations:
        if op.get('details'):
            try:
                op['details'] = json.loads(op['details'])
            except:
                pass
        if op.get('created_at'):
            op['created_at'] = op['created_at']
    
    return jsonify({
        'status': 'success',
        'data': operations
    })

@app.route('/api/history/trades', methods=['GET'])
def get_trade_history():
    """获取交易历史"""
    limit = request.args.get('limit', 50, type=int)
    
    trades = data_storage.get_recent_trades(limit=limit)
    
    return jsonify({
        'status': 'success',
        'data': trades
    })

@app.route('/api/history/analyses', methods=['GET'])
def get_analysis_history():
    """获取分析历史"""
    limit = request.args.get('limit', 20, type=int)
    
    analyses = data_storage.get_recent_analyses(limit=limit)
    
    return jsonify({
        'status': 'success',
        'data': analyses
    })

@app.route('/api/history/selections', methods=['GET'])
def get_selection_history():
    """获取选股历史"""
    limit = request.args.get('limit', 20, type=int)
    
    selections = data_storage.get_recent_selections(limit=limit)
    
    return jsonify({
        'status': 'success',
        'data': selections
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    stats = data_storage.get_statistics()
    
    return jsonify({
        'status': 'success',
        'data': stats
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """清理历史记录"""
    days = request.json.get('days', 30)
    
    cleared = data_storage.clear_old_records(days=days)
    
    return jsonify({
        'status': 'success',
        'message': f'已清理 {cleared} 条旧记录',
        'cleared': cleared
    })

if __name__ == '__main__':
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=False, host='0.0.0.0', port=5000)
