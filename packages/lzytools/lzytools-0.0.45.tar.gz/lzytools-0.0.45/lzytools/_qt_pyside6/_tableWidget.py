from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class TabelWidgetHiddenOverLengthText(QTableWidget):
    """文本框控件，自动隐藏长文本（abcd->a...）
    备注：利用tableWidget的文本单元格自动隐藏长文本的特性"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        # 设置列宽度为自动适应控件大小
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # 隐藏行列
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        # 设置为单行单列
        self.setColumnCount(1)
        self.insertRow(0)
        # 固定控件高度、单元格行高
        self.setFixedHeight(18)
        self.setRowHeight(0, 16)
        # 设置文本单元格
        self.item_filename = QTableWidgetItem('')
        self.setItem(0, 0, self.item_filename)
        # 禁止编辑
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        # 禁止选择
        self.setSelectionMode(QTableWidget.NoSelection)
        # 禁止获取焦点
        self.setFocusPolicy(Qt.NoFocus)
        # 设置样式表
        self.setStyleSheet("""
            QTableWidget {
                border: 0px;
                background: transparent;
                gridline-color: transparent;
                selection-background-color: transparent;
            }

            QTableWidget::item {
                border: 0px;
                padding: 0px;
            }

            QHeaderView::section {
                border: 0px;
                background: transparent;
                padding: 0px;
            }
        """)

    def set_text(self, text: str):
        """设置文本"""
        self.item_filename.setText(text)

    def set_height(self, height: int):
        """设置控件高度
        :param height: int，高度"""
        self.setFixedHeight(height)  # 控件高度
        self.setRowHeight(0, height - 2)  # 单元格行高
