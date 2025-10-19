"""

WellLog UI 组件模块

命名规范：
- C + 类名：返回 Class 对象（如 CPyBOProjectDialog 返回 PyBOProject）
- T + 类名：返回 Tuple（如 TStrDialog 返回 (str, str)）
- S + 类名：返回 String（如 SNameDialog 返回 str）
- B + 类名：返回 Boolean（如 BConfirmDialog 返回 bool）
- L + 类名：返回 List（如 LItemsDialog 返回 List[str]）
- N + 类名：返回 None（如 NInfoDialog 不返回值）

便捷函数命名：show_ + 类型前缀 + 描述
- show_c_pybo_project_dialog() -> PyBOProject
- show_t_str_dialog() -> (str, str)
- show_s_name_dialog() -> str
- show_b_confirm_dialog() -> bool
- show_l_items_dialog() -> List[str]
- show_n_info_dialog() -> None
"""

from welllog_ui.database_project_dialog import CPyBOProjectDialog, show_CPyBOProjectDialog
from welllog_ui.widgets.well_filter_dialog import WellFilterDialog
from welllog_ui.widgets.well_selection_dialog_v2 import WellSelectionDialog
from welllog_ui.widgets.well_curve_plotter_pyqtgraph import WellCurvePlotterPyQtGraph


__all__ = [
    'CPyBOProjectDialog',  # 返回 PyBOProject 对象的对话框
    'show_CPyBOProjectDialog',  # 便捷函数：显示对话框并返回 PyBOProject
    'WellFilterDialog',
    'WellSelectionDialog',  # 统一的井选择对话框
    'WellCurvePlotterPyQtGraph',
]
