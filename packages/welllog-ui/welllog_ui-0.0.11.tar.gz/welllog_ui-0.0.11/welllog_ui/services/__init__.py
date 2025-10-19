"""
WellLog UI 数据服务包

- 提供数据层抽象，封装 PyBO 相关操作。
- 统一管理 PyBOProject 的全局实例，避免多处重复弹窗与连接。
"""

from typing import Optional, Any, Tuple
from PySide6 import QtWidgets

# from .data_service import DataService
from welllog_ui.services.bowells_service import BOWellsService
from welllog_ui.database_project_dialog import CATCH_PATH

# ==================== 全局 PyBO Project 管理 ====================

GLOBAL_PYBO_PROJECT: Optional[Any] = None
GLOBAL_DB_NAME: Optional[str] = None
GLOBAL_PROJECT_NAME: Optional[str] = None
GLOBAL_DATASERVICE: Optional[BOWellsService] = None
GLOBAL_DATASERVICE_IS_MY: bool = False


def ensure_pybo_project(parent: Optional[QtWidgets.QWidget] = None) -> Optional[Any]:
    """

    """
    global GLOBAL_PYBO_PROJECT, GLOBAL_DB_NAME, GLOBAL_PROJECT_NAME
    if GLOBAL_PYBO_PROJECT is not None:
        return GLOBAL_PYBO_PROJECT

    # 延迟导入以避免循环依赖
    if not GLOBAL_DATASERVICE_IS_MY:
        from welllog_ui.database_project_dialog import show_CPyBOProjectDialog
        GLOBAL_PYBO_PROJECT, GLOBAL_DB_NAME, GLOBAL_PROJECT_NAME = show_CPyBOProjectDialog(parent)
        if GLOBAL_PYBO_PROJECT is not None:
            return GLOBAL_PYBO_PROJECT
    return True if GLOBAL_DATASERVICE_IS_MY else None


def reset_pybo_project(db_name: Optional[str] = None, project_name: Optional[str] = None) -> None:
    """重置全局连接状态。"""
    global GLOBAL_DB_NAME, GLOBAL_PROJECT_NAME
    GLOBAL_PYBO_PROJECT = None
    GLOBAL_DB_NAME = db_name
    GLOBAL_PROJECT_NAME = project_name


def get_pybo_connection_selection() -> Tuple[Optional[str], Optional[str]]:
    """获取全局保存的 (db_name, project_name)。"""
    return GLOBAL_DB_NAME, GLOBAL_PROJECT_NAME


def get_data_service() -> BOWellsService:
    """获取数据服务单例实例。"""
    global GLOBAL_DATASERVICE
    if GLOBAL_DATASERVICE is None and not GLOBAL_DATASERVICE_IS_MY:
        GLOBAL_DATASERVICE = BOWellsService(GLOBAL_DB_NAME, GLOBAL_PROJECT_NAME)
    elif GLOBAL_DATASERVICE is None and GLOBAL_DATASERVICE_IS_MY:
        GLOBAL_DATASERVICE = BOWellsService(is_my=True)
    return GLOBAL_DATASERVICE


__all__ = [
    'BOWellsService', 'get_data_service', 'ensure_pybo_project', 'get_pybo_connection_selection', 'reset_pybo_project',
]
