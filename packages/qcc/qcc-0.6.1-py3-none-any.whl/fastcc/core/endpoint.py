"""Endpoint 配置模型"""

import asyncio
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .config import ConfigProfile


class Endpoint:
    """Endpoint 配置模型

    代表一个 API endpoint，包含 URL、API Key、权重、优先级等配置信息。
    支持从现有 ConfigProfile 创建，记录来源配置以便追溯。

    注意：endpoint 的唯一性由 (base_url, api_key) 决定，ID 基于这两者的哈希值生成。
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        weight: int = 100,
        priority: int = 1,
        enabled: bool = True,
        max_failures: int = 3,
        timeout: int = 30,
        source_profile: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """初始化 Endpoint

        Args:
            base_url: API 基础 URL
            api_key: API Key
            weight: 权重，用于负载均衡 (默认 100)
            priority: 优先级，数字越小优先级越高 (默认 1)
            enabled: 是否启用 (默认 True)
            max_failures: 最大连续失败次数阈值 (默认 3)
            timeout: 请求超时时间/秒 (默认 30)
            source_profile: 来源配置名称（用于追溯从哪个配置复用）
            metadata: 额外的元数据信息
        """
        # 基于 base_url + api_key 生成稳定的 ID（确保相同的配置得到相同的 ID）
        self.id = self._generate_stable_id(base_url, api_key)
        self.base_url = base_url
        self.api_key = api_key
        self.weight = weight
        self.priority = priority
        self.enabled = enabled
        self.max_failures = max_failures
        self.timeout = timeout
        self.source_profile = source_profile
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()

        # 健康状态
        self.health_status = {
            'status': 'unknown',  # unknown, healthy, degraded, unhealthy
            'last_check': None,
            'consecutive_failures': 0,
            'total_requests': 0,
            'failed_requests': 0,
            'success_rate': 100.0,
            'avg_response_time': 0,
            'last_error': None  # 最后一次错误信息
        }

        # 异步锁：写操作加锁，读操作不加锁
        # 用于保护 health_status 和 enabled 字段的并发修改
        self._lock = asyncio.Lock()

    @staticmethod
    def _generate_stable_id(base_url: str, api_key: str) -> str:
        """基于 base_url 和 api_key 生成稳定的唯一 ID

        Args:
            base_url: API 基础 URL
            api_key: API Key

        Returns:
            8 字符的稳定 ID
        """
        # 使用 SHA256 哈希确保唯一性和稳定性
        content = f"{base_url}|{api_key}".encode('utf-8')
        hash_value = hashlib.sha256(content).hexdigest()
        return hash_value[:8]  # 取前 8 个字符作为短 ID

    def to_dict(self, include_health_status: bool = False) -> Dict[str, Any]:
        """转换为字典（用于序列化）

        Args:
            include_health_status: 是否包含健康状态（默认 False，因为健康状态应该只保存在内存中）

        Returns:
            包含配置信息的字典
        """
        result = {
            'id': self.id,
            'base_url': self.base_url,
            'api_key': self.api_key,
            'weight': self.weight,
            'priority': self.priority,
            'enabled': self.enabled,
            'max_failures': self.max_failures,
            'timeout': self.timeout,
            'source_profile': self.source_profile,
            'metadata': self.metadata,
            'created_at': self.created_at
        }

        # 只在明确要求时才包含健康状态（用于 API 响应等场景）
        if include_health_status:
            result['health_status'] = self.health_status

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Endpoint':
        """从字典创建 Endpoint（用于反序列化）

        Args:
            data: 包含配置信息的字典

        Returns:
            Endpoint 实例
        """
        endpoint = cls(
            base_url=data['base_url'],
            api_key=data['api_key'],
            weight=data.get('weight', 100),
            priority=data.get('priority', 1),
            enabled=data.get('enabled', True),
            max_failures=data.get('max_failures', 3),
            timeout=data.get('timeout', 30),
            source_profile=data.get('source_profile'),
            metadata=data.get('metadata', {})
        )
        endpoint.id = data.get('id', endpoint.id)
        endpoint.created_at = data.get('created_at', endpoint.created_at)
        # 注意：不从持久化数据加载 health_status，每次启动时都使用新的初始状态
        # 这样可以确保状态是实时的，不会受到旧数据的影响
        return endpoint

    @classmethod
    def from_profile(cls, profile: 'ConfigProfile', **kwargs) -> 'Endpoint':
        """从配置档案创建 Endpoint

        这个方法支持"配置复用"功能，可以快速从现有配置创建 endpoint。

        Args:
            profile: 源配置档案
            **kwargs: 覆盖参数（weight, priority 等）

        Returns:
            新创建的 Endpoint 实例

        Example:
            >>> profile = config_manager.get_profile("work")
            >>> endpoint = Endpoint.from_profile(profile, weight=50, priority=2)
        """
        # 默认参数
        endpoint_kwargs = {
            'base_url': profile.base_url,
            'api_key': profile.api_key,
            'source_profile': profile.name,
            'metadata': {
                'source_description': profile.description,
                'imported_at': datetime.now().isoformat()
            }
        }

        # 合并用户提供的覆盖参数
        endpoint_kwargs.update(kwargs)

        return cls(**endpoint_kwargs)

    def display_info(self, show_full_key: bool = False) -> str:
        """生成显示信息

        Args:
            show_full_key: 是否显示完整的 API Key（默认脱敏）

        Returns:
            格式化的信息字符串
        """
        status_icon = {
            'healthy': '✓',
            'degraded': '⚠',
            'unhealthy': '✗',
            'unknown': '?'
        }.get(self.health_status['status'], '?')

        enabled_icon = '✓' if self.enabled else '✗'

        api_key_display = (
            self.api_key if show_full_key
            else f"{self.api_key[:10]}...{self.api_key[-4:]}"
        )

        info = [
            f"ID: {self.id}",
            f"URL: {self.base_url}",
            f"Key: {api_key_display}",
            f"权重: {self.weight}",
            f"优先级: {self.priority}",
            f"启用: {enabled_icon}",
            f"健康: {status_icon}",
        ]

        if self.source_profile:
            info.append(f"来源: {self.source_profile}")

        return " | ".join(info)

    async def update_health_status(
        self,
        status: Optional[str] = None,
        increment_requests: bool = False,
        is_failure: bool = False,
        response_time: Optional[float] = None,
        error_message: Optional[str] = None
    ):
        """更新健康状态（异步方法，使用写锁保护）

        Args:
            status: 新的健康状态 ('healthy', 'degraded', 'unhealthy')
            increment_requests: 是否增加请求计数
            is_failure: 是否为失败请求
            response_time: 响应时间（毫秒）
            error_message: 错误信息（可选）
        """
        async with self._lock:
            if status:
                self.health_status['status'] = status

            self.health_status['last_check'] = datetime.now().isoformat()

            if increment_requests:
                self.health_status['total_requests'] += 1

                if is_failure:
                    self.health_status['failed_requests'] += 1
                    self.health_status['consecutive_failures'] += 1
                    # 记录错误信息
                    if error_message:
                        self.health_status['last_error'] = error_message
                else:
                    self.health_status['consecutive_failures'] = 0
                    # 成功时清除错误信息
                    self.health_status['last_error'] = None

                # 更新成功率
                if self.health_status['total_requests'] > 0:
                    success_count = (self.health_status['total_requests'] -
                                   self.health_status['failed_requests'])
                    self.health_status['success_rate'] = (
                        success_count / self.health_status['total_requests'] * 100
                    )

            if response_time is not None:
                # 使用简单移动平均更新响应时间
                current_avg = self.health_status['avg_response_time']
                total = self.health_status['total_requests']

                if total > 0:
                    self.health_status['avg_response_time'] = (
                        (current_avg * (total - 1) + response_time) / total
                    )
                else:
                    self.health_status['avg_response_time'] = response_time

    def is_healthy(self) -> bool:
        """检查 endpoint 是否健康

        Returns:
            True 如果健康，False 否则
        """
        # 如果被禁用，立即返回 False
        if not self.enabled:
            return False

        # 如果状态明确标记为 unhealthy，立即返回 False
        if self.health_status['status'] == 'unhealthy':
            return False

        # 如果连续失败次数达到阈值，返回 False
        if self.health_status['consecutive_failures'] >= self.max_failures:
            return False

        # 只有 healthy 或 unknown 状态才认为是健康的
        return self.health_status['status'] in ['healthy', 'unknown']

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Endpoint({self.id}, {self.base_url}, enabled={self.enabled})"

    def __eq__(self, other) -> bool:
        """相等性比较（基于 base_url 和 api_key）"""
        if not isinstance(other, Endpoint):
            return False
        return (self.base_url == other.base_url and
                self.api_key == other.api_key)

    def __hash__(self) -> int:
        """哈希值（用于去重）"""
        return hash((self.base_url, self.api_key))
