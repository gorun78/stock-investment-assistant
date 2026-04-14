#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据存储模块 - 使用SQLite保存操作日志和交易记录
"""

import sqlite3
import os
import json
from datetime import datetime
from contextlib import contextmanager

class DataStorage:
    """数据存储类"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            db_path = os.path.join(data_dir, 'stock_assistant.db')
        
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    module TEXT NOT NULL,
                    description TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_type TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    stock_symbol TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    profit REAL DEFAULT 0,
                    balance_after REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_type TEXT NOT NULL,
                    market_trend TEXT,
                    top_sectors TEXT,
                    portfolio_summary TEXT,
                    timing_signal TEXT,
                    risk_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_selections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy TEXT NOT NULL,
                    sector TEXT,
                    results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    actions_count INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_operation_logs_created 
                ON operation_logs(created_at)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trading_records_created 
                ON trading_records(created_at)
            ''')
    
    def log_operation(self, operation_type, module, description='', details=None):
        """记录操作日志"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO operation_logs (operation_type, module, description, details)
                VALUES (?, ?, ?, ?)
            ''', (operation_type, module, description, json.dumps(details, ensure_ascii=False) if details else None))
            return cursor.lastrowid
    
    def log_trade(self, trade_type, stock_name, price, quantity, total_amount, 
                  profit=0, balance_after=None, stock_symbol=None):
        """记录交易"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trading_records 
                (trade_type, stock_name, stock_symbol, price, quantity, total_amount, profit, balance_after)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (trade_type, stock_name, stock_symbol, price, quantity, total_amount, profit, balance_after))
            return cursor.lastrowid
    
    def log_analysis(self, analysis_type, market_trend=None, top_sectors=None, 
                     portfolio_summary=None, timing_signal=None, risk_level=None):
        """记录分析结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results 
                (analysis_type, market_trend, top_sectors, portfolio_summary, timing_signal, risk_level)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (analysis_type, market_trend, 
                  json.dumps(top_sectors, ensure_ascii=False) if top_sectors else None,
                  json.dumps(portfolio_summary, ensure_ascii=False) if portfolio_summary else None,
                  timing_signal, risk_level))
            return cursor.lastrowid
    
    def log_selection(self, strategy, sector, results):
        """记录选股结果"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_selections (strategy, sector, results)
                VALUES (?, ?, ?)
            ''', (strategy, sector, json.dumps(results, ensure_ascii=False)))
            return cursor.lastrowid
    
    def get_recent_operations(self, limit=50, module=None):
        """获取最近操作记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if module:
                cursor.execute('''
                    SELECT * FROM operation_logs 
                    WHERE module = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (module, limit))
            else:
                cursor.execute('''
                    SELECT * FROM operation_logs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_trades(self, limit=50):
        """获取最近交易记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM trading_records 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_analyses(self, limit=20):
        """获取最近分析记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_results 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get('top_sectors'):
                    result['top_sectors'] = json.loads(result['top_sectors'])
                if result.get('portfolio_summary'):
                    result['portfolio_summary'] = json.loads(result['portfolio_summary'])
                results.append(result)
            return results
    
    def get_recent_selections(self, limit=20):
        """获取最近选股记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM stock_selections 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                if result.get('results'):
                    result['results'] = json.loads(result['results'])
                results.append(result)
            return results
    
    def get_statistics(self):
        """获取统计数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) as count FROM operation_logs')
            ops_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM trading_records')
            trades_count = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM analysis_results')
            analyses_count = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT trade_type, SUM(total_amount) as total 
                FROM trading_records 
                GROUP BY trade_type
            ''')
            trade_summary = {row['trade_type']: row['total'] for row in cursor.fetchall()}
            
            cursor.execute('''
                SELECT SUM(profit) as total_profit FROM trading_records
            ''')
            total_profit = cursor.fetchone()['total_profit'] or 0
            
            return {
                'total_operations': ops_count,
                'total_trades': trades_count,
                'total_analyses': analyses_count,
                'buy_total': trade_summary.get('buy', 0),
                'sell_total': trade_summary.get('sell', 0),
                'total_profit': total_profit
            }
    
    def clear_old_records(self, days=30):
        """清理旧记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM operation_logs 
                WHERE created_at < datetime('now', ?)
            ''', (f'-{days} days',))
            
            cursor.execute('''
                DELETE FROM analysis_results 
                WHERE created_at < datetime('now', ?)
            ''', (f'-{days} days',))
            
            return cursor.rowcount


data_storage = DataStorage()
