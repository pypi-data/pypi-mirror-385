
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout
from qfluentwidgets import SubtitleLabel, setFont


class WidgetDemo(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)

        # Must set a globally unique object name for the sub-interface
        self.setObjectName(text.replace(' ', '-'))