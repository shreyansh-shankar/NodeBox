from PyQt6.QtCore import QObject, pyqtSignal


class PerformanceEventBus(QObject):
    """Singleton-like event bus to broadcast app performance metrics.

    Carries aggregated NodeBox-specific metrics so UI components can subscribe
    without tight coupling to execution code.
    """

    metrics_signal = pyqtSignal(dict)


_instance = None


def get_performance_bus() -> PerformanceEventBus:
    global _instance
    if _instance is None:
        _instance = PerformanceEventBus()
    return _instance
