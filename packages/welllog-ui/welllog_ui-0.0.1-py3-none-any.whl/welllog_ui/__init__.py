from .main_V2 import run_main
from . import services, widgets, tools, config, database_project_dialog, main_V2, libPyBO39

__version__ = '0.0.1'

__all__ = ['run_main', 'services', 'widgets', 'tools', 'config', 'database_project_dialog', 'main_V2', 'libPyBO39']


"""
py -m build
py -m twine check dist/*
py -m twine upload --non-interactive -r pypi dist/*
"""