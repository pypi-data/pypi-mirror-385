"""API 客户端模块."""
import asyncio
import logging
from typing import Any, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class TimesheetAPIClient:
    """工时系统 API 客户端."""

    def __init__(self) -> None:
        """初始化客户端."""
        self.base_url = settings.API_BASE_URL
        self.headers = settings.get_headers()

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        data: Optional[dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> dict[str, Any]:
        """发起 HTTP 请求，支持重试机制.

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE, PATCH)
            endpoint: API 端点路径
            params: URL 查询参数
            data: 请求体数据
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）

        Returns:
            API 响应数据

        Raises:
            Exception: 请求失败错误
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"API 请求尝试 {attempt + 1}/{max_retries + 1}: {method} {url}")
                
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
                ) as client:
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        headers=self.headers,
                        params=params,
                        json=data,
                    )
                    
                    # 检查响应状态
                    if response.status_code == 401:
                        raise Exception("认证失败：Token 可能已过期，请重新生成")
                    elif response.status_code == 403:
                        raise Exception("权限不足：当前用户没有访问此资源的权限")
                    elif response.status_code == 404:
                        raise Exception(f"资源不存在：{endpoint}")
                    elif response.status_code >= 500:
                        raise Exception(f"服务器错误：HTTP {response.status_code}")
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # 检查业务状态码（只对字典类型检查）
                    if isinstance(result, dict):
                        code = result.get("code")
                        if code is not None and code != 0:
                            error_msg = result.get("message", "未知业务错误")
                            raise Exception(f"业务错误: {error_msg}")
                    
                    logger.debug(f"API 请求成功: {method} {url}")
                    return result

            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}"
                try:
                    error_body = e.response.json()
                    if "message" in error_body:
                        last_error = f"{last_error}: {error_body['message']}"
                except Exception:
                    pass
                last_error = f"API 请求失败: {last_error}"
                
            except httpx.RequestError as e:
                last_error = f"网络请求错误: {str(e)}"
                
            except Exception as e:
                # 如果是认证或权限错误，不重试
                if "认证失败" in str(e) or "权限不足" in str(e) or "资源不存在" in str(e):
                    raise e
                last_error = f"未知错误: {str(e)}"

            # 如果不是最后一次尝试，等待后重试
            if attempt < max_retries:
                logger.warning(f"请求失败，{retry_delay}秒后重试: {last_error}")
                await asyncio.sleep(retry_delay * (2 ** attempt))  # 指数退避
            else:
                logger.error(f"所有重试失败: {last_error}")
                raise Exception(last_error)

    async def get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """GET 请求."""
        return await self.request("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """POST 请求."""
        return await self.request("POST", endpoint, params=params, data=data)

    async def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """PUT 请求."""
        return await self.request("PUT", endpoint, params=params, data=data)

    async def delete(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """DELETE 请求."""
        return await self.request("DELETE", endpoint, params=params)

    async def patch(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """PATCH 请求."""
        return await self.request("PATCH", endpoint, params=params, data=data)


# 创建全局客户端实例
api_client = TimesheetAPIClient()
