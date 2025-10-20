"""
WellLog UI 数据服务包

- 提供数据层抽象，封装 PyBO 相关操作。
- 统一管理 PyBOProject 的全局实例，避免多处重复弹窗与连接。
"""

from .bowells_service import BOWellsService
from .db import get_data_service, ensure_pybo_project, get_pybo_connection_selection, reset_pybo_project


__all__ = ['BOWellsService', 'get_data_service', 'ensure_pybo_project', 'get_pybo_connection_selection', 'reset_pybo_project']
