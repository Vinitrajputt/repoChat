# utils/animations.py
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

def fade_in(widget):
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(500)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    animation.start()

def slide_in(widget):
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(300)
    animation.setStartValue(widget.pos().y() + 50)
    animation.setEndValue(widget.pos())
    animation.setEasingCurve(QEasingCurve.Type.OutBounce)
    animation.start()