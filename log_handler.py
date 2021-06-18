import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QIcon
import qrc_resources
from PyQt5.QtWidgets import QAction


class Window(QMainWindow):
    """Main Window."""
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File menu
        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("Edit")
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.cutAction)
        # Help menu
        helpMenu = menuBar.addMenu(QIcon(":alert.svg"), "Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createToolBars(self):
        # Using a title
        fileToolBar = self.addToolBar("File")
        editToolBar = QToolBar("Edit", self)
        self.addToolBar(editToolBar)
        helpToolBar = QToolBar("Help", self)
        self.addToolBar(Qt.LeftToolBarArea, helpToolBar)

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("New")
        # Creating actions using the second constructor
        self.openAction = QAction("Open...", self)
        self.saveAction = QAction("Save", self)
        self.exitAction = QAction("Exit", self)
        self.copyAction = QAction("Copy", self)
        self.pasteAction = QAction("Paste", self)
        self.cutAction = QAction("Cut", self)
        self.helpContentAction = QAction("Help Content", self)
        self.aboutAction = QAction("About", self)



    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self.setWindowTitle("Log Handler")
        self.resize(400, 200)
        self.centralWidget = QLabel("Hello, World")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())