"""
统一的 PostgreSQL 消费者管理器
自动识别单命名空间和多命名空间模式
"""
import asyncio
import logging
import multiprocessing
from typing import Dict, Optional, Set
from jettask.core.unified_manager_base import UnifiedManagerBase
from jettask.core.namespace import NamespaceDataAccessManager
from jettask.persistence.consumer import PostgreSQLConsumer

logger = logging.getLogger(__name__)


class UnifiedConsumerManager(UnifiedManagerBase):
    """
    统一的消费者管理器
    继承自 UnifiedManagerBase，实现消费者特定的逻辑
    """

    def __init__(self,
                 task_center_url: str,
                 check_interval: int = 30,
                 backlog_monitor_interval: int = 30,
                 concurrency: int = 4,
                 debug: bool = False):
        """
        初始化消费者管理器

        Args:
            task_center_url: 任务中心URL
            check_interval: 命名空间检测间隔（秒）
            backlog_monitor_interval: 积压监控间隔（秒）
            concurrency: 并发数（每个命名空间的 worker 进程数）
            debug: 是否启用调试模式
        """
        super().__init__(task_center_url, check_interval, debug)

        self.backlog_monitor_interval = backlog_monitor_interval
        self.concurrency = concurrency

        # 消费者管理
        self.consumer_instance: Optional[PostgreSQLConsumer] = None  # 单命名空间模式
        self.consumer_processes: Dict[str, multiprocessing.Process] = {}  # 多命名空间模式
        self.known_namespaces: Set[str] = set()

        # 命名空间数据访问管理器
        self.namespace_manager: Optional[NamespaceDataAccessManager] = None

    async def run_single_namespace(self, namespace_name: str):
        """
        运行单命名空间模式

        Args:
            namespace_name: 命名空间名称
        """
        logger.info(f"启动单命名空间消费者: {namespace_name}")
        logger.info(f"积压监控间隔: {self.backlog_monitor_interval}秒")

        try:
            # 创建命名空间数据访问管理器
            base_url = self.get_base_url()
            self.namespace_manager = NamespaceDataAccessManager(task_center_base_url=base_url)

            # 获取命名空间连接
            conn = await self.namespace_manager.get_connection(namespace_name)

            # 检查是否配置了 PostgreSQL
            if not conn.pg_config:
                logger.error(f"命名空间 {namespace_name} 未配置 PostgreSQL，无法启动消费者")
                return

            logger.info(f"命名空间 {namespace_name} 配置:")
            logger.info(f"  - Redis: {'已配置' if conn.redis_config else '未配置'}")
            logger.info(f"  - PostgreSQL: 已配置")
            logger.info(f"  - Redis Prefix: {conn.redis_prefix}")

            # 创建并启动消费者
            self.consumer_instance = PostgreSQLConsumer(
                pg_config=conn.pg_config,
                redis_config=conn.redis_config,
                prefix=conn.redis_prefix,
                namespace_name=namespace_name
            )

            logger.info(f"✓ 消费者已启动: {namespace_name}")

            # 运行消费者
            await self.consumer_instance.start(concurrency=self.concurrency)

        except Exception as e:
            logger.error(f"单命名空间消费者运行失败: {e}", exc_info=self.debug)
            raise
        finally:
            # 清理
            if self.consumer_instance:
                await self.consumer_instance.stop()
                logger.info(f"消费者已停止: {namespace_name}")

            if self.namespace_manager:
                await self.namespace_manager.close_all()

    async def run_multi_namespace(self, namespace_names: Optional[Set[str]]):
        """
        运行多命名空间模式

        Args:
            namespace_names: 目标命名空间集合，None表示所有命名空间
        """
        logger.info("启动多命名空间消费者管理")
        logger.info(f"命名空间检测间隔: {self.check_interval}秒")
        logger.info(f"积压监控间隔: {self.backlog_monitor_interval}秒")

        # 创建命名空间数据访问管理器
        base_url = self.get_base_url()
        self.namespace_manager = NamespaceDataAccessManager(task_center_base_url=base_url)

        # 获取初始命名空间
        namespaces = await self.fetch_namespaces_info(namespace_names)

        # 启动每个命名空间的消费者进程
        for ns_info in namespaces:
            self._start_consumer_process(ns_info['name'])
            self.known_namespaces.add(ns_info['name'])

        # 创建并发任务
        try:
            health_check_task = asyncio.create_task(self._health_check_loop())
            namespace_check_task = asyncio.create_task(self._namespace_check_loop())

            # 等待任一任务完成或出错
            _, pending = await asyncio.wait(
                [health_check_task, namespace_check_task],
                return_when=asyncio.FIRST_EXCEPTION
            )

            # 取消所有未完成的任务
            for task in pending:
                task.cancel()

        except asyncio.CancelledError:
            logger.info("收到取消信号")
        finally:
            # 清理
            if self.namespace_manager:
                await self.namespace_manager.close_all()

    def _start_consumer_process(self, namespace_name: str):
        """启动单个命名空间的消费者进程"""

        # 如果进程已存在且存活，跳过
        if namespace_name in self.consumer_processes:
            process = self.consumer_processes[namespace_name]
            if process.is_alive():
                logger.debug(f"命名空间 {namespace_name} 的消费者进程已在运行")
                return
            else:
                # 清理已停止的进程
                process.terminate()
                process.join(timeout=5)

        # 创建新进程
        logger.info(f"启动命名空间 {namespace_name} 的消费者进程")

        process = multiprocessing.Process(
            target=_run_consumer_in_process,
            args=(self.task_center_url, namespace_name, self.backlog_monitor_interval, self.concurrency, self.debug),
            name=f"Consumer-{namespace_name}"
        )
        process.start()
        self.consumer_processes[namespace_name] = process

        logger.info(f"✓ 消费者进程已启动: {namespace_name} (PID: {process.pid})")

    async def _health_check_loop(self):
        """健康检查循环 - 检查消费者进程状态"""
        logger.info("健康检查循环已启动")

        while True:
            try:
                # 检查所有消费者进程
                dead_processes = []
                for ns_name, process in self.consumer_processes.items():
                    if not process.is_alive():
                        logger.warning(f"消费者进程 {ns_name} 已停止 (退出码: {process.exitcode})")
                        dead_processes.append(ns_name)

                # 重启已停止的进程
                for ns_name in dead_processes:
                    logger.info(f"重启消费者进程: {ns_name}")
                    self._start_consumer_process(ns_name)

                # 等待下一次检查
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"健康检查循环异常: {e}", exc_info=self.debug)
                await asyncio.sleep(10)

    async def _namespace_check_loop(self):
        """命名空间检查循环 - 检测新的命名空间"""
        logger.info("命名空间检查循环已启动")

        while True:
            try:
                # 获取当前所有命名空间
                namespaces = await self.fetch_namespaces_info(None)
                current_namespaces = {ns['name'] for ns in namespaces}

                # 发现新命名空间
                new_namespaces = current_namespaces - self.known_namespaces
                if new_namespaces:
                    logger.info(f"发现新命名空间: {new_namespaces}")
                    for ns_name in new_namespaces:
                        self._start_consumer_process(ns_name)
                        self.known_namespaces.add(ns_name)

                # 停止已删除的命名空间消费者
                removed_namespaces = self.known_namespaces - current_namespaces
                if removed_namespaces:
                    logger.info(f"命名空间已删除: {removed_namespaces}")
                    for ns_name in removed_namespaces:
                        if ns_name in self.consumer_processes:
                            process = self.consumer_processes[ns_name]
                            logger.info(f"停止消费者进程: {ns_name}")
                            process.terminate()
                            process.join(timeout=10)
                            del self.consumer_processes[ns_name]
                        self.known_namespaces.remove(ns_name)

                # 等待下一次检查
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"命名空间检查循环异常: {e}", exc_info=self.debug)
                await asyncio.sleep(10)

    async def run(self):
        """
        运行管理器（自动判断单/多命名空间模式）
        """
        try:
            self.running = True

            if self.is_single_namespace:
                # 单命名空间模式
                await self.run_single_namespace(self.namespace_name)
            else:
                # 多命名空间模式
                target_namespaces = self.get_target_namespaces()
                await self.run_multi_namespace(target_namespaces)

        except KeyboardInterrupt:
            logger.info("收到中断信号，停止所有消费者...")
        finally:
            self.running = False

            # 停止所有消费者进程
            for ns_name, process in list(self.consumer_processes.items()):
                logger.info(f"停止消费者进程: {ns_name}")
                process.terminate()
                process.join(timeout=10)

            logger.info("所有消费者已停止")


def _run_consumer_in_process(task_center_url: str, namespace_name: str,
                             backlog_monitor_interval: int, concurrency: int, debug: bool):
    """
    在独立进程中运行消费者（复用 run_single_namespace 逻辑）

    Args:
        task_center_url: 任务中心URL
        namespace_name: 命名空间名称
        backlog_monitor_interval: 积压监控间隔
        concurrency: 并发数
        debug: 是否启用调试模式
    """
    import logging

    # 配置日志
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format=f'%(asctime)s - [{namespace_name}] - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建临时管理器实例并运行单命名空间
    manager = UnifiedConsumerManager(
        task_center_url=task_center_url,
        backlog_monitor_interval=backlog_monitor_interval,
        concurrency=concurrency,
        debug=debug
    )

    # 运行异步任务
    try:
        asyncio.run(manager.run_single_namespace(namespace_name))
    except KeyboardInterrupt:
        logging.getLogger(__name__).info("进程收到中断信号")


__all__ = ['UnifiedConsumerManager']
