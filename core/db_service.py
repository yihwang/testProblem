# 数据库服务 - 提供持久化数据存储功能

import sqlite3
import uuid
import os
from datetime import datetime
from typing import Optional, List
from core.config import logger


class DatabaseService:
    """数据库服务类，负责文章数据的持久化存储"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库服务
        
        Args:
            db_path: 数据库文件路径，默认使用应用根目录下的articles.db
        """
        if db_path is None:
            # 默认使用应用根目录下的articles.db
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "articles.db")
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库，创建必要的表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建articles表，存储文章的基本信息
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        description TEXT,
                        content TEXT,
                        url TEXT UNIQUE,
                        source TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 创建full_texts表，存储文章的完整网页内容
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS full_texts (
                        id TEXT PRIMARY KEY,
                        article_id TEXT,
                        full_text TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE
                    )
                ''')
                
                # 为url创建索引，提高查询效率
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles (url)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_full_texts_article_id ON full_texts (article_id)')
                
                conn.commit()
                logger.info(f"数据库初始化成功，文件路径: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"数据库初始化失败: {str(e)}")
    
    def check_article_exists(self, url: str) -> Optional[dict]:
        """
        检查指定URL的文章是否已存在于数据库中
        
        Args:
            url: 文章URL
            
        Returns:
            文章信息字典，如果不存在则返回None
        """
        if not url:
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # 使返回的结果可以通过列名访问
                cursor = conn.cursor()
                
                # 查询文章基本信息
                cursor.execute('''
                    SELECT a.*, ft.full_text 
                    FROM articles a 
                    LEFT JOIN full_texts ft ON a.id = ft.article_id 
                    WHERE a.url = ?
                ''', (url,))
                
                result = cursor.fetchone()
                if result:
                    # 将结果转换为字典
                    article_data = dict(result)
                    logger.info(f"找到已存在的文章: {url}")
                    return article_data
                
                logger.info(f"未找到文章: {url}")
                return None
        except sqlite3.Error as e:
            logger.error(f"检查文章是否存在时出错: {str(e)}")
            return None
    
    def save_article(self, article_data: dict) -> bool:
        """
        保存文章信息到数据库
        
        Args:
            article_data: 包含文章信息的字典，需要包含url字段
            
        Returns:
            保存是否成功
        """
        if not article_data or 'url' not in article_data:
            logger.error("保存文章失败: 缺少必要的文章数据或URL")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = datetime.now().isoformat()
                
                # 检查文章是否已存在
                existing_article = self.check_article_exists(article_data['url'])
                
                if existing_article:
                    # 文章已存在，更新信息
                    article_id = existing_article['id']
                    
                    # 更新articles表
                    cursor.execute('''
                        UPDATE articles 
                        SET title = ?, description = ?, content = ?, source = ?, updated_at = ? 
                        WHERE id = ?
                    ''', (
                        article_data.get('title'),
                        article_data.get('description'),
                        article_data.get('content'),
                        article_data.get('source'),
                        current_time,
                        article_id
                    ))
                    
                    # 更新full_texts表
                    if 'full_text' in article_data and article_data['full_text']:
                        # 检查full_texts表中是否已有记录
                        cursor.execute('SELECT id FROM full_texts WHERE article_id = ?', (article_id,))
                        full_text_record = cursor.fetchone()
                        
                        if full_text_record:
                            cursor.execute('''
                                UPDATE full_texts 
                                SET full_text = ?, updated_at = ? 
                                WHERE article_id = ?
                            ''', (
                                article_data['full_text'],
                                current_time,
                                article_id
                            ))
                        else:
                            cursor.execute('''
                                INSERT INTO full_texts (id, article_id, full_text, created_at, updated_at) 
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                str(uuid.uuid4()),
                                article_id,
                                article_data['full_text'],
                                current_time,
                                current_time
                            ))
                else:
                    # 文章不存在，创建新记录
                    article_id = str(uuid.uuid4())
                    
                    # 插入articles表
                    cursor.execute('''
                        INSERT INTO articles (id, title, description, content, url, source, created_at, updated_at) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article_id,
                        article_data.get('title'),
                        article_data.get('description'),
                        article_data.get('content'),
                        article_data['url'],
                        article_data.get('source'),
                        current_time,
                        current_time
                    ))
                    
                    # 插入full_texts表（如果有full_text）
                    if 'full_text' in article_data and article_data['full_text']:
                        cursor.execute('''
                            INSERT INTO full_texts (id, article_id, full_text, created_at, updated_at) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            str(uuid.uuid4()),
                            article_id,
                            article_data['full_text'],
                            current_time,
                            current_time
                        ))
                
                conn.commit()
                logger.info(f"成功保存文章: {article_data['url']}")
                return True
        except sqlite3.Error as e:
            logger.error(f"保存文章时出错: {str(e)}")
            return False
    
    def save_full_text(self, url: str, full_text: str) -> bool:
        """
        保存文章的完整网页内容
        
        Args:
            url: 文章URL
            full_text: 完整网页内容
            
        Returns:
            保存是否成功
        """
        if not url or not full_text:
            logger.error("保存网页内容失败: 缺少必要的URL或内容")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                current_time = datetime.now().isoformat()
                
                # 检查文章是否存在
                cursor.execute('SELECT id FROM articles WHERE url = ?', (url,))
                result = cursor.fetchone()
                
                if result:
                    article_id = result[0]
                    
                    # 检查full_texts表中是否已有记录
                    cursor.execute('SELECT id FROM full_texts WHERE article_id = ?', (article_id,))
                    full_text_record = cursor.fetchone()
                    
                    if full_text_record:
                        # 更新现有记录
                        cursor.execute('''
                            UPDATE full_texts 
                            SET full_text = ?, updated_at = ? 
                            WHERE article_id = ?
                        ''', (
                            full_text,
                            current_time,
                            article_id
                        ))
                    else:
                        # 创建新记录
                        cursor.execute('''
                            INSERT INTO full_texts (id, article_id, full_text, created_at, updated_at) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            str(uuid.uuid4()),
                            article_id,
                            full_text,
                            current_time,
                            current_time
                        ))
                    
                    conn.commit()
                    logger.info(f"成功保存网页内容: {url}")
                    return True
                else:
                    logger.error(f"保存网页内容失败: 找不到对应的文章记录，URL: {url}")
                    return False
        except sqlite3.Error as e:
            logger.error(f"保存网页内容时出错: {str(e)}")
            return False
    
    def get_articles_by_topic(self, topic: str, limit: int = 10) -> List[dict]:
        """
        根据主题搜索文章
        
        Args:
            topic: 搜索主题
            limit: 返回的文章数量上限
            
        Returns:
            文章信息列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 在标题、描述和内容中搜索包含主题的文章
                query = '''
                    SELECT a.*, ft.full_text 
                    FROM articles a 
                    LEFT JOIN full_texts ft ON a.id = ft.article_id 
                    WHERE a.title LIKE ? OR a.description LIKE ? OR a.content LIKE ?
                    ORDER BY a.updated_at DESC
                    LIMIT ?
                '''
                
                search_pattern = f'%{topic}%'
                cursor.execute(query, (search_pattern, search_pattern, search_pattern, limit))
                
                results = cursor.fetchall()
                articles = [dict(row) for row in results]
                
                logger.info(f"找到 {len(articles)} 篇关于 '{topic}' 的文章")
                return articles
        except sqlite3.Error as e:
            logger.error(f"搜索文章时出错: {str(e)}")
            return []


# 创建单例实例，方便其他模块使用
db_service = DatabaseService()