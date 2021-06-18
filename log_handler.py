import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QPlainTextEdit
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QIcon, QFont
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
        fileMenu.addSeparator()
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
        fileToolBar.addAction(self.newAction)
        fileToolBar.addAction(self.openAction)
        fileToolBar.addAction(self.saveAction)

        editToolBar = QToolBar("Edit", self)
        editToolBar.addAction(self.log_list_Action)
        self.addToolBar(Qt.LeftToolBarArea, editToolBar)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)
        editToolBar.addAction(self.cutAction)

    def _createContextMenu(self):
        # Setting contextMenuPolicy
        self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        # Populating the widget with actions
        self.centralWidget.addAction(self.newAction)
        self.centralWidget.addAction(self.openAction)
        self.centralWidget.addAction(self.saveAction)
        self.centralWidget.addAction(self.copyAction)
        self.centralWidget.addAction(self.pasteAction)
        self.centralWidget.addAction(self.cutAction)

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("New")
        self.newAction.setIcon(QIcon(":file-new.svg"))
        self.log_list_Action = QAction(QIcon(":list.svg"), "Список логов", self)
        self.openAction = QAction(QIcon(":file-open.svg"), "Open...", self)
        self.saveAction = QAction(QIcon(":file-save.svg"), "Save", self)
        self.exitAction = QAction(QIcon(":exit.svg"), "Exit", self)
        # Edit actions
        self.copyAction = QAction(QIcon(":edit-copy.svg"), "Copy", self)
        self.pasteAction = QAction(QIcon(":edit-paste.svg"), "Paste", self)
        self.cutAction = QAction(QIcon(":edit-cut.svg"), "Cut", self)
        self.helpContentAction = QAction("Help Content", self)
        self.aboutAction = QAction("About", self)

    def log_list(self):
        # Logic for creating a new file goes here...
        self.centralWidget.setText("<b>File > Log List</b> clicked")

    def newFile(self):
        # Logic for creating a new file goes here...
        self.centralWidget.setText("<b>File > New</b> clicked")

    def openFile(self):
        # Logic for opening an existing file goes here...
        self.centralWidget.setText("<b>File > Open...</b> clicked")

    def saveFile(self):
        # Logic for saving a file goes here...
        self.centralWidget.setText("<b>File > Save</b> clicked")

    def copyContent(self):
        # Logic for copying content goes here...
        self.centralWidget.setText("<b>Edit > Copy</b> clicked")

    def pasteContent(self):
        # Logic for pasting content goes here...
        self.centralWidget.setText("<b>Edit > Pate</b> clicked")

    def cutContent(self):
        # Logic for cutting content goes here...
        self.centralWidget.setText("<b>Edit > Cut</b> clicked")

    def helpContent(self):
        # Logic for launching help goes here...
        self.centralWidget.setText("<b>Help > Help Content...</b> clicked")

    def about(self):
        # Logic for showing an about dialog content goes here...
        self.centralWidget.setText("<b>Help > About...</b> clicked")

    def _connectActions(self):
        # Connect File actions
        self.log_list_Action.triggered.connect(self.log_list)
        self.newAction.triggered.connect(self.newFile)
        self.openAction.triggered.connect(self.openFile)
        self.saveAction.triggered.connect(self.saveFile)
        self.exitAction.triggered.connect(self.close)
        # Connect Edit actions
        self.copyAction.triggered.connect(self.copyContent)
        self.pasteAction.triggered.connect(self.pasteContent)
        self.cutAction.triggered.connect(self.cutContent)

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.plainTextEdit = QPlainTextEdit()
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setFont(QFont('Arial', 11))

        layoutV = QVBoxLayout()

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self.setWindowTitle("Log Handler")
        self.resize(600, 350)
        self.centralWidget = QLabel("Hello, World")
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)
        self._createContextMenu()
        self._connectActions()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())