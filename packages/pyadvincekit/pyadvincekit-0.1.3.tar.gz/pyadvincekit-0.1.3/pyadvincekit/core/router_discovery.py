"""
路由自动发现模块（框架内置）

提供在给定目录下自动扫描并加载 FastAPI APIRouter 的能力。
外部工程只需调用 auto_discover_and_register_routers 即可获取路由列表。
"""

import importlib
import inspect
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter


class RouterDiscovery:
    """路由自动发现器"""

    def __init__(self, api_directory: str = "api") -> None:
        self.api_directory = api_directory
        self.discovered_routers: List[APIRouter] = []

    def discover_routers(self, exclude_files: Optional[List[str]] = None) -> List[APIRouter]:
        if exclude_files is None:
            exclude_files = ["__init__.py"]

        routers: List[APIRouter] = []
        api_path = Path(self.api_directory)
        if not api_path.exists():
            return routers

        for file_path in api_path.glob("*.py"):
            if file_path.name in exclude_files:
                continue

            try:
                module_name = f"{self.api_directory}.{file_path.stem}"
                module = importlib.import_module(module_name)
                router = self._extract_router_from_module(module)
                if router:
                    routers.append(router)
            except Exception:
                # 保持容错，跳过异常模块
                continue

        self.discovered_routers = routers
        return routers

    def _extract_router_from_module(self, module) -> Optional[APIRouter]:
        # 优先 router 变量
        if hasattr(module, "router"):
            router_obj = getattr(module, "router")
            if isinstance(router_obj, APIRouter):
                return router_obj

        # 次选：任意 APIRouter 实例
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, APIRouter):
                return obj
        return None


def auto_discover_and_register_routers(
    api_directory: str = "api",
    exclude_files: Optional[List[str]] = None,
) -> List[APIRouter]:
    discovery = RouterDiscovery(api_directory)
    return discovery.discover_routers(exclude_files)


def discover_routers(api_directory: str = "api") -> List[APIRouter]:
    return auto_discover_and_register_routers(api_directory)




