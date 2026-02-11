"""
数据库操作模块
提供SQLite数据库的CRUD操作
"""
import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径，默认为项目目录下的data/ulanzi.db
        """
        if db_path is None:
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            db_path = os.path.join(current_dir, 'data', 'ulanzi.db')

        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """确保数据库和表存在"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建品类规则表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS category_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL,
                base_score INTEGER,
                weights JSON,
                keywords JSON,
                hard_filters JSON,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建分类任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                source_file TEXT,
                source_table TEXT,
                status TEXT DEFAULT 'pending',
                total_count INTEGER DEFAULT 0,
                processed_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME
            )
        ''')

        # 创建分类结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classification_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                sku_id TEXT,
                sku_title TEXT,
                site TEXT,
                clean_title TEXT,
                predicted_category TEXT,
                expected_category TEXT,
                decision_reason TEXT,
                scores_all JSON,
                features_bool JSON,
                features_num JSON,
                audit_status TEXT DEFAULT 'pending',
                corrected_by TEXT,
                corrected_at DATETIME,
                FOREIGN KEY (job_id) REFERENCES classification_jobs(id)
            )
        ''')

        # 创建审核日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                result_id INTEGER,
                action TEXT,
                old_value TEXT,
                new_value TEXT,
                auditor TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    # ===== 规则相关操作 =====

    def save_rules_snapshot(self, rules_loader) -> int:
        """
        保存规则快照

        Args:
            rules_loader: 规则加载器实例

        Returns:
            插入的记录ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # 从 rules_loader 获取品类名称和基础分
        category_name = "all_categories"  # 保存全部品类配置
        base_score = 0  # 基础分存储在 scoring_models 中

        cursor.execute('''
            INSERT INTO category_rules
            (category_name, base_score, weights, keywords, hard_filters)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            category_name,
            base_score,
            json.dumps(rules_loader.scoring_models, ensure_ascii=False),
            json.dumps(rules_loader.signals, ensure_ascii=False),
            json.dumps(rules_loader.hard_filters, ensure_ascii=False)
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return record_id

    def get_latest_rules(self) -> Optional[Dict]:
        """获取最新的规则快照"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM category_rules ORDER BY updated_at DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'category_name': row[1],
                'base_score': row[2],
                'weights': json.loads(row[3]) if row[3] else {},
                'keywords': json.loads(row[4]) if row[4] else {},
                'hard_filters': json.loads(row[5]) if row[5] else {},
                'updated_at': row[6]
            }
        return None

    # ===== 任务相关操作 =====

    def create_job(self, name: str, source_file: str = None) -> int:
        """创建分类任务"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO classification_jobs (name, source_file, status)
            VALUES (?, ?, 'pending')
        ''', (name, source_file))

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id

    def update_job_status(self, job_id: int, status: str, processed_count: int = None):
        """更新任务状态"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status == 'completed':
            cursor.execute('''
                UPDATE classification_jobs
                SET status = ?, processed_count = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, processed_count, job_id))
        else:
            cursor.execute('''
                UPDATE classification_jobs
                SET status = ?, processed_count = ?
                WHERE id = ?
            ''', (status, processed_count, job_id))

        conn.commit()
        conn.close()

    def get_job(self, job_id: int) -> Optional[Dict]:
        """获取任务详情"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM classification_jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'source_file': row[2],
                'source_table': row[3],
                'status': row[4],
                'total_count': row[5],
                'processed_count': row[6],
                'created_at': row[7],
                'completed_at': row[8]
            }
        return None

    # ===== 结果相关操作 =====

    def save_results(self, job_id: int, results: List[Dict]):
        """保存分类结果"""
        conn = self.get_connection()
        cursor = conn.cursor()

        for result in results:
            cursor.execute('''
                INSERT INTO classification_results
                (job_id, sku_id, sku_title, site, clean_title, predicted_category,
                 decision_reason, scores_all, features_bool, features_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_id,
                result.get('sku_id'),
                result.get('sku_title'),
                result.get('site'),
                result.get('clean_title'),
                result.get('predicted_category'),
                result.get('decision_reason'),
                json.dumps(result.get('scores_all', {})),
                json.dumps(result.get('features_bool', {})),
                json.dumps(result.get('features_num', {}))
            ))

        conn.commit()
        conn.close()

    def get_results(self, job_id: int, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """获取分类结果"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM classification_results
            WHERE job_id = ?
            ORDER BY id
            LIMIT ? OFFSET ?
        ''', conn, params=(job_id, limit, offset))
        conn.close()
        return df

    def get_unreviewed_results(self, job_id: int = None, limit: int = 50) -> pd.DataFrame:
        """获取待审核的结果"""
        conn = self.get_connection()

        query = '''
            SELECT * FROM classification_results
            WHERE audit_status = 'pending' OR audit_status IS NULL
        '''
        params = []

        if job_id:
            query += ' AND job_id = ?'
            params.append(job_id)

        query += ' ORDER BY id LIMIT ?'
        params.append(limit)

        df = pd.read_sql_query(query, conn, params=tuple(params))
        conn.close()
        return df

    def update_result_audit(self, result_id: int, corrected_category: str,
                            auditor: str = 'system'):
        """更新审核结果"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 获取原结果
        cursor.execute('SELECT predicted_category FROM classification_results WHERE id = ?', (result_id,))
        row = cursor.fetchone()
        old_category = row[0] if row else None

        # 更新结果
        cursor.execute('''
            UPDATE classification_results
            SET expected_category = ?,
                audit_status = 'corrected',
                corrected_by = ?,
                corrected_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (corrected_category, auditor, result_id))

        # 记录日志
        cursor.execute('''
            INSERT INTO audit_logs (result_id, action, old_value, new_value, auditor)
            VALUES (?, 'correct', ?, ?, ?)
        ''', (result_id, old_category, corrected_category, auditor))

        conn.commit()
        conn.close()

    # ===== 统计相关操作 =====

    def get_statistics(self, job_id: int = None) -> Dict:
        """获取分类统计信息"""
        conn = self.get_connection()

        query = '''
            SELECT predicted_category, COUNT(*) as count
            FROM classification_results
        '''
        params = []

        if job_id:
            query += ' WHERE job_id = ?'
            params.append(job_id)

        query += ' GROUP BY predicted_category'

        df = pd.read_sql_query(query, conn, params=tuple(params))
        conn.close()

        return {
            'total': df['count'].sum() if not df.empty else 0,
            'by_category': df.set_index('predicted_category')['count'].to_dict()
        }

    def get_audit_statistics(self) -> Dict:
        """获取审核统计信息"""
        conn = self.get_connection()

        df = pd.read_sql_query('''
            SELECT audit_status, COUNT(*) as count
            FROM classification_results
            GROUP BY audit_status
        ''', conn)
        conn.close()

        return {
            'pending': df[df['audit_status'] == 'pending']['count'].sum() if not df.empty else 0,
            'approved': df[df['audit_status'] == 'approved']['count'].sum() if not df.empty else 0,
            'corrected': df[df['audit_status'] == 'corrected']['count'].sum() if not df.empty else 0,
            'rejected': df[df['audit_status'] == 'rejected']['count'].sum() if not df.empty else 0
        }
