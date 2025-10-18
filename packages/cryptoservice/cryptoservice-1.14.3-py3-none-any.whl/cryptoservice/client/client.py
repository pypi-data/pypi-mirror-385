"""Binance API 客户端工厂，用于创建和管理客户端实例."""

import asyncio

from binance import AsyncClient, Client

from cryptoservice.config import get_logger, settings
from cryptoservice.exceptions import MarketDataError

# 使用统一的日志配置
logger = get_logger(__name__)


class BinanceClientFactory:
    """Binance客户端工厂类."""

    _instance: Client | None = None
    _async_instance: AsyncClient | None = None

    @classmethod
    def create_client(cls, api_key: str, api_secret: str) -> Client:
        """创建或获取Binance客户端实例（单例模式）.

        Args:
            api_key: API密钥
            api_secret: API密钥对应的secret

        Returns:
            Client: Binance客户端实例

        Raises:
            MarketDataError: 当客户端初始化失败时抛出
        """
        if not cls._instance:
            try:
                if not api_key or not api_secret:
                    raise ValueError("Missing Binance API credentials")

                # 获取代理配置
                proxies = settings.get_proxy_config()
                if proxies:
                    logger.info(f"使用代理配置: {proxies}")
                    cls._instance = Client(api_key, api_secret, proxies=proxies)
                else:
                    cls._instance = Client(api_key, api_secret)

                logger.info("[green]Successfully created Binance client[/green]")
            except Exception as e:
                logger.error(f"[red]Failed to initialize Binance client: {e}[/red]")
                raise MarketDataError(f"Failed to initialize Binance client: {e}") from e
        return cls._instance

    @classmethod
    async def create_async_client(cls, api_key: str, api_secret: str) -> AsyncClient:
        """创建或获取Binance异步客户端实例（单例模式）.

        Args:
            api_key: API密钥
            api_secret: API密钥对应的secret

        Returns:
            AsyncClient: Binance异步客户端实例

        Raises:
            MarketDataError: 当客户端初始化失败时抛出
        """
        if not cls._async_instance:
            try:
                if not api_key or not api_secret:
                    raise ValueError("Missing Binance API credentials")

                proxies = settings.get_proxy_config()
                https_proxy = None

                if proxies:
                    logger.info(f"配置代理: {proxies}")

                    # 使用 HTTPS 代理
                    if "https" in proxies:
                        https_proxy = proxies["https"]
                        logger.info(f"使用 HTTPS 代理: {https_proxy}")
                    # 如果只有 HTTP 代理，也用作 HTTPS
                    elif "http" in proxies:
                        https_proxy = proxies["http"]
                        logger.info(f"使用 HTTP 代理作为 HTTPS: {https_proxy}")

                # 创建 AsyncClient
                if https_proxy:
                    cls._async_instance = await AsyncClient.create(
                        api_key=api_key, api_secret=api_secret, https_proxy=https_proxy
                    )
                    logger.info("[green]Successfully created Binance async client with HTTPS proxy[/green]")
                else:
                    cls._async_instance = await AsyncClient.create(api_key=api_key, api_secret=api_secret)
                    logger.info("[green]Successfully created Binance async client[/green]")

            except Exception as e:
                logger.error(f"[red]Failed to initialize Binance async client: {e}[/red]")
                raise MarketDataError(f"Failed to initialize Binance async client: {e}") from e
        return cls._async_instance

    @classmethod
    async def close_client(cls, timeout: float = 5.0) -> None:
        """关闭现有的异步客户端会话.

        Args:
            timeout: 关闭连接的超时时间（秒），默认5秒
        """
        if cls._async_instance:
            try:
                # 使用超时控制来避免SSL关闭时长时间挂起
                await asyncio.wait_for(cls._async_instance.close_connection(), timeout=timeout)
            except TimeoutError:
                # SSL连接关闭超时是常见的，特别是在使用代理时
                # 这不影响数据完整性，因为所有操作都已完成
                logger.debug(f"客户端连接关闭超时({timeout}秒)，这是正常的，可以忽略")
            except Exception as e:
                # 捕获其他关闭时的异常，避免影响程序退出
                # 这些通常是网络清理相关的错误，不影响数据完整性
                logger.debug(f"关闭客户端连接时出现异常: {type(e).__name__}, 可以安全忽略")
            finally:
                cls._async_instance = None

        logger.info("[yellow]Binance async client session closed.[/yellow]")

    @classmethod
    def get_client(cls) -> Client | None:
        """获取现有的客户端实例."""
        return cls._instance

    @classmethod
    def reset_client(cls) -> None:
        """重置客户端实例."""
        cls._instance = None
        cls._async_instance = None
