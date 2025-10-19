__version__ = "1.1.6"  # Должно совпадать с версией в setup.py
version = "1.1.6"      # Для обратной совместимости

# Явно экспортируем нужные модули
from .xlizard import *
from xlizard.combined_metrics import CombinedMetrics
from xlizard.sourcemonitor_metrics import SourceMonitorMetrics

# Добавляем экспорт игры (inline функции чтобы избежать импорта)
def get_duck_game_script():
    """Returns the JavaScript code for the duck game"""
    return "<!-- Duck game script included in htmloutput -->"

def get_duck_game_css():
    """Returns CSS styles for the duck game"""
    return "<!-- Duck game CSS included in htmloutput -->"

__all__ = [
    'CombinedMetrics', 
    'load_thresholds', 
    'DEFAULT_THRESHOLDS', 
    'Config', 
    'SourceMonitorMetrics',
    'get_duck_game_script', 
    'get_duck_game_css'
]