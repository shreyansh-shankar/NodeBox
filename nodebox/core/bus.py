from PyQt6.QtCore import QObject, pyqtSignal


class PerformanceEventBus(QObject):
    """Singleton event bus to broadcast app performance metrics."""

    metrics_signal = pyqtSignal(dict)


_instance = None


def get_performance_bus() -> PerformanceEventBus:
    global _instance
    if _instance is None:
        _instance = PerformanceEventBus()
    return _instance


__all__ = ["PerformanceEventBus", "get_performance_bus"]
