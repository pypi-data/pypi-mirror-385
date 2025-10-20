"""
Namespace 中间件 - 自动注入命名空间上下文

这个中间件会自动检测路由中的 {namespace} 参数，并将 NamespaceContext 注入到 request.state.ns
这样所有路由都无需手动使用 Depends(get_namespace_context)，直接访问 request.state.ns 即可
"""
import logging
import re
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typing import Callable

from jettask.utils.namespace_dep import NamespaceContext

logger = logging.getLogger(__name__)


class NamespaceMiddleware(BaseHTTPMiddleware):
    """
    Namespace 自动注入中间件

    功能：
    1. 自动检测路由路径中的 {namespace} 参数
    2. 查询命名空间配置并建立数据库连接
    3. 将 NamespaceContext 注入到 request.state.ns
    4. 统一处理命名空间不存在等错误

    使用方式：
    ```python
    # 在 app.py 中注册
    app.add_middleware(NamespaceMiddleware)

    # 在路由中使用
    @router.get("/{namespace}/queues")
    async def get_queues(request: Request):
        ns = request.state.ns  # 已自动注入
        redis_client = await ns.get_redis_client()
        # ... 业务逻辑
    ```
    """

    # 需要排除的路径前缀（这些路径不需要 namespace）
    EXCLUDED_PATHS = [
        '/api/v1/namespaces',  # 命名空间管理自身
        '/api/v1/overview/',   # 根路径（健康检查等）
        '/docs',               # API 文档
        '/openapi.json',       # OpenAPI schema
        '/redoc',              # ReDoc 文档
        '/health',             # 健康检查
    ]

    async def dispatch(self, request: Request, call_next: Callable):
        """
        中间件处理逻辑

        Args:
            request: HTTP 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            HTTP 响应
        """
        # 1. 检查是否是排除路径
        path = request.url.path

        # 检查排除路径
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                # 不需要 namespace，直接放行
                return await call_next(request)

        # 2. 从路径中提取 namespace 参数
        # 匹配模式：/api/v1/xxx/{namespace}/...
        namespace_match = re.search(r'/api/v1/[^/]+/([^/]+)', path)

        if not namespace_match:
            # 没有 namespace 参数，直接放行
            return await call_next(request)

        namespace = namespace_match.group(1)

        # 3. 特殊处理：如果 namespace 实际上是其他路径段（如 "redis"），跳过
        # 例如：/api/v1/queues/redis/monitor/{namespace}
        if namespace in ['redis', 'tasks-v2', 'statistics']:
            # 尝试从更后面的路径段提取 namespace
            # 模式：/api/v1/queues/redis/monitor/{namespace}
            namespace_match2 = re.search(r'/api/v1/[^/]+/[^/]+/[^/]+/([^/]+)', path)
            if namespace_match2:
                namespace = namespace_match2.group(1)
            else:
                # 如果还是没有，直接放行（可能这个路由不需要 namespace）
                return await call_next(request)

        # 4. 获取 namespace_data_access
        if not hasattr(request.app.state, 'namespace_data_access'):
            logger.error("namespace_data_access 未初始化")
            return JSONResponse(
                status_code=500,
                content={"detail": "Namespace data access not initialized"}
            )

        manager = request.app.state.namespace_data_access.manager

        # 5. 获取命名空间连接并注入上下文
        try:
            connection = await manager.get_connection(namespace)

            # 创建 NamespaceContext 并注入到 request.state
            request.state.ns = NamespaceContext(
                namespace_name=namespace,
                connection=connection,
                manager=manager
            )

            logger.debug(f"已为请求 {path} 注入命名空间上下文: {namespace}")

        except ValueError as e:
            # 命名空间不存在或配置错误
            logger.warning(f"命名空间 '{namespace}' 不存在或配置错误: {e}")
            return JSONResponse(
                status_code=404,
                content={"detail": f"命名空间 '{namespace}' 不存在或配置错误"}
            )
        except Exception as e:
            # 其他错误（数据库连接失败等）
            logger.error(f"获取命名空间 '{namespace}' 连接失败: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": f"获取命名空间连接失败: {str(e)}"}
            )

        # 6. 调用下一个处理器
        response = await call_next(request)
        return response
