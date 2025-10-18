#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 监控系统 - 队列消费者进程

这是一个单独运行的守护进程，从 Redis 队列中消费监控任务并写入数据库。
在 uwsgi 多进程环境下，只需运行一个或多个此进程即可处理所有 worker 的监控数据。

使用方法：
    python -m mdbq.route.monitor_worker
    
或通过 systemd/supervisor 管理：
    supervisorctl start api_monitor_worker
"""

import os
import sys
import time
import signal
from typing import Optional


class MonitorWorker:
    """监控任务队列消费者"""
    
    def __init__(self, redis_client, database: str = 'api监控系统', pool=None):
        """
        初始化消费者
        
        Args:
            redis_client: Redis 客户端实例
            database: 监控数据库名称
            pool: 数据库连接池（可选）
        """
        from mdbq.route.monitor import RouteMonitor
        
        self.monitor = RouteMonitor(
            database=database,
            pool=pool,
            redis_client=redis_client,
            enable_async=True
        )
        self.running = True
        self.processed_total = 0
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """处理关闭信号"""
        self.running = False
    
    def run(self, batch_size: int = 100, sleep_interval: float = 0.1):
        """
        运行消费者主循环
        
        Args:
            batch_size: 每次处理的最大任务数
            sleep_interval: 队列为空时的休眠间隔（秒）
        """
        last_log_time = time.time()
        log_interval = 60  # 每60秒输出一次统计
        
        try:
            while self.running:
                # 消费一批任务
                processed = self.monitor.consume_queue_tasks(
                    batch_size=batch_size,
                    timeout=1.0
                )
                
                self.processed_total += processed
                
                # 定期输出统计信息
                current_time = time.time()
                if current_time - last_log_time >= log_interval:
                    last_log_time = current_time
                
                # 如果队列为空，短暂休眠
                if processed == 0:
                    time.sleep(sleep_interval)
        
        except Exception as e:
            pass


def create_worker_from_config(config_file: Optional[str] = None):
    """
    从配置文件创建消费者实例
    
    Args:
        config_file: 配置文件路径（可选，默认 ~/spd.txt）
    
    Returns:
        MonitorWorker: 消费者实例
    """
    try:
        import redis
        from mdbq.myconf import myconf
        
        # 读取配置
        if config_file is None:
            config_file = os.path.join(os.path.expanduser("~"), 'spd.txt')
        
        parser = myconf.ConfigParser()
        redis_password = parser.get_value(
            file_path=config_file,
            section='redis',
            key='password',
            value_type=str
        )
        
        # 创建 Redis 客户端
        redis_client = redis.Redis(
            host='127.0.0.1',
            port=6379,
            db=0,
            password=redis_password,
            decode_responses=False,
            socket_timeout=5,
            socket_connect_timeout=3
        )
        
        # 创建消费者
        worker = MonitorWorker(
            redis_client=redis_client,
            database='api监控系统'
        )
        
        return worker
        
    except Exception as e:
        sys.exit(1)


def main():
    """主函数"""
    
    # 创建消费者
    worker = create_worker_from_config()
    
    # 运行消费者
    worker.run(
        batch_size=100,      # 每次处理100个任务
        sleep_interval=0.5   # 队列空时休眠0.5秒
    )


if __name__ == '__main__':
    main()

