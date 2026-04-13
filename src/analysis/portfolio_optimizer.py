#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资组合优化模块
包含均值-方差优化、风险平价模型等投资组合优化算法
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')


class PortfolioOptimizer:
    """投资组合优化器"""
    
    def __init__(self, risk_free_rate: float = 0.03):
        """
        初始化投资组合优化器
        
        Args:
            risk_free_rate: 无风险利率（年化）
        """
        self.risk_free_rate = risk_free_rate
    
    def optimize_portfolio(self, stock_data: Dict, method: str = 'mean_variance', 
                          risk_profile: str = '稳健型') -> Dict:
        """
        优化投资组合
        
        Args:
            stock_data: 股票数据字典
            method: 优化方法（mean_variance, risk_parity, equal_weight）
            risk_profile: 风险偏好（激进型, 稳健型, 保守型）
        
        Returns:
            优化后的投资组合
        """
        if method == 'mean_variance':
            return self._optimize_mean_variance(stock_data, risk_profile)
        elif method == 'risk_parity':
            return self._optimize_risk_parity(stock_data)
        elif method == 'equal_weight':
            return self._optimize_equal_weight(stock_data)
        else:
            return self._optimize_mean_variance(stock_data, risk_profile)
    
    def _optimize_mean_variance(self, stock_data: Dict, risk_profile: str) -> Dict:
        """
        均值-方差优化
        
        Args:
            stock_data: 股票数据字典
            risk_profile: 风险偏好
        
        Returns:
            优化后的权重
        """
        # 提取股票名称
        stocks = list(stock_data.keys())
        n_stocks = len(stocks)
        
        if n_stocks == 0:
            return {'weights': {}, 'method': 'mean_variance', 'status': 'failed'}
        
        # 估算预期收益率和协方差矩阵
        expected_returns = self._estimate_returns(stock_data)
        cov_matrix = self._estimate_covariance(stock_data)
        
        # 根据风险偏好设置目标
        if risk_profile == '激进型':
            # 最大化收益
            target_return = None
            max_risk = 0.25
        elif risk_profile == '保守型':
            # 最小化风险
            target_return = 0.05
            max_risk = 0.10
        else:  # 稳健型
            # 最大化夏普比率
            target_return = None
            max_risk = 0.15
        
        # 优化权重
        try:
            if target_return:
                # 最小化风险
                result = self._minimize_risk(expected_returns, cov_matrix, target_return)
            else:
                # 最大化夏普比率
                result = self._maximize_sharpe(expected_returns, cov_matrix, max_risk)
            
            weights = result['weights']
            
            # 构建权重字典
            weight_dict = {}
            for i, stock in enumerate(stocks):
                weight_dict[stock] = weights[i] * 100
            
            return {
                'weights': weight_dict,
                'method': 'mean_variance',
                'expected_return': result['expected_return'],
                'volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio'],
                'status': 'success'
            }
        
        except Exception as e:
            # 优化失败，使用等权重
            return self._optimize_equal_weight(stock_data)
    
    def _optimize_risk_parity(self, stock_data: Dict) -> Dict:
        """
        风险平价优化
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            优化后的权重
        """
        stocks = list(stock_data.keys())
        n_stocks = len(stocks)
        
        if n_stocks == 0:
            return {'weights': {}, 'method': 'risk_parity', 'status': 'failed'}
        
        # 估算协方差矩阵
        cov_matrix = self._estimate_covariance(stock_data)
        
        # 目标：每个资产的风险贡献相等
        def risk_parity_objective(weights):
            # 计算组合波动率
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # 计算每个资产的风险贡献
            marginal_contrib = np.dot(cov_matrix, weights)
            risk_contrib = np.multiply(weights, marginal_contrib) / portfolio_vol
            
            # 目标：最小化风险贡献的差异
            target_risk = portfolio_vol / n_stocks
            return np.sum((risk_contrib - target_risk) ** 2)
        
        # 约束条件
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0.01, 1) for _ in range(n_stocks))
        
        # 初始权重
        initial_weights = np.ones(n_stocks) / n_stocks
        
        # 优化
        try:
            result = minimize(
                risk_parity_objective,
                initial_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            
            weights = result.x
            
            # 构建权重字典
            weight_dict = {}
            for i, stock in enumerate(stocks):
                weight_dict[stock] = weights[i] * 100
            
            # 计算组合指标
            expected_returns = self._estimate_returns(stock_data)
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
            
            return {
                'weights': weight_dict,
                'method': 'risk_parity',
                'expected_return': portfolio_return,
                'volatility': portfolio_vol,
                'sharpe_ratio': sharpe_ratio,
                'status': 'success'
            }
        
        except Exception as e:
            return self._optimize_equal_weight(stock_data)
    
    def _optimize_equal_weight(self, stock_data: Dict) -> Dict:
        """
        等权重优化
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            等权重配置
        """
        stocks = list(stock_data.keys())
        n_stocks = len(stocks)
        
        if n_stocks == 0:
            return {'weights': {}, 'method': 'equal_weight', 'status': 'failed'}
        
        # 等权重
        weight = 100 / n_stocks
        weight_dict = {stock: weight for stock in stocks}
        
        # 计算组合指标
        expected_returns = self._estimate_returns(stock_data)
        cov_matrix = self._estimate_covariance(stock_data)
        
        weights = np.ones(n_stocks) / n_stocks
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        return {
            'weights': weight_dict,
            'method': 'equal_weight',
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'status': 'success'
        }
    
    def _estimate_returns(self, stock_data: Dict) -> np.ndarray:
        """
        估算预期收益率
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            预期收益率数组
        """
        returns = []
        for name, data in stock_data.items():
            # 使用当日涨跌幅作为预期收益率的简化估算
            daily_return = data.get('change_percent', 0) / 100
            
            # 年化（假设一年250个交易日）
            annual_return = daily_return * 250
            
            # 限制范围
            annual_return = max(-0.5, min(0.5, annual_return))
            
            returns.append(annual_return)
        
        return np.array(returns)
    
    def _estimate_covariance(self, stock_data: Dict) -> np.ndarray:
        """
        估算协方差矩阵
        
        Args:
            stock_data: 股票数据字典
        
        Returns:
            协方差矩阵
        """
        n_stocks = len(stock_data)
        
        # 简化版协方差矩阵估算
        # 基于当日波动率
        volatilities = []
        for name, data in stock_data.items():
            if data.get('open_price', 0) > 0:
                daily_vol = abs(data.get('high_price', 0) - data.get('low_price', 0)) / data.get('open_price', 1)
            else:
                daily_vol = 0.02  # 默认2%日波动率
            
            # 年化波动率
            annual_vol = daily_vol * np.sqrt(250)
            volatilities.append(annual_vol)
        
        volatilities = np.array(volatilities)
        
        # 构建协方差矩阵
        # 假设股票间相关性为0.3
        correlation = 0.3
        cov_matrix = np.outer(volatilities, volatilities) * correlation
        
        # 对角线为方差
        for i in range(n_stocks):
            cov_matrix[i, i] = volatilities[i] ** 2
        
        return cov_matrix
    
    def _maximize_sharpe(self, expected_returns: np.ndarray, cov_matrix: np.ndarray, 
                        max_risk: float) -> Dict:
        """
        最大化夏普比率
        
        Args:
            expected_returns: 预期收益率
            cov_matrix: 协方差矩阵
            max_risk: 最大风险
        
        Returns:
            优化结果
        """
        n_stocks = len(expected_returns)
        
        def neg_sharpe_ratio(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            if portfolio_vol == 0:
                return 0
            
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe
        
        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'ineq', 'fun': lambda x: max_risk - np.sqrt(np.dot(x.T, np.dot(cov_matrix, x)))}
        ]
        
        bounds = tuple((0.01, 1) for _ in range(n_stocks))
        initial_weights = np.ones(n_stocks) / n_stocks
        
        result = minimize(
            neg_sharpe_ratio,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        weights = result.x
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        return {
            'weights': weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _minimize_risk(self, expected_returns: np.ndarray, cov_matrix: np.ndarray, 
                      target_return: float) -> Dict:
        """
        最小化风险
        
        Args:
            expected_returns: 预期收益率
            cov_matrix: 协方差矩阵
            target_return: 目标收益率
        
        Returns:
            优化结果
        """
        n_stocks = len(expected_returns)
        
        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        # 约束条件
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.dot(x, expected_returns) - target_return}
        ]
        
        bounds = tuple((0.01, 1) for _ in range(n_stocks))
        initial_weights = np.ones(n_stocks) / n_stocks
        
        result = minimize(
            portfolio_volatility,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )
        
        weights = result.x
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        return {
            'weights': weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio
        }
    
    def generate_efficient_frontier(self, stock_data: Dict, n_points: int = 20) -> Dict:
        """
        生成有效前沿
        
        Args:
            stock_data: 股票数据字典
            n_points: 前沿点数
        
        Returns:
            有效前沿数据
        """
        expected_returns = self._estimate_returns(stock_data)
        cov_matrix = self._estimate_covariance(stock_data)
        
        # 计算最小和最大收益率
        min_return = min(expected_returns)
        max_return = max(expected_returns)
        
        # 生成目标收益率序列
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier = []
        for target_return in target_returns:
            try:
                result = self._minimize_risk(expected_returns, cov_matrix, target_return)
                frontier.append({
                    'return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe_ratio': result['sharpe_ratio']
                })
            except:
                continue
        
        return {
            'efficient_frontier': frontier,
            'min_volatility_portfolio': frontier[0] if frontier else None,
            'max_sharpe_portfolio': max(frontier, key=lambda x: x['sharpe_ratio']) if frontier else None
        }
    
    def calculate_portfolio_metrics(self, stock_data: Dict, weights: Dict) -> Dict:
        """
        计算投资组合指标
        
        Args:
            stock_data: 股票数据字典
            weights: 权重字典
        
        Returns:
            投资组合指标
        """
        stocks = list(stock_data.keys())
        n_stocks = len(stocks)
        
        if n_stocks == 0:
            return {}
        
        # 转换权重为数组
        weight_array = np.array([weights.get(stock, 0) / 100 for stock in stocks])
        
        # 计算指标
        expected_returns = self._estimate_returns(stock_data)
        cov_matrix = self._estimate_covariance(stock_data)
        
        portfolio_return = np.dot(weight_array, expected_returns)
        portfolio_vol = np.sqrt(np.dot(weight_array.T, np.dot(cov_matrix, weight_array)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0
        
        # 计算风险贡献
        marginal_contrib = np.dot(cov_matrix, weight_array)
        risk_contrib = np.multiply(weight_array, marginal_contrib) / portfolio_vol if portfolio_vol > 0 else np.zeros(n_stocks)
        
        risk_contrib_dict = {}
        for i, stock in enumerate(stocks):
            risk_contrib_dict[stock] = risk_contrib[i] / portfolio_vol * 100 if portfolio_vol > 0 else 0
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'risk_contribution': risk_contrib_dict,
            'max_weight': max(weights.values()) if weights else 0,
            'min_weight': min(weights.values()) if weights else 0,
            'concentration': sum(w**2 for w in weights.values()) / 10000 if weights else 0
        }


# 使用示例
if __name__ == "__main__":
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
        }
    }
    
    # 创建优化器
    optimizer = PortfolioOptimizer()
    
    # 均值-方差优化
    result_mv = optimizer.optimize_portfolio(test_stock_data, method='mean_variance', risk_profile='稳健型')
    print("均值-方差优化结果:")
    print(f"权重: {result_mv['weights']}")
    print(f"预期收益: {result_mv['expected_return']:.4f}")
    print(f"波动率: {result_mv['volatility']:.4f}")
    print(f"夏普比率: {result_mv['sharpe_ratio']:.4f}")
    
    # 风险平价优化
    result_rp = optimizer.optimize_portfolio(test_stock_data, method='risk_parity')
    print("\n风险平价优化结果:")
    print(f"权重: {result_rp['weights']}")
