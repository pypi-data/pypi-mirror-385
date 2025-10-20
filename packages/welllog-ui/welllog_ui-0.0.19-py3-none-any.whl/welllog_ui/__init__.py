# 子模块延迟导入，避免循环依赖
from . import services, widgets, tools
from .main_V2 import run_main
from .database_project_dialog import CPyBOProjectDialog, show_CPyBOProjectDialog, CATCH_PATH
from . import libPyBO39 as pybo
from .config import UIConfig

__version__ = '0.0.19'

__all__ = ['services', 'widgets', 'tools', 'run_main', 'CPyBOProjectDialog', 'show_CPyBOProjectDialog', 'CATCH_PATH', 'pybo', 'UIConfig', '__version__']


"""
py -m build
py -m twine check dist/*
py -m twine upload --non-interactive --config-file .\.pypirc -r pypi dist/*

"""