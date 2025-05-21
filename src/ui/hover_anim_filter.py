from PyQt6.QtCore import QObject, QEvent, QPropertyAnimation, QEasingCurve, QSize


class HoverAnimationFilter(QObject):
    """Event filter that scales a widget on hover using QPropertyAnimation."""

    def __init__(self, scale_factor: float = 1.05, duration: int = 150, parent=None):
        super().__init__(parent)
        self.scale_factor = scale_factor
        self.duration = duration
        self._animations = {}

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            self._start_animation(obj, True)
        elif event.type() == QEvent.Type.Leave:
            self._start_animation(obj, False)
        return False

    def _start_animation(self, widget, enlarge: bool):
        base_size = widget.property("_hover_base_size")
        if base_size is None:
            base_size = widget.size()
            widget.setProperty("_hover_base_size", base_size)

        if enlarge:
            target_w = int(base_size.width() * self.scale_factor)
            target_h = int(base_size.height() * self.scale_factor)
        else:
            target_w = base_size.width()
            target_h = base_size.height()

        animation = self._animations.get(widget)
        if not animation:
            animation = QPropertyAnimation(widget, b"size", widget)
            self._animations[widget] = animation

        animation.stop()
        animation.setDuration(self.duration)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.setStartValue(widget.size())
        animation.setEndValue(QSize(target_w, target_h))
        animation.start()
