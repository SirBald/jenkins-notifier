import requests
from PyQt5.QtWidgets import (
    QAction,
    qApp,
    QApplication,
    QCheckBox,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QSizePolicy,
    QSpacerItem,
    QStyle,
    QSystemTrayIcon,
    QWidget
    )
import PyQt5.QtCore as core
from PyQt5.QtGui import QIcon


_ICON_GRAY = None
_ICON_GREEN = None
_ICON_RED = None


_STATUS_SUCCESS = "SUCCESS"
_STATUS_FAILURE = "FAILURE"


_URL = "https://your.build.website/job/jenkins-notifier-job/lastCompletedBuild/api/json/"


def create_icons():
    global _ICON_RED
    global _ICON_GREEN
    global _ICON_GRAY
    _ICON_GRAY = QIcon("icons/gray.png")
    _ICON_GREEN = QIcon("icons/green.png")
    _ICON_RED = QIcon("icons/red.png")


class JenkinsJob:
    def __init__(self, json):
        self.status = json.get("result")
        self.full_display_name = json.get("fullDisplayName")


def jenkins_job_status(url):
    r = {}
    try:
        r = requests.get(url).json()
    finally:
        return JenkinsJob(r)


class NotifierWindow(QMainWindow):
    _job_status = None
    _timer = None
    _tray_icon = None

    # Override the class constructor
    def __init__(self):
        # Be sure to call the super class method
        QMainWindow.__init__(self)

        # self._job_status = StateKeeper(self.changeTrayIcon)

        self.setMinimumSize(core.QSize(480, 80))         # Set sizes
        self.setWindowTitle("Jenkins Notifier")     # Set a title
        central_widget = QWidget(self)              # Create a central widget
        self.setCentralWidget(central_widget)       # Set the central widget

        # Init QSystemTrayIcon
        self._tray_icon = QSystemTrayIcon(self)
        create_icons()
        self._tray_icon.setIcon(_ICON_GRAY)

        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(quit_action)
        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.show()

        self._createTimer()

    def _changeTrayIcon(self, jenkins_job):
        if (self._job_status == jenkins_job.status):
            return
        self._job_status = jenkins_job.status
        icon = _ICON_GRAY
        if (jenkins_job.status == _STATUS_SUCCESS):
            icon = _ICON_GREEN
        elif (jenkins_job.status == _STATUS_FAILURE):
            icon = _ICON_RED
        self._tray_icon.setIcon(icon)
        self._tray_icon.setToolTip(
            "Build {} status {}".format(jenkins_job.full_display_name, jenkins_job.status))
        self._tray_icon.showMessage(
            jenkins_job.status,
            jenkins_job.full_display_name,
            icon,
            1000
        )

    def _createTimer(self):
        self._timer = core.QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._updateJobStatus)
        self._timer.start()

    @core.pyqtSlot()
    def _updateJobStatus(self):
        self._changeTrayIcon(jenkins_job_status(_URL))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    mw = NotifierWindow()
    sys.exit(app.exec())
