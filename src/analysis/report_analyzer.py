#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告分析模块
功能：
1. 生成不同类型的报告（详细报告、摘要报告、PDF报告等）
2. 支持不同格式的输出（JSON、CSV、PDF等）
3. 提供报告模板和定制化选项
4. 整合系统各层级的信息，生成全面的分析报告
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from fpdf import FPDF

class ReportAnalyzer:
    """报告分析器"""
    
    def __init__(self, enhanced_dikw_assistant):
        """
        初始化报告分析器
        
        Args:
            enhanced_dikw_assistant: 增强版DIKW投资助手实例
        """
        self.assistant = enhanced_dikw_assistant
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_report(self, report_type: str = "complete", output_format: str = "json") -> str:
        """
        生成报告
        
        Args:
            report_type: 报告类型 (complete, summary, technical, portfolio, risk)
            output_format: 输出格式 (json, csv)
            
        Returns:
            生成的报告文件路径
        """
        print(f"\n📋 正在生成{self._get_report_type_name(report_type)}...")
        
        # 确保有完整的报告数据
        if not hasattr(self.assistant, 'stock_data') or not self.assistant.stock_data:
            self.assistant.generate_complete_report()
        
        # 生成报告数据
        report_data = self._generate_report_data(report_type)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.reports_dir}/stock_report_{report_type}_{timestamp}.{output_format}"
        
        # 根据格式输出
        if output_format == "json":
            self._save_json_report(report_data, filename)
        elif output_format == "csv":
            self._save_csv_report(report_data, filename)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        print(f"✅ 报告已生成: {filename}")
        return filename
    
    def _get_report_type_name(self, report_type: str) -> str:
        """获取报告类型的中文名称"""
        type_names = {
            "complete": "完整报告",
            "summary": "摘要报告",
            "technical": "技术分析报告",
            "portfolio": "投资组合报告",
            "risk": "风险分析报告"
        }
        return type_names.get(report_type, report_type)
    
    def _generate_report_data(self, report_type: str) -> Dict:
        """生成报告数据"""
        if report_type == "complete":
            return self.assistant.generate_complete_report()
        elif report_type == "summary":
            return self._generate_summary_report()
        elif report_type == "technical":
            return self._generate_technical_report()
        elif report_type == "portfolio":
            return self._generate_portfolio_report()
        elif report_type == "risk":
            return self._generate_risk_report()
        else:
            raise ValueError(f"不支持的报告类型: {report_type}")
    
    def _generate_summary_report(self) -> Dict:
        """生成摘要报告"""
        return {
            "report_metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "report_type": "summary",
                "user_profile": self.assistant.user_risk_profile,
                "investment_amount": self.assistant.investment_amount
            },
            "market_overview": {
                "market_trend": self.assistant.market_analysis.get('market_sentiment', {}).get('market_trend', '未知'),
                "rising_count": self.assistant.market_analysis.get('market_sentiment', {}).get('rising_count', 0),
                "falling_count": self.assistant.market_analysis.get('market_sentiment', {}).get('falling_count', 0),
                "average_change": self.assistant.market_analysis.get('market_sentiment', {}).get('average_change', 0)
            },
            "top_sectors": self.assistant.market_analysis.get('sector_analysis', {}).get('sector_ranking', [])[:3],
            "portfolio_summary": {
                "total_investment": self.assistant.investment_amount,
                "allocated_stocks": len(self.assistant.investment_knowledge.get('portfolio_allocation', {})),
                "sharpe_ratio": self.assistant.investment_knowledge.get('optimized_portfolio', {}).get('sharpe_ratio', 0),
                "expected_return": self.assistant.investment_knowledge.get('optimized_portfolio', {}).get('expected_return', 0) * 100
            },
            "timing_recommendation": {
                "signal": self.assistant.investment_wisdom.get('timing_recommendations', {}).get('overall_signal', '未知'),
                "action": self.assistant.investment_wisdom.get('timing_recommendations', {}).get('action', '未知'),
                "confidence": self.assistant.investment_wisdom.get('timing_recommendations', {}).get('confidence', '中')
            },
            "risk_analysis": {
                "risk_level": self.assistant.investment_knowledge.get('risk_analysis', {}).get('risk_level', '未知'),
                "var_95": self.assistant.investment_knowledge.get('risk_analysis', {}).get('var', {}).get('var_95', 0),
                "risk_alerts": len(self.assistant.investment_wisdom.get('dynamic_risk_control', {}).get('risk_alerts', []))
            },
            "immediate_actions": self.assistant.investment_wisdom.get('personalized_advice', {}).get('immediate_actions', [])
        }
    
    def _generate_technical_report(self) -> Dict:
        """生成技术分析报告"""
        technical_data = {}
        for stock_name, tech_analysis in self.assistant.market_analysis.get('technical_analysis', {}).items():
            technical_data[stock_name] = {
                "current_price": self.assistant.stock_data.get(stock_name, {}).get('current_price', 0),
                "change_percent": self.assistant.stock_data.get(stock_name, {}).get('change_percent', 0),
                "technical_score": tech_analysis.get('technical_score', {}).get('score', 50),
                "trend": tech_analysis.get('trend', '未知'),
                "macd": tech_analysis.get('macd', {}),
                "kdj": tech_analysis.get('kdj', {}),
                "rsi": tech_analysis.get('rsi', {}),
                "bollinger": tech_analysis.get('bollinger', {})
            }
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "report_type": "technical",
                "stocks_analyzed": len(technical_data)
            },
            "technical_analysis": technical_data
        }
    
    def _generate_portfolio_report(self) -> Dict:
        """生成投资组合报告"""
        portfolio = self.assistant.investment_knowledge.get('portfolio_allocation', {})
        optimized = self.assistant.investment_knowledge.get('optimized_portfolio', {})
        
        portfolio_data = []
        total_invested = 0
        for stock_name, alloc in portfolio.items():
            investment = alloc.get('investment_amount', 0)
            total_invested += investment
            portfolio_data.append({
                "stock_name": stock_name,
                "sector": alloc.get('sector', '未知'),
                "weight_percent": alloc.get('weight_percent', 0),
                "investment_amount": investment,
                "shares": alloc.get('shares', 0),
                "price": alloc.get('price', 0)
            })
        
        cash_reserve = self.assistant.investment_amount - total_invested
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "report_type": "portfolio",
                "user_profile": self.assistant.user_risk_profile,
                "total_investment": self.assistant.investment_amount
            },
            "portfolio_summary": {
                "total_invested": total_invested,
                "cash_reserve": cash_reserve,
                "cash_percent": (cash_reserve / self.assistant.investment_amount) * 100,
                "sharpe_ratio": optimized.get('sharpe_ratio', 0),
                "expected_return": optimized.get('expected_return', 0) * 100,
                "expected_volatility": optimized.get('expected_volatility', 0) * 100
            },
            "portfolio_allocation": portfolio_data,
            "optimization_method": optimized.get('method', '未知')
        }
    
    def _generate_risk_report(self) -> Dict:
        """生成风险分析报告"""
        risk_analysis = self.assistant.investment_knowledge.get('risk_analysis', {})
        dynamic_risk = self.assistant.investment_wisdom.get('dynamic_risk_control', {})
        
        return {
            "report_metadata": {
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "report_type": "risk",
                "user_profile": self.assistant.user_risk_profile
            },
            "risk_summary": {
                "risk_level": risk_analysis.get('risk_level', '未知'),
                "var_95": risk_analysis.get('var', {}).get('var_95', 0),
                "var_95_percent": risk_analysis.get('var', {}).get('var_95_percent', 0),
                "stress_test_results": risk_analysis.get('stress_test', {})
            },
            "dynamic_risk_control": {
                "position_adjustment": dynamic_risk.get('position_adjustment', {}),
                "risk_alerts": dynamic_risk.get('risk_alerts', []),
                "stock_recommendations": dynamic_risk.get('stock_recommendations', {})
            },
            "risk_control_rules": self.assistant.investment_knowledge.get('risk_control_rules', {})
        }
    
    def _save_json_report(self, data: Dict, filename: str):
        """保存JSON格式报告"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_csv_report(self, data: Dict, filename: str):
        """保存CSV格式报告"""
        # 根据报告类型确定CSV结构
        report_type = data.get('report_metadata', {}).get('report_type', 'unknown')
        
        if report_type == 'portfolio':
            # 投资组合报告
            portfolio_data = data.get('portfolio_allocation', [])
            if portfolio_data:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=portfolio_data[0].keys())
                    writer.writeheader()
                    writer.writerows(portfolio_data)
        elif report_type == 'technical':
            # 技术分析报告
            technical_data = data.get('technical_analysis', {})
            rows = []
            for stock_name, tech_info in technical_data.items():
                row = {'stock_name': stock_name}
                row.update({
                    'current_price': tech_info.get('current_price', 0),
                    'change_percent': tech_info.get('change_percent', 0),
                    'technical_score': tech_info.get('technical_score', 50),
                    'trend': tech_info.get('trend', '未知')
                })
                rows.append(row)
            if rows:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
        else:
            # 其他报告类型，保存摘要信息
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Field', 'Value'])
                writer.writerow(['Report Type', report_type])
                writer.writerow(['Generated At', data.get('report_metadata', {}).get('generated_at', '')])
                writer.writerow(['User Profile', data.get('report_metadata', {}).get('user_profile', '')])
    
    def _save_pdf_report(self, data: Dict, filename: str):
        """保存PDF格式报告"""
        pdf = FPDF()
        pdf.add_page()
        
        # 设置字体 - 使用fpdf默认支持的字体
        pdf.set_font("Arial", 'B', 16)
        
        # 标题
        report_type = data.get('report_metadata', {}).get('report_type', 'unknown')
        title = self._get_report_type_name(report_type)
        # 使用英文标题避免中文编码问题
        pdf.cell(0, 10, f"Stock Investment Analysis {report_type.capitalize()}", 0, 1, 'C')
        
        # 元数据
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 8, f"Generated At: {data.get('report_metadata', {}).get('generated_at', '')}", 0, 1, 'C')
        pdf.cell(0, 8, f"User Profile: {data.get('report_metadata', {}).get('user_profile', 'Unknown')}", 0, 1, 'C')
        pdf.ln(10)
        
        # 内容
        pdf.set_font("Arial", 'B', 12)
        
        if report_type == 'summary':
            self._add_summary_to_pdf(pdf, data)
        elif report_type == 'technical':
            self._add_technical_to_pdf(pdf, data)
        elif report_type == 'portfolio':
            self._add_portfolio_to_pdf(pdf, data)
        elif report_type == 'risk':
            self._add_risk_to_pdf(pdf, data)
        
        # 保存PDF
        pdf.output(filename)
    
    def _add_summary_to_pdf(self, pdf: FPDF, data: Dict):
        """添加摘要内容到PDF"""
        # 市场概况
        pdf.cell(0, 10, "Market Overview", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        market = data.get('market_overview', {})
        pdf.cell(0, 6, f"• Market Trend: {market.get('market_trend', 'Unknown')}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Rise/Fall Ratio: {market.get('rising_count', 0)} up/{market.get('falling_count', 0)} down", 0, 1, 'L')
        pdf.cell(0, 6, f"• Average Change: {market.get('average_change', 0):+.2f}%", 0, 1, 'L')
        pdf.ln(5)
        
        # 板块表现
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Sector Performance", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        for i, sector in enumerate(data.get('top_sectors', [])[:3], 1):
            pdf.cell(0, 6, f"{i}. {sector.get('sector', 'Unknown')}: {sector.get('avg_change', 0):+.2f}% ({sector.get('strength', 'Unknown')})")
        pdf.ln(5)
        
        # 投资组合摘要
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Portfolio Summary", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        portfolio = data.get('portfolio_summary', {})
        pdf.cell(0, 6, f"• Total Investment: ¥{portfolio.get('total_investment', 0):,.0f}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Allocated Stocks: {portfolio.get('allocated_stocks', 0)}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Sharpe Ratio: {portfolio.get('sharpe_ratio', 0):.3f}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Expected Return: {portfolio.get('expected_return', 0):.2f}%", 0, 1, 'L')
        pdf.ln(5)
        
        # 择时建议
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Timing Recommendation", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        timing = data.get('timing_recommendation', {})
        pdf.cell(0, 6, f"• Signal: {timing.get('signal', 'Unknown')}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Recommended Action: {timing.get('action', 'Unknown')}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Confidence: {timing.get('confidence', 'Medium')}", 0, 1, 'L')
        pdf.ln(5)
        
        # 立即行动建议
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Immediate Actions", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        for i, action in enumerate(data.get('immediate_actions', [])[:3], 1):
            # 尝试将中文行动建议转换为英文
            action_en = action
            if '择时信号' in action:
                action_en = "Consider building or increasing positions based on timing signals"
            elif '技术指标' in action:
                action_en = "Set price alert monitoring based on technical indicators"
            elif '准备投资资金' in action:
                action_en = "Prepare investment funds and enter the market in batches according to plan"
            pdf.cell(0, 6, f"{i}. {action_en}", 0, 1, 'L')
    
    def _add_technical_to_pdf(self, pdf: FPDF, data: Dict):
        """添加技术分析内容到PDF"""
        technical_data = data.get('technical_analysis', {})
        for stock_name, tech_info in technical_data.items():
            pdf.cell(0, 10, f"{stock_name}", 0, 1, 'L')
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 6, f"• Current Price: ¥{tech_info.get('current_price', 0):.2f}", 0, 1, 'L')
            pdf.cell(0, 6, f"• Change: {tech_info.get('change_percent', 0):+.2f}%", 0, 1, 'L')
            pdf.cell(0, 6, f"• Technical Score: {tech_info.get('technical_score', 50)}", 0, 1, 'L')
            pdf.cell(0, 6, f"• Trend: {tech_info.get('trend', 'Unknown')}", 0, 1, 'L')
            pdf.set_font("Arial", 'B', 12)
            pdf.ln(5)
    
    def _add_portfolio_to_pdf(self, pdf: FPDF, data: Dict):
        """添加投资组合内容到PDF"""
        # 投资组合摘要
        summary = data.get('portfolio_summary', {})
        pdf.cell(0, 10, "Portfolio Summary", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"• Total Investment: ¥{data.get('report_metadata', {}).get('total_investment', 0):,.0f}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Invested: ¥{summary.get('total_invested', 0):,.0f}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Cash Reserve: ¥{summary.get('cash_reserve', 0):,.0f} ({summary.get('cash_percent', 0):.1f}%)", 0, 1, 'L')
        pdf.cell(0, 6, f"• Sharpe Ratio: {summary.get('sharpe_ratio', 0):.3f}", 0, 1, 'L')
        pdf.cell(0, 6, f"• Expected Return: {summary.get('expected_return', 0):.2f}%", 0, 1, 'L')
        pdf.cell(0, 6, f"• Expected Volatility: {summary.get('expected_volatility', 0):.2f}%", 0, 1, 'L')
        pdf.ln(5)
        
        # 投资组合分配
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Portfolio Allocation", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        for alloc in data.get('portfolio_allocation', []):
            pdf.cell(0, 6, f"• {alloc.get('stock_name', 'Unknown')} ({alloc.get('sector', 'Unknown')}): {alloc.get('weight_percent', 0):.1f}% (¥{alloc.get('investment_amount', 0):.0f})", 0, 1, 'L')
    
    def _add_risk_to_pdf(self, pdf: FPDF, data: Dict):
        """添加风险分析内容到PDF"""
        # 风险摘要
        summary = data.get('risk_summary', {})
        pdf.cell(0, 10, "Risk Summary", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 6, f"• Risk Level: {summary.get('risk_level', 'Unknown')}", 0, 1, 'L')
        pdf.cell(0, 6, f"• VaR(95%): ¥{summary.get('var_95', 0):.2f} ({summary.get('var_95_percent', 0):.2f}%)", 0, 1, 'L')
        pdf.ln(5)
        
        # 风险预警
        pdf.set_font("Arial", 'B', 12)
        risk_alerts = data.get('dynamic_risk_control', {}).get('risk_alerts', [])
        pdf.cell(0, 10, f"Risk Alerts ({len(risk_alerts)} items)", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        for alert in risk_alerts[:5]:  # 只显示前5个预警
            # 尝试将中文预警转换为英文
            alert_en = alert
            if '风险' in alert:
                alert_en = "Risk alert: " + alert
            pdf.cell(0, 6, f"• {alert_en}", 0, 1, 'L')
        pdf.ln(5)
        
        # 风险控制规则
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Risk Control Rules", 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        rules = data.get('risk_control_rules', {})
        position_limits = rules.get('position_limits', {})
        pdf.cell(0, 6, f"• Max Single Stock Position: {position_limits.get('max_single_stock', 0)}%", 0, 1, 'L')
        pdf.cell(0, 6, f"• Max Single Sector Position: {position_limits.get('max_single_sector', 0)}%", 0, 1, 'L')
        pdf.cell(0, 6, f"• Cash Reserve: {position_limits.get('cash_reserve', 0)}%", 0, 1, 'L')
    
    def generate_all_reports(self, formats: List[str] = None) -> List[str]:
        """
        生成所有类型的报告
        
        Args:
            formats: 输出格式列表，默认包含json和pdf
            
        Returns:
            生成的报告文件路径列表
        """
        if formats is None:
            formats = ["json", "pdf"]
        
        report_types = ["complete", "summary", "technical", "portfolio", "risk"]
        generated_files = []
        
        for report_type in report_types:
            for fmt in formats:
                try:
                    file_path = self.generate_report(report_type, fmt)
                    generated_files.append(file_path)
                except Exception as e:
                    print(f"生成{self._get_report_type_name(report_type)}({fmt})失败: {str(e)}")
        
        return generated_files

# 使用示例
if __name__ == "__main__":
    # 导入增强版DIKW投资助手
    from stock_investment_assistant_v2 import EnhancedDIKWStockAssistant
    
    # 创建投资助手实例
    assistant = EnhancedDIKWStockAssistant(
        user_risk_profile="稳健型",
        investment_amount=100000
    )
    
    # 生成完整报告
    assistant.generate_complete_report()
    
    # 创建报告分析器
    report_analyzer = ReportAnalyzer(assistant)
    
    # 生成摘要报告（PDF格式）
    report_analyzer.generate_report("summary", "pdf")
    
    # 生成技术分析报告（JSON格式）
    report_analyzer.generate_report("technical", "json")
    
    # 生成投资组合报告（CSV格式）
    report_analyzer.generate_report("portfolio", "csv")
    
    # 生成风险分析报告（PDF格式）
    report_analyzer.generate_report("risk", "pdf")
    
    print("\n✅ 所有报告生成完成!")
