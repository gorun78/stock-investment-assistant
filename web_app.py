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
from stock_investment_assistant_v2 import EnhancedDIKWStockAssistant

# 设置系统编码为UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 确保reports目录存在
if not os.path.exists('reports'):
    os.makedirs('reports')

# 全局变量，存储投资助手实例
investment_assistant = None

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
    file_path = os.path.join('reports', filename)
    
    if not os.path.exists(file_path):
        return jsonify({
            'status': 'error',
            'message': '文件不存在'
        })
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)
