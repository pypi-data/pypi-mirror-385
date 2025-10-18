# appmaker/browserapp.py
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QToolBar, QAction, QLineEdit, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class BrowserTab(QWidget):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl(url))
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Web Browser")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.switch_tab)
        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        self.add_toolbar_buttons()
        self.add_tab("https://www.google.com")

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #222;
                color: white;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                padding: 4px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #444;
                color: white;
                border-radius: 6px;
                padding: 5px;
            }
            QTabBar::tab {
                background: #333;
                color: white;
                padding: 8px;
                border-radius: 6px;
            }
            QTabBar::tab:selected {
                background: #555;
            }
        """)

    def add_toolbar_buttons(self):
        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        self.toolbar.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.toolbar.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(lambda: self.current_browser().setUrl(QUrl("https://www.google.com")))
        self.toolbar.addAction(home_btn)

        self.toolbar.addWidget(self.urlbar)

        new_tab_btn = QPushButton("+")
        new_tab_btn.clicked.connect(lambda: self.add_tab("https://www.google.com"))
        self.toolbar.addWidget(new_tab_btn)

    def add_tab(self, url="https://www.google.com"):
        new_tab = BrowserTab(url)
        index = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(index)
        new_tab.browser.urlChanged.connect(lambda qurl, i=index: self.update_urlbar(qurl, i))
        new_tab.browser.titleChanged.connect(lambda title, i=index: self.tabs.setTabText(i, title[:20]))

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget:
            widget.deleteLater()
        self.tabs.removeTab(index)
        if self.tabs.count() == 0:
            QApplication.quit()

    def switch_tab(self, index):
        browser = self.current_browser()
        if browser:
            self.update_urlbar(browser.url(), index)
            browser.urlChanged.connect(lambda qurl, i=index: self.update_urlbar(qurl, i))

    def current_browser(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            return current_widget.browser
        return None

    def navigate_to_url(self):
        url = self.urlbar.text()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.current_browser().setUrl(QUrl(url))

    def update_urlbar(self, qurl, index):
        if index != self.tabs.currentIndex():
            return
        self.urlbar.setText(qurl.toString())


# 🔥 This is the function you can call from your main script
def run_browser():
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
