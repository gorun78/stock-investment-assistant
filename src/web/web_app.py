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

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.stock_investment_assistant_v2 import EnhancedDIKWStockAssistant, STOCK_CONFIG

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
investment_assistant = None

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
    
    # 创建投资助手实例
    investment_assistant = EnhancedDIKWStockAssistant(
        user_risk_profile=risk_profile,
        investment_amount=investment_amount
    )
    
    return jsonify({
        'status': 'success',
        'message': f'配置成功：{risk_profile} | ¥{investment_amount:,.0f}'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """执行分析"""
    global investment_assistant
    
    if not investment_assistant:
        return jsonify({
            'status': 'error',
            'message': '请先配置投资参数'
        })
    
    try:
        # 生成完整报告
        report = investment_assistant.generate_complete_report()
        
        # 提取摘要信息
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
    
    if not investment_assistant:
        return jsonify({
            'status': 'error',
            'message': '请先配置投资参数'
        })
    
    return jsonify({
        'status': 'success',
        'data': investment_assistant.stock_data
    })

@app.route('/api/generate_reports', methods=['POST'])
def generate_reports():
    """生成报告"""
    global investment_assistant
    
    if not investment_assistant:
        return jsonify({
            'status': 'error',
            'message': '请先配置投资参数'
        })
    
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
    
    if not investment_assistant:
        return jsonify({
            'status': 'error',
            'message': '请先配置投资参数'
        })
    
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
    
    if result['success']:
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
    
    if result['success']:
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
    
    # 获取股票池
    stocks = HOT_STOCKS.copy()
    
    # 板块过滤
    if sector_filter and sector_filter != '全部':
        stocks = [s for s in stocks if s['sector'] == sector_filter]
    
    # 应用选股策略
    selected = apply_selection_strategy(stocks, strategy_id, risk_profile)
    
    # 分析每只股票的潜力
    result = []
    for stock in selected[:count]:
        analysis = analyze_stock_potential(stock)
        result.append({
            **stock,
            'potential_score': analysis['score'],
            'rating': analysis['rating'],
            'reasons': analysis['reasons']
        })
    
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

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)
