"""
API 监控装饰器模块

高性能、轻量级的 API 访问监控系统，专注于核心监控指标的收集和分析。

核心特性：
1. 请求监控：记录接口访问的核心信息（耗时、状态、ip 等）
2. 统计分析：提供按时间维度的访问统计和性能分析
3. 高性能：精简字段设计，优化索引策略，最小化性能影响
4. 安全性：自动脱敏敏感信息，支持 ip 风险评估
5. 自动清理：支持历史数据自动归档和清理
"""

import os
import json
import time
import uuid
import pymysql
import functools
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dbutils.pooled_db import PooledDB # type: ignore
from flask import request, g



class RouteMonitor:
    """
    路由监控核心类
    
    负责 API 请求的监控、日志记录和统计分析。
    采用精简设计，专注于核心监控指标，最大程度降低对业务性能的影响。
    
    Attributes:
        database (str): 监控数据库名称，默认为 'api监控系统'
        pool (PooledDB): 数据库连接池
        
    核心方法:
        - api_monitor: 装饰器，用于监控 API 接口
        - get_statistics_summary: 获取统计摘要数据
        - cleanup_old_data: 清理历史数据
    """
    
    def __init__(self, database: str = 'api监控系统', pool = None):
        """
        初始化监控系统
        
        Args:
            database: 数据库名称，默认为 'api监控系统'
            pool: 数据库连接池对象，如果不传则使用默认配置创建
        """
        self.database = database
        self.pool = pool
        if self.pool is None:
            self.init_database_pool()
        self.init_database_tables()

    def init_database_pool(self):
        """
        初始化数据库连接池
        
        配置说明：
        - 最大连接数：2（监控系统不需要大量连接）
        - 编码：utf8mb4（支持中文和 emoji）
        - 自动重连：开启
        """
        from mdbq.myconf import myconf # type: ignore
        parser = myconf.ConfigParser()
        host, port, username, password = parser.get_section_values(
            file_path=os.path.join(os.path.expanduser("~"), 'spd.txt'),
            section='mysql',
            keys=['host', 'port', 'username', 'password'],
        )
        try:
            self.pool = PooledDB(
                creator=pymysql,
                maxconnections=2,
                mincached=1,
                maxcached=2,
                blocking=True,
                host=host,
                port=int(port),
                user=username,
                password=password,
                ping=1,  # 自动重连
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

            # 创建数据库
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                        f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
                    cursor.execute(f"USE `{self.database}`")
            finally:
                connection.close()
                
        except Exception as e:
            raise
    
    def ensure_database_context(self, cursor):
        """
        确保游标处于正确的数据库上下文中
        
        Args:
            cursor: 数据库游标对象
        """
        try:
            cursor.execute(f"USE `{self.database}`")
        except Exception:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.database}` "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            cursor.execute(f"USE `{self.database}`")
        
    def init_database_tables(self):
        """
        初始化数据库表结构
        
        创建三张核心表：
        1. api_访问日志：记录每次 API 请求的详细信息
        2. api_接口统计：按小时汇总的接口性能统计
        3. api_ip记录：IP 维度的访问统计
        """
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    self.ensure_database_context(cursor)
                    
                    # ==================== 表 1：访问日志表 ====================
                    # 设计原则：只保留核心监控字段，移除冗余信息
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `api_访问日志` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键，自增id',
                            `请求id` VARCHAR(64) NOT NULL COMMENT '请求唯一标识（用于追踪）',
                            `请求时间` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '请求时间，精确到毫秒',
                            `请求方法` VARCHAR(10) NOT NULL COMMENT 'HTTP 方法（GET/POST/PUT/DELETE等）',
                            `接口路径` VARCHAR(500) NOT NULL COMMENT 'API 接口路径',
                            `客户端ip` VARCHAR(45) NOT NULL COMMENT '客户端 ip 地址（支持 IPv6）',
                            `响应状态码` SMALLINT COMMENT 'HTTP 响应状态码',
                            `响应耗时` DECIMAL(10,3) COMMENT '请求处理耗时（毫秒）',
                            `用户标识` VARCHAR(64) COMMENT '用户id或标识（如有）',
                            `用户代理` VARCHAR(500) COMMENT '浏览器 User-Agent（精简版）',
                            `请求参数` TEXT COMMENT '请求参数（JSON格式，可选记录）',
                            `错误信息` TEXT COMMENT '错误信息（仅失败请求记录）',
                            `创建时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                            `更新时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
                            
                            UNIQUE KEY `uk_请求id` (`请求id`),
                            INDEX `idx_请求时间` (`请求时间`),
                            INDEX `idx_接口路径` (`接口路径`(191)),
                            INDEX `idx_客户端ip` (`客户端ip`),
                            INDEX `idx_响应状态码` (`响应状态码`),
                            INDEX `idx_用户标识` (`用户标识`),
                            INDEX `idx_时间_接口` (`请求时间`, `接口路径`(191))
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='API 访问日志表 - 记录每次请求的核心信息'
                        ROW_FORMAT=COMPRESSED;
                    """)
                    
                    # ==================== 表 2：接口统计表 ====================
                    # 设计原则：按小时维度汇总，用于性能分析和趋势监控
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `api_接口统计` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键，自增id',
                            `统计日期` DATE NOT NULL COMMENT '统计日期',
                            `统计小时` TINYINT NOT NULL COMMENT '统计小时（0-23）',
                            `接口路径` VARCHAR(500) NOT NULL COMMENT 'API 接口路径',
                            `请求方法` VARCHAR(10) NOT NULL COMMENT 'HTTP 请求方法',
                            `请求总数` INT UNSIGNED DEFAULT 0 COMMENT '总请求次数',
                            `成功次数` INT UNSIGNED DEFAULT 0 COMMENT '成功响应次数（状态码 < 400）',
                            `失败次数` INT UNSIGNED DEFAULT 0 COMMENT '失败响应次数（状态码 >= 400）',
                            `平均耗时` DECIMAL(10,3) DEFAULT 0 COMMENT '平均响应耗时（毫秒）',
                            `最大耗时` DECIMAL(10,3) DEFAULT 0 COMMENT '最大响应耗时（毫秒）',
                            `最小耗时` DECIMAL(10,3) DEFAULT 0 COMMENT '最小响应耗时（毫秒）',
                            `独立ip数` INT UNSIGNED DEFAULT 0 COMMENT '访问的独立 ip 数量',
                            `创建时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                            `更新时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
                            
                            UNIQUE KEY `uk_日期_小时_接口_方法` (`统计日期`, `统计小时`, `接口路径`(191), `请求方法`),
                            INDEX `idx_统计日期` (`统计日期`),
                            INDEX `idx_接口路径` (`接口路径`(191)),
                            INDEX `idx_日期_接口` (`统计日期`, `接口路径`(191))
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='API 接口统计表 - 按小时汇总的接口性能数据';
                    """)
                    
                    # ==================== 表 3：IP 访问记录表 ====================
                    # 设计原则：按日期汇总 IP 访问情况，用于安全分析和流量监控
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS `api_ip记录` (
                            `id` BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键，自增id',
                            `统计日期` DATE NOT NULL COMMENT '统计日期',
                            `客户端ip` VARCHAR(45) NOT NULL COMMENT '客户端 ip 地址',
                            `请求总数` INT UNSIGNED DEFAULT 0 COMMENT '该 ip 当日总请求数',
                            `成功次数` INT UNSIGNED DEFAULT 0 COMMENT '成功请求次数',
                            `失败次数` INT UNSIGNED DEFAULT 0 COMMENT '失败请求次数',
                            `平均耗时` DECIMAL(10,3) DEFAULT 0 COMMENT '平均响应耗时（毫秒）',
                            `首次访问` DATETIME COMMENT '首次访问时间',
                            `最后访问` DATETIME COMMENT '最后访问时间',
                            `访问接口数` INT UNSIGNED DEFAULT 0 COMMENT '访问的不同接口数量',
                            `风险评分` TINYINT UNSIGNED DEFAULT 0 COMMENT '风险评分（0-100，用于识别异常流量）',
                            `创建时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
                            `更新时间` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '记录更新时间',
                            
                            UNIQUE KEY `uk_日期_ip` (`统计日期`, `客户端ip`),
                            INDEX `idx_统计日期` (`统计日期`),
                            INDEX `idx_客户端ip` (`客户端ip`),
                            INDEX `idx_风险评分` (`风险评分`),
                            INDEX `idx_请求总数` (`请求总数`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
                        COMMENT='API ip 访问记录表 - ip 维度的访问统计';
                    """)
                connection.commit()
                
            finally:
                connection.close()
                
        except Exception as e:
            # 静默处理初始化错误，避免影响主应用启动
            pass
    
    # ==================== 辅助方法 ====================
    
    def generate_request_id(self) -> str:
        """
        生成唯一的请求 ID
        
        格式：req_{时间戳}_{随机字符串}
        示例：req_1697654321123_a1b2c3d4
        
        Returns:
            str: 请求唯一标识符
        """
        timestamp = str(int(time.time() * 1000))
        random_part = uuid.uuid4().hex[:8]
        return f"req_{timestamp}_{random_part}"
    
    def get_real_ip(self, request) -> str:
        """
        获取真实客户端 IP 地址
        
        优先级顺序：
        1. X-Forwarded-For（代理服务器传递的原始IP）
        2. X-Real-IP（Nginx 等反向代理设置）
        3. CF-Connecting-IP（Cloudflare CDN）
        4. request.remote_addr（直连IP）
        
        Args:
            request: Flask request 对象
            
        Returns:
            str: 客户端真实 IP 地址
        """
        # IP 头优先级列表
        ip_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',
            'X-Client-IP',
        ]
        
        # 尝试从请求头获取 IP
        for header in ip_headers:
            header_value = request.headers.get(header)
            if header_value:
                # X-Forwarded-For 可能包含多个 IP，取第一个
                ip = header_value.split(',')[0].strip()
                if ip:
                    return ip
        
        # 如果没有代理头，返回直连 IP
        return request.remote_addr or 'unknown'
    
    def sanitize_params(self, params: Dict[str, Any]) -> Optional[str]:
        """
        清理和脱敏请求参数
        
        自动移除敏感字段（如 password、token 等）
        
        Args:
            params: 请求参数字典
            
        Returns:
            str: JSON 格式的参数字符串（已脱敏），或 None
        """
        if not params:
            return None
        
        # 敏感字段列表
        sensitive_keys = ['password', 'passwd', 'pwd', 'token', 'secret', 'key', 'api_key', 'apikey']
        
        # 创建副本并脱敏
        sanitized = {}
        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '***'
            else:
                # 截断过长的值
                if isinstance(value, str) and len(value) > 500:
                    sanitized[key] = value[:500] + '...'
                else:
                    sanitized[key] = value
        
        try:
            return json.dumps(sanitized, ensure_ascii=False)
        except Exception:
            return None
    
    # ==================== 核心数据收集 ====================
    
    def collect_request_data(self, request) -> Dict[str, Any]:
        """
        收集请求核心数据
        
        仅收集必要的监控信息，避免过度记录造成性能和存储压力。
        
        Args:
            request: Flask request 对象
            
        Returns:
            dict: 包含请求核心信息的字典
        """
        request_id = self.generate_request_id()
        g.request_id = request_id  # 保存到全局变量，供后续使用
        
        # 获取客户端 IP
        client_ip = self.get_real_ip(request)
        
        # 获取 User-Agent（截断过长的）
        user_agent = request.headers.get('User-Agent', '')
        if len(user_agent) > 500:
            user_agent = user_agent[:500]
        
        # 获取用户标识（如果有）
        user_id = None
        if hasattr(g, 'current_user_id'):
            user_id = str(g.current_user_id)
        elif hasattr(g, 'user_id'):
            user_id = str(g.user_id)
        
        # 收集请求参数（可选，仅在需要时记录）
        request_params = None
        if request.args:
            request_params = self.sanitize_params(dict(request.args))
        
        # 构建请求数据字典
        request_data = {
            '请求id': request_id,
            '请求时间': datetime.now(),
            '请求方法': request.method,
            '接口路径': request.endpoint or request.path,
            '客户端ip': client_ip,
            '用户标识': user_id,
            '用户代理': user_agent,
            '请求参数': request_params,
        }
        
        return request_data
    
    # ==================== 数据持久化 ====================
    
    def save_request_log(self, request_data: Dict[str, Any], response_data: Dict[str, Any] = None):
        """
        保存请求日志到数据库
        
        Args:
            request_data: 请求数据字典
            response_data: 响应数据字典（可选）
        """
        request_id = request_data.get('请求id', 'unknown')
        
        try:
            # 合并响应数据
            if response_data:
                request_data.update(response_data)
            
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    self.ensure_database_context(cursor)
                    
                    # 插入请求日志
                    sql = """
                        INSERT INTO `api_访问日志` (
                            `请求id`, `请求时间`, `请求方法`, `接口路径`, `客户端ip`,
                            `响应状态码`, `响应耗时`, `用户标识`, `用户代理`, `请求参数`, `错误信息`
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """
                    
                    cursor.execute(sql, (
                        request_data.get('请求id'),
                        request_data.get('请求时间'),
                        request_data.get('请求方法'),
                        request_data.get('接口路径'),
                        request_data.get('客户端ip'),
                        request_data.get('响应状态码'),
                        request_data.get('响应耗时'),
                        request_data.get('用户标识'),
                        request_data.get('用户代理'),
                        request_data.get('请求参数'),
                        request_data.get('错误信息'),
                    ))
                    
                connection.commit()
                
            finally:
                connection.close()
                
        except Exception as e:
            # 静默处理错误，避免影响主业务
            pass
    
    def update_statistics(self, request_data: Dict[str, Any]):
        """
        更新统计数据
        
        包括：
        1. 接口统计：按小时汇总接口性能数据
        2. IP 统计：按日期汇总 IP 访问数据
        
        Args:
            request_data: 包含请求和响应信息的字典
        """
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    self.ensure_database_context(cursor)
                    
                    now = datetime.now()
                    date = now.date()
                    hour = now.hour
                    
                    # 判断是否成功（状态码 < 400）
                    status_code = request_data.get('响应状态码', 500)
                    is_success = 1 if status_code < 400 else 0
                    is_error = 1 if status_code >= 400 else 0
                    response_time = request_data.get('响应耗时', 0)
                    
                    # 1. 更新接口统计表
                    cursor.execute("""
                        INSERT INTO `api_接口统计` (
                            `统计日期`, `统计小时`, `接口路径`, `请求方法`,
                            `请求总数`, `成功次数`, `失败次数`,
                            `平均耗时`, `最大耗时`, `最小耗时`
                        ) VALUES (
                            %s, %s, %s, %s, 1, %s, %s, %s, %s, %s
                        ) ON DUPLICATE KEY UPDATE
                            `请求总数` = `请求总数` + 1,
                            `成功次数` = `成功次数` + %s,
                            `失败次数` = `失败次数` + %s,
                            `平均耗时` = (
                                (`平均耗时` * (`请求总数` - 1) + %s) / `请求总数`
                            ),
                            `最大耗时` = GREATEST(`最大耗时`, %s),
                            `最小耗时` = LEAST(`最小耗时`, %s)
                    """, (
                        date, hour, 
                        request_data.get('接口路径', ''),
                        request_data.get('请求方法', ''),
                        is_success, is_error,
                        response_time, response_time, response_time,
                        is_success, is_error,
                        response_time,
                        response_time,
                        response_time
                    ))
                    
                    # 2. 更新 IP 统计表
                    cursor.execute("""
                        INSERT INTO `api_ip记录` (
                            `统计日期`, `客户端ip`, `请求总数`, `成功次数`, `失败次数`,
                            `平均耗时`, `首次访问`, `最后访问`
                        ) VALUES (
                            %s, %s, 1, %s, %s, %s, %s, %s
                        ) ON DUPLICATE KEY UPDATE
                            `请求总数` = `请求总数` + 1,
                            `成功次数` = `成功次数` + %s,
                            `失败次数` = `失败次数` + %s,
                            `平均耗时` = (
                                (`平均耗时` * (`请求总数` - 1) + %s) / `请求总数`
                            ),
                            `最后访问` = %s
                    """, (
                        date,
                        request_data.get('客户端ip', ''),
                        is_success, is_error,
                        response_time, now, now,
                        is_success, is_error,
                        response_time,
                        now
                    ))
                    
                connection.commit()
                
            finally:
                connection.close()
                
        except Exception as e:
            # 静默处理错误
            pass
    
    # ==================== 核心装饰器 ====================

    def api_monitor(self, func):
        """
        API 监控装饰器
        
        使用方法：
        ```python
        from mdbq.route.monitor import api_monitor
        
        @app.route('/api/users')
        @api_monitor
        def get_users():
            return {'users': [...]}
        ```
        
        功能：
        1. 自动记录请求的核心信息（IP、耗时、状态等）
        2. 实时更新统计数据
        3. 异常情况也会被记录
        4. 不影响主业务逻辑的执行
        
        Args:
            func: 被装饰的函数
            
        Returns:
            装饰后的函数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 记录开始时间
            start_time = time.time()
            g.request_start_time = start_time
            
            # 收集请求数据
            request_data = self.collect_request_data(request)
            request_id = request_data.get('请求id', 'unknown')
            
            try:
                # 执行原函数
                response = func(*args, **kwargs)
                
                # 计算响应时间
                end_time = time.time()
                process_time = round((end_time - start_time) * 1000, 3)  # 毫秒
                
                # 获取响应状态码
                response_status = 200
                if hasattr(response, 'status_code'):
                    response_status = response.status_code
                elif isinstance(response, tuple) and len(response) > 1:
                    # 处理 (data, status_code) 格式的返回
                    response_status = response[1]
                
                # 更新响应数据
                response_data = {
                    '响应状态码': response_status,
                    '响应耗时': process_time,
                }
                
                # 保存日志
                self.save_request_log(request_data, response_data)
                
                # 更新统计
                request_data.update(response_data)
                self.update_statistics(request_data)
                
                return response
                
            except Exception as e:
                # 记录错误信息
                end_time = time.time()
                process_time = round((end_time - start_time) * 1000, 3)
                
                # 构建错误数据
                error_data = {
                    '响应状态码': 500,
                    '响应耗时': process_time,
                    '错误信息': f"{type(e).__name__}: {str(e)}"
                }
                
                # 保存错误日志
                self.save_request_log(request_data, error_data)
                
                # 更新统计
                request_data.update(error_data)
                self.update_statistics(request_data)
                
                # 重新抛出异常，不影响原有错误处理逻辑
                raise
                
        return wrapper

    
    # ==================== 数据查询与分析 ====================

    def get_statistics_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        获取统计摘要
        
        提供指定天数内的 API 访问统计概览。
        
        Args:
            days: 统计天数，默认 7 天
            
        Returns:
            dict: 包含以下内容的统计摘要：
                - 统计周期
                - 总体统计（总请求数、成功率、平均耗时等）
                - 热门接口 TOP 10
                - IP 统计
        """
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    self.ensure_database_context(cursor)
                    
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=days)
                    
                    # 1. 总体统计
                    cursor.execute("""
                        SELECT 
                            SUM(请求总数) as 总请求数,
                            SUM(成功次数) as 成功次数,
                            SUM(失败次数) as 失败次数,
                            ROUND(AVG(平均耗时), 2) as 平均耗时,
                            COUNT(DISTINCT 接口路径) as 接口数量
                        FROM api_接口统计
                        WHERE 统计日期 BETWEEN %s AND %s
                    """, (start_date, end_date))
                    
                    summary = cursor.fetchone() or {}
                    
                    # 2. 热门接口 TOP 10
                    cursor.execute("""
                        SELECT 
                            接口路径,
                            SUM(请求总数) as 请求次数,
                            ROUND(AVG(平均耗时), 2) as 平均耗时
                        FROM api_接口统计
                        WHERE 统计日期 BETWEEN %s AND %s
                        GROUP BY 接口路径
                        ORDER BY 请求次数 DESC
                        LIMIT 10
                    """, (start_date, end_date))
                    
                    top_endpoints = cursor.fetchall()
                    
                    # 3. IP 统计
                    cursor.execute("""
                        SELECT 
                            COUNT(DISTINCT 客户端ip) as 独立ip数,
                            SUM(请求总数) as ip总请求数
                        FROM api_ip记录
                        WHERE 统计日期 BETWEEN %s AND %s
                    """, (start_date, end_date))
                    
                    ip_stats = cursor.fetchone() or {}
                    
                    # 4. 性能最慢的接口 TOP 5
                    cursor.execute("""
                        SELECT 
                            接口路径,
                            ROUND(MAX(最大耗时), 2) as 最大耗时,
                            ROUND(AVG(平均耗时), 2) as 平均耗时
                        FROM api_接口统计
                        WHERE 统计日期 BETWEEN %s AND %s
                        GROUP BY 接口路径
                        ORDER BY 最大耗时 DESC
                        LIMIT 5
                    """, (start_date, end_date))
                    
                    slow_endpoints = cursor.fetchall()
                    
                    # 构建返回结果
                    result = {
                        '统计周期': f'{start_date} 至 {end_date}',
                        '总体统计': summary,
                        '热门接口': top_endpoints,
                        'ip统计': ip_stats,
                        '慢接口': slow_endpoints
                    }
                    
                    return result
                    
            finally:
                connection.close()
                    
        except Exception as e:
            return {'错误': str(e)}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """
        清理历史数据
        
        删除指定天数之前的访问日志，保留统计数据。
        建议定期执行（如每天凌晨）以控制数据库大小。
        
        Args:
            days_to_keep: 保留最近多少天的数据，默认 30 天
            
        Returns:
            dict: 清理结果，包含删除的记录数
        """
        try:
            connection = self.pool.connection()
            try:
                with connection.cursor() as cursor:
                    self.ensure_database_context(cursor)
                    
                    cutoff_date = datetime.now().date() - timedelta(days=days_to_keep)
                    
                    # 1. 清理访问日志表
                    cursor.execute("""
                        DELETE FROM api_访问日志
                        WHERE 请求时间 < %s
                    """, (cutoff_date,))
                    
                    deleted_logs = cursor.rowcount
                    
                    # 2. 清理 ip 记录表（可选，通常保留更久）
                    cursor.execute("""
                        DELETE FROM api_ip记录
                        WHERE 统计日期 < %s
                    """, (cutoff_date,))
                    
                    deleted_ip_records = cursor.rowcount
                    
                connection.commit()
                
                result = {
                    '删除日志数': deleted_logs,
                    '删除ip记录数': deleted_ip_records,
                    '清理日期': str(cutoff_date)
                }
                
                return result
                
            finally:
                connection.close()
                
        except Exception as e:
            return {'错误': str(e)}


# ==================== 全局实例与导出 ====================

# 创建全局监控实例
route_monitor = RouteMonitor()

# 导出核心装饰器（推荐使用此方式）
api_monitor = route_monitor.api_monitor


# ==================== 便捷工具函数 ====================

def get_request_id() -> Optional[str]:
    """
    获取当前请求的唯一 ID
    
    可在被 @api_monitor 装饰的函数内调用，用于日志关联和问题追踪。
    
    Returns:
        str: 请求 ID，如果不在请求上下文中则返回 None
        
    示例：
        ```python
        @api_monitor
        def my_api():
            req_id = get_request_id()
            logger.info(f"处理请求: {req_id}")
            return {'status': 'ok'}
        ```
    """
    return getattr(g, 'request_id', None)


def get_statistics_summary(days: int = 7) -> Dict[str, Any]:
    """
    获取统计摘要数据
    
    Args:
        days: 统计天数，默认 7 天
        
    Returns:
        dict: 统计摘要数据
        
    示例：
        ```python
        # 获取最近 7 天的统计
        stats = get_statistics_summary(7)
        print(stats['总体统计'])
        
        # 获取最近 30 天的统计
        stats = get_statistics_summary(30)
        ```
    """
    return route_monitor.get_statistics_summary(days)


def cleanup_old_data(days_to_keep: int = 30) -> Dict[str, int]:
    """
    清理历史数据
    
    删除指定天数之前的详细日志，保留统计数据。
    建议通过定时任务定期执行。
    
    Args:
        days_to_keep: 保留最近多少天的数据，默认 30 天
        
    Returns:
        dict: 清理结果统计
        
    示例：
        ```python
        # 保留最近 30 天的数据，删除更早的
        result = cleanup_old_data(30)
        print(f"清理完成: {result}")
        ```
    """
    return route_monitor.cleanup_old_data(days_to_keep)


# ==================== 模块导出列表 ====================
__all__ = [
    'RouteMonitor',
    'api_monitor',
    'get_request_id',
    'get_statistics_summary',
    'cleanup_old_data',
]