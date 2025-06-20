from PyQt5.QtWidgets import  QMainWindow, QHeaderView
from descriptionUI_ui import Ui_descWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush

class MainDesc(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_descWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("About App")

        table = self.ui.tableWidget
        vHeader = table.verticalHeader()
        header = table.horizontalHeader()
        if vHeader is not None:
            vHeader.setVisible(False)
        table.setWordWrap(True)

        if header is not None:
            for col in range(table.columnCount() - 1):
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(table.columnCount() - 1, QHeaderView.Stretch)
        
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                    item.setToolTip(item.text())
        table.resizeRowsToContents()

        if header:
            header.setStyleSheet("""
                QHeaderView::section {
                    background-color: black;
                    color: white;
                    font-weight: bold;
                    padding: 4px;
                }
            """)

        row_colors = [
           QColor("green"),
           QColor("yellow"),  
            QColor("orange"),  
            QColor("red"),  
            QColor("purple"), 
            QColor("maroon"),  
        ]
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and row < len(row_colors):
                    item.setBackground(QBrush(QColor(row_colors[row])))

