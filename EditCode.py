#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==============================================================================
# Nazwa pliku: EditCode.py
# 
# Copyright (c) 2026 Daniel Kaliski
# Ten kod jest objęty licencją GNU GENERAL PUBLIC LICENSE GPL-3.0.
# Pełny tekst licencji znajduje się w pliku LICENSE lub na stronie:
# https://opensource.org/license/gpl-3.0
# ==============================================================================

import sys
import os
import platform
import json
import base64
import tempfile

os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, 
                             QVBoxLayout, QWidget, QSplitter, 
                             QTreeView, QPlainTextEdit, QLabel,
                             QTabWidget, QDialog, QPushButton, QHBoxLayout, QFrame,
                             QAbstractButton, QMessageBox, QTabBar)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QFileSystemModel, QFont, QAction, QColor, QPalette
from PyQt6.QtCore import Qt, QProcess, QLocale
from PyQt6.QtGui import QFileSystemModel, QFont, QAction, QColor, QPalette, QIcon

SVG_CLOSE = '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M 2 2 L 8 8 M 8 2 L 2 8" stroke="#888888" stroke-width="1.5" stroke-linecap="round"/></svg>'
SVG_CLOSE_HOVER = '<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M 2 2 L 8 8 M 8 2 L 2 8" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/></svg>'

temp_dir = tempfile.gettempdir()
close_icon_path = os.path.join(temp_dir, "editcode_close.svg").replace('\\', '/')
close_hover_icon_path = os.path.join(temp_dir, "editcode_close_hover.svg").replace('\\', '/')

with open(close_icon_path, "w", encoding="utf-8") as f: 
    f.write(SVG_CLOSE)
with open(close_hover_icon_path, "w", encoding="utf-8") as f: 
    f.write(SVG_CLOSE_HOVER)

def detect_language():
    lang_code = QLocale.system().name()
    return 'pl' if lang_code.lower().startswith('pl') else 'en'

LANG = detect_language()

T = {
    'pl': {
        'file': 'Plik', 'new': 'Nowy', 'open_file': 'Otwórz plik...',
        'open_folder': 'Otwórz folder projektu...', 'save': 'Zapisz',
        'exit': 'Wyjdź', 'tools': 'Narzędzia', 'run': '▶ Uruchom', 'stop': '⏹ Zatrzymaj',
        'help': 'Pomoc', 'about': 'O programie EditCode',
        'new_file': 'Nowy plik', 'terminal': ' Terminal',
        'unsaved_title': 'Niezapisane zmiany',
        'unsaved_tab': "Karta '{}' zawiera niezapisane zmiany.\nCzy na pewno chcesz ją zamknąć bez zapisu?",
        'unsaved_exit': 'Masz niezapisane pliki. Wyjść bez zapisywania?',
        'save_before_run': 'Zapisz plik przed uruchomieniem.', 'error': 'Błąd',
        'yes': 'Tak', 'no': 'Nie', 'cancel': 'Anuluj', 'ok': 'OK',
        'select_folder': 'Wybierz folder projektu', 'all_files': 'Wszystkie pliki (*)',
        'welcome': '# Witaj w EditCode!\n',
        'run_msg': '\n[EditCode] Uruchamianie: {}\n',
        'stop_msg': '\n[EditCode] Wymuszono zatrzymanie procesu.\n',
        'no_run_support': '\n--- Brak obsługi uruchamiania dla rozszerzenia {} ---\n',
        'doc_def': 'Definiuje nową funkcję', 'doc_print': 'Wypisuje tekst na konsolę',
        'doc_if': 'Główny blok uruchomieniowy skryptu', 'doc_for': 'Pętla for',
        'close_tab_btn': 'Zamknij zakładkę'
    },
    'en': {
        'file': 'File', 'new': 'New', 'open_file': 'Open File...',
        'open_folder': 'Open Folder...', 'save': 'Save',
        'exit': 'Exit', 'tools': 'Tools', 'run': '▶ Run', 'stop': '⏹ Stop',
        'help': 'Help', 'about': 'About EditCode',
        'new_file': 'Untitled', 'terminal': ' Terminal',
        'unsaved_title': 'Unsaved Changes',
        'unsaved_tab': "Tab '{}' has unsaved changes.\nAre you sure you want to close it?",
        'unsaved_exit': 'You have unsaved files. Exit without saving?',
        'save_before_run': 'Save the file before running.', 'error': 'Error',
        'yes': 'Yes', 'no': 'No', 'cancel': 'Cancel', 'ok': 'OK',
        'select_folder': 'Select Project Folder', 'all_files': 'All Files (*)',
        'welcome': '# Welcome to EditCode!\n',
        'run_msg': '\n[EditCode] Running: {}\n',
        'stop_msg': '\n[EditCode] Process forcefully stopped.\n',
        'no_run_support': '\n--- No run support for {} ---\n',
        'doc_def': 'Defines a new function', 'doc_print': 'Prints text to console',
        'doc_if': 'Main execution block', 'doc_for': 'For loop',
        'close_tab_btn': 'Close Tab'
    }
}[LANG]

class CustomDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog { background-color: #252525; border: 1px solid #555555; }
            QLabel { color: #ffffff; font-size: 12px; }
            QPushButton { 
                background-color: #3a3a3a; color: #ffffff; 
                border: 1px solid #555555; border-radius: 4px; padding: 6px 16px; 
            }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #2a2a2a; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        msg_label = QLabel(message)
        layout.addWidget(msg_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch() 
        
        yes_btn = QPushButton(T['yes'])
        no_btn = QPushButton(T['no'])
        
        yes_btn.clicked.connect(lambda: self.done(1))
        no_btn.clicked.connect(lambda: self.done(0))
        
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)

MONACO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <style> body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; background-color: #1e1e1e; } </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.40.0/min/vs/loader.min.js"></script>
</head>
<body>
    <div id="editor" style="width: 100%; height: 100%;"></div>
    <script>
        function b64DecodeUnicode(str) {
            if (!str) return "";
            return decodeURIComponent(atob(str).split('').map(function(c) {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
        }

        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.40.0/min/vs' }});
        var editor;
        require(['vs/editor/editor.main'], function() {
            monaco.languages.registerCompletionItemProvider('python', {
                provideCompletionItems: function(model, position) {
                    var suggestions = [
                        { label: 'def_function', kind: monaco.languages.CompletionItemKind.Snippet, insertText: ['def ${1:nazwa}(${2:args}):', '\\t${3:pass}'].join('\\n'), insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: '__DOC_DEF__' },
                        { label: 'print', kind: monaco.languages.CompletionItemKind.Function, insertText: 'print(${1:wartosc})', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: '__DOC_PRINT__' },
                        { label: 'if_main', kind: monaco.languages.CompletionItemKind.Snippet, insertText: ['if __name__ == "__main__":', '\\t${1:main()}'].join('\\n'), insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: '__DOC_IF__' },
                        { label: 'for_loop', kind: monaco.languages.CompletionItemKind.Snippet, insertText: ['for ${1:element} in ${2:kolekcja}:', '\\t${3:pass}'].join('\\n'), insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: '__DOC_FOR__' }
                    ];
                    return { suggestions: suggestions };
                }
            });

            var fileContent = b64DecodeUnicode('__B64_CONTENT__');

            editor = monaco.editor.create(document.getElementById('editor'), {
                value: fileContent,
                language: '__INITIAL_LANG__',
                theme: 'vs-dark',
                automaticLayout: true
            });

            editor.onDidChangeModelContent(function() { document.title = "MODIFIED"; });
        });
        function getEditorContent() { return editor.getValue(); }
        function setEditorSaved() { document.title = "SAVED"; }
    </script>
</body>
</html>
"""

MONACO_HTML = MONACO_HTML.replace('__DOC_DEF__', T['doc_def'])\
                         .replace('__DOC_PRINT__', T['doc_print'])\
                         .replace('__DOC_IF__', T['doc_if'])\
                         .replace('__DOC_FOR__', T['doc_for'])

class EditCode(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EditCode")
        self.resize(1200, 800)
        self.center_window()
        
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setContentsMargins(0, 0, 0, 0)
        
        self.setStyleSheet("""
            QMainWindow, QWidget#centralwidget, QFrame { 
                background-color: #121212; 
                border: none; 
                margin: 0; 
                padding: 0; 
                outline: none;
            }
            QToolTip {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555555;
            }
        """)

        central_widget = QFrame()
        central_widget.setObjectName("centralwidget")
        central_widget.setFrameShape(QFrame.Shape.NoFrame)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        self.setCentralWidget(central_widget)

        self.custom_toolbar = QFrame()
        self.custom_toolbar.setStyleSheet("background-color: #121212; border: none; outline: none;")
        toolbar_layout = QHBoxLayout(self.custom_toolbar)
        toolbar_layout.setContentsMargins(10, 6, 10, 6) 
        toolbar_layout.setSpacing(10)

        run_btn = QPushButton(T['run'])
        run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        run_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus) # <--- USUWA NIEBIESKĄ OBWÓDKĘ
        run_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d; color: #ffffff; 
                border: none; border-radius: 4px; padding: 6px 14px;
            }
            QPushButton:hover { background-color: #3d3d3d; }
            QPushButton:pressed { background-color: #555555; }
        """)
        run_btn.clicked.connect(self.run_code)

        stop_btn = QPushButton(T['stop'])
        stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        stop_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus) # <--- USUWA NIEBIESKĄ OBWÓDKĘ
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d; color: #ffffff; 
                border: none; border-radius: 4px; padding: 6px 14px;
            }
            QPushButton:hover { background-color: #3d3d3d; }
            QPushButton:pressed { background-color: #555555; }
        """)
        stop_btn.clicked.connect(self.stop_code)

        toolbar_layout.addWidget(run_btn)
        toolbar_layout.addWidget(stop_btn)
        toolbar_layout.addStretch() 

        central_layout.addWidget(self.custom_toolbar)

        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical)

        splitter_style = "QSplitter { border: none; } QSplitter::handle { background-color: #121212; border: none; }"
        self.horizontal_splitter.setStyleSheet(splitter_style)
        self.horizontal_splitter.setHandleWidth(0) 
        self.vertical_splitter.setStyleSheet(splitter_style)
        self.vertical_splitter.setHandleWidth(0)   

        central_layout.addWidget(self.horizontal_splitter)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("") 
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setHeaderHidden(True) 
        self.tree_view.hide() 
        
        for i in range(1, 4):
            self.tree_view.setColumnHidden(i, True)
        self.tree_view.doubleClicked.connect(self.on_file_double_clicked)
        self.tree_view.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; border: none; outline: none;")

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True) 
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.tabs.setStyleSheet(f"""
            QTabWidget {{ background: #121212; border: none; margin: 0; padding: 0; }}
            QTabWidget::pane {{ border: none; background: #1e1e1e; top: 0px; }}
            QTabBar {{ background: #121212; border: none; qproperty-drawBase: 0; }}
            QTabWidget::tab-bar {{ alignment: left; border: none; }}
            
            QTabBar::tab {{ 
                background: #121212; color: #888888; 
                padding: 10px 15px 10px 24px; 
                border: none;
                border-top-left-radius: 8px; border-top-right-radius: 8px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{ 
                background: #1e1e1e; color: #ffffff; 
                border: none;
            }}
            QTabBar::tab:hover:!selected {{ color: #dddddd; background: #1a1a1a; }}
            
            QTabBar::tab:last {{
                background: transparent;
                padding: 10px 16px;
                margin-left: 2px;
                font-size: 18px;
                font-weight: bold;
                color: #888888;
            }}
            QTabBar::tab:last:hover {{
                color: #ffffff;
                background: transparent;
            }}
            
            QTabBar::close-button {{
                image: url("{close_icon_path}");
                subcontrol-position: left center;
                margin-left: 8px; width: 12px; height: 12px;
                background: transparent; border: none;
            }}
            QTabBar::close-button:hover {{ 
                image: url("{close_hover_icon_path}");
                background: transparent; 
            }}
        """)

        self.plus_tab = QWidget()
        self.tabs.addTab(self.plus_tab, "+")
        self.tabs.setTabToolTip(0, T['new_file'])
        self.remove_plus_close_button()

        self.terminal_box = QFrame()
        self.terminal_box.setFrameShape(QFrame.Shape.NoFrame)
        terminal_layout = QVBoxLayout(self.terminal_box)
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(0)
        
        terminal_label = QLabel(T['terminal'])
        terminal_label.setStyleSheet("background-color: #121212; color: #aaaaaa; padding: 6px; border: none;")
        
        self.terminal_output = QPlainTextEdit()
        self.terminal_output.setFont(QFont("Courier New", 10))
        self.terminal_output.setStyleSheet("background-color: #121212; color: #00FF00; border: none; padding: 4px; outline: none;")
        
        terminal_layout.addWidget(terminal_label)
        terminal_layout.addWidget(self.terminal_output)

        self.horizontal_splitter.addWidget(self.tree_view)
        self.horizontal_splitter.addWidget(self.vertical_splitter)
        self.vertical_splitter.addWidget(self.tabs)
        self.vertical_splitter.addWidget(self.terminal_box)
        self.vertical_splitter.setSizes([600, 200])
        self.horizontal_splitter.setSizes([250, 950])

        self.terminal_process = QProcess(self)
        self.terminal_process.readyReadStandardOutput.connect(self.read_terminal_output)
        self.terminal_process.readyReadStandardError.connect(self.read_terminal_error)
        self.start_system_terminal()
        self.terminal_output.installEventFilter(self)

        self.create_menu()
      
        self.new_file()
   
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.on_tab_changed(self.tabs.currentIndex())
        
    def remove_plus_close_button(self):
        """Siłowo usuwa krzyżyk zamykający z ostatniej zakładki (tej ze znakiem +)"""
        last_idx = self.tabs.count() - 1
        if last_idx >= 0 and self.tabs.tabText(last_idx) == "+":
            self.tabs.tabBar().setTabButton(last_idx, QTabBar.ButtonPosition.RightSide, None)
            self.tabs.tabBar().setTabButton(last_idx, QTabBar.ButtonPosition.LeftSide, None)

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def create_menu(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True) 
        
        file_menu = menubar.addMenu(T['file'])
        
        new_act = file_menu.addAction(T['new'])
        new_act.setShortcut("Ctrl+N")
        new_act.triggered.connect(self.new_file)

        open_act = file_menu.addAction(T['open_file'])
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self.open_file)
        
        open_folder_act = file_menu.addAction(T['open_folder'])
        open_folder_act.triggered.connect(self.open_folder)

        self.save_act = file_menu.addAction(T['save'])
        self.save_act.setShortcut("Ctrl+S")
        self.save_act.triggered.connect(self.save_file)
        
        file_menu.addSeparator()
        
        exit_act = file_menu.addAction(T['exit'])
        exit_act.triggered.connect(self.close)

        help_menu = menubar.addMenu(T['help'])
        about_act = help_menu.addAction(T['about'])
        about_act.setMenuRole(QAction.MenuRole.AboutRole)
        about_act.triggered.connect(self.show_about)

    def show_about(self):
        if platform.system() == "Darwin":
            try:
                import ctypes
                import ctypes.util
                objc_path = ctypes.util.find_library('objc')
                objc = ctypes.cdll.LoadLibrary(objc_path)
                objc.objc_getClass.restype = ctypes.c_void_p
                objc.sel_registerName.restype = ctypes.c_void_p
                
                NSApplication_class = objc.objc_getClass(b"NSApplication")
                sharedApp_sel = objc.sel_registerName(b"sharedApplication")
                orderFront_sel = objc.sel_registerName(b"orderFrontStandardAboutPanel:")
                
                msgSend_shared = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
                msgSend_about = ctypes.cast(objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
                
                sharedApp = msgSend_shared(NSApplication_class, sharedApp_sel)
                msgSend_about(sharedApp, orderFront_sel, None)
                return 
            except Exception as e:
                pass 
                
        text = (
            "<h3>EditCode</h3>"
            "<p>Wersja 1.0.0<br>Lekkie środowisko programistyczne.</p>"
            "<p>Copyright © 2026 Daniel Kaliski.<br>All rights reserved.</p>"
        )
        if LANG == 'en':
            text = (
                "<h3>EditCode</h3>"
                "<p>Version 1.0.0<br>Lightweight IDE.</p>"
                "<p>Copyright © 2026 Daniel Kaliski.<br>All rights reserved.</p>"
            )
            
        QMessageBox.about(self, T['about'], text)

    def create_tab(self, filepath=None, content="", lang="python"):
        browser = QWebEngineView()
        browser.page().setBackgroundColor(QColor("#1e1e1e"))
        browser.setStyleSheet("border: none; outline: none;")
        
        browser.filepath = filepath
        browser.is_modified = False
        
        b64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        html = MONACO_HTML.replace('__B64_CONTENT__', b64_content).replace('__INITIAL_LANG__', lang)
        
        browser.setHtml(html)
        browser.titleChanged.connect(lambda title, b=browser: self.on_tab_title_changed(b, title))
        
        tab_title = os.path.basename(filepath) if filepath else T['new_file']
        
        insert_idx = self.tabs.count() - 1
        if insert_idx < 0: 
            insert_idx = 0
            
        index = self.tabs.insertTab(insert_idx, browser, tab_title)
        self.tabs.setCurrentIndex(index)
        
        self.remove_plus_close_button()
        
        for btn in self.tabs.tabBar().findChildren(QAbstractButton):
            btn.setToolTip(T['close_tab_btn'])
            
        return browser

    def on_tab_title_changed(self, browser, title):
        if title == "MODIFIED" and not browser.is_modified:
            browser.is_modified = True
            index = self.tabs.indexOf(browser)
            if index != -1:
                current_text = self.tabs.tabText(index)
                if not current_text.endswith("*"):
                    self.tabs.setTabText(index, current_text + "*")

    def close_tab(self, index):
        if self.tabs.tabText(index) == "+": 
            return 
            
        browser = self.tabs.widget(index)
        
        if browser.is_modified:
            filename = os.path.basename(browser.filepath) if browser.filepath else T['new_file']
            dialog = CustomDialog(T['unsaved_title'], T['unsaved_tab'].format(filename), self)
            if dialog.exec() == 0: 
                return

        self.tabs.removeTab(index)
        browser.deleteLater()

        if self.tabs.count() == 1 and self.tabs.tabText(0) == "+":
            self.close()
        else:
            self.remove_plus_close_button()

    def on_tab_changed(self, index):
        if index == -1: return

        if self.tabs.tabText(index) == "+":
            if self.tabs.count() > 1:
                self.tabs.setCurrentIndex(self.tabs.count() - 2)
            self.new_file()
            return

        browser = self.tabs.widget(index)
        if hasattr(browser, 'filepath'):
            title = browser.filepath if browser.filepath else T['new_file']
            self.setWindowTitle(f"EditCode - {title}")

    def run_code(self):
        index = self.tabs.currentIndex()
        if index == -1 or self.tabs.tabText(index) == "+": return
        
        browser = self.tabs.widget(index)
        
        if browser.is_modified or not browser.filepath:
            dialog = CustomDialog(T['save'], T['save_before_run'], self)
            dialog.exec() 
            self.save_file(run_after_save=True)
            return

        self.execute_command(browser.filepath)

    def execute_command(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        cmd = ""
        
        if ext == '.py':
            if getattr(sys, 'frozen', False):
                if platform.system() == "Darwin": 
                    if os.path.exists("/usr/local/bin/python3"):
                        python_exec = "/usr/local/bin/python3"
                    elif os.path.exists("/opt/homebrew/bin/python3"):
                        python_exec = "/opt/homebrew/bin/python3"
                    else:
                        python_exec = "python3"
                elif platform.system() == "Windows":
                    python_exec = "python"
                else:
                    python_exec = "python3"
            else:
                python_exec = sys.executable
                
            cmd = f'"{python_exec}" -u "{filepath}"'
        elif ext == '.js':
            cmd = f'node "{filepath}"'
        elif ext in ['.sh', '.bat']:
            cmd = f'"{filepath}"'
        else:
            self.terminal_output.appendPlainText(T['no_run_support'].format(ext))
            return

        self.terminal_output.appendPlainText(T['run_msg'].format(cmd))
        self.terminal_process.write((cmd + "\n").encode('utf-8'))

    def stop_code(self):
        self.terminal_output.appendPlainText(T['stop_msg'])
        self.terminal_process.kill()
        self.terminal_process.waitForFinished()
        self.start_system_terminal()

    def new_file(self):
        self.create_tab(filepath=None, content=T['welcome'], lang='python')

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, T['select_folder'])
        if folder_path:
            self.tree_view.setRootIndex(self.file_model.setRootPath(folder_path))
            self.tree_view.show()
            cd_cmd = f"cd '{folder_path}'\n"
            self.terminal_process.write(cd_cmd.encode())

    def on_file_double_clicked(self, index):
        filepath = self.file_model.filePath(index)
        if os.path.isfile(filepath):
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "+": continue 
                browser = self.tabs.widget(i)
                if browser.filepath == filepath:
                    self.tabs.setCurrentIndex(i)
                    return
            self.load_file_into_editor(filepath)

    def get_language_from_extension(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        mapping = {
            '.py': 'python', '.js': 'javascript', '.html': 'html',
            '.css': 'css', '.cpp': 'cpp', '.c': 'c', '.json': 'json',
            '.md': 'markdown'
        }
        return mapping.get(ext, 'plaintext')

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, T['open_file'], "", T['all_files'])
        if filepath:
            self.load_file_into_editor(filepath)

    def load_file_into_editor(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            lang = self.get_language_from_extension(filepath)
            self.create_tab(filepath=filepath, content=content, lang=lang)
        except Exception as e:
            dialog = CustomDialog(T['error'], T['open_error'].format(e), self)
            dialog.exec()

    def save_file(self, run_after_save=False):
        index = self.tabs.currentIndex()
        if index == -1 or self.tabs.tabText(index) == "+": return
        
        browser = self.tabs.widget(index)
        
        if not browser.filepath:
            filepath, _ = QFileDialog.getSaveFileName(self, T['save'], "", T['all_files'])
            if not filepath: return
            browser.filepath = filepath
            self.tabs.setTabText(index, os.path.basename(filepath))

        def write_to_disk(content):
            try:
                with open(browser.filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                browser.is_modified = False
                browser.page().runJavaScript("setEditorSaved();")
                
                self.tabs.setTabText(self.tabs.indexOf(browser), os.path.basename(browser.filepath))
                self.setWindowTitle(f"EditCode - {browser.filepath}")
                
                if run_after_save:
                    self.execute_command(browser.filepath)
                    
            except Exception as e:
                dialog = CustomDialog(T['error'], T['save_error'].format(e), self)
                dialog.exec()

        browser.page().runJavaScript("getEditorContent();", write_to_disk)

    def start_system_terminal(self):
        sys_type = platform.system()
        if sys_type == "Windows":
            self.terminal_process.start("powershell.exe", ["-NoExit"])
        elif sys_type == "Darwin":
            self.terminal_process.start("/bin/zsh", ["-i"])
        else:
            self.terminal_process.start("/bin/bash", ["-i"])

    def read_terminal_output(self):
        data = self.terminal_process.readAllStandardOutput().data().decode(errors='replace')
        self.terminal_output.insertPlainText(data)
        self.terminal_output.ensureCursorVisible()

    def read_terminal_error(self):
        data = self.terminal_process.readAllStandardError().data().decode(errors='replace')
        self.terminal_output.insertPlainText(data)
        self.terminal_output.ensureCursorVisible()

    def eventFilter(self, obj, event):
        if obj == self.terminal_output and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                cursor = self.terminal_output.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.terminal_output.setTextCursor(cursor)
                
                lines = self.terminal_output.toPlainText().split('\n')
                last_line = lines[-1] if lines else ""
                command = last_line.strip()
                
                self.terminal_process.write((command + "\n").encode())
                self.terminal_output.insertPlainText("\n")
                return True 
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "+": continue 
            
            browser = self.tabs.widget(i)
            if browser.is_modified:
                self.tabs.setCurrentIndex(i)
                dialog = CustomDialog(T['exit'], T['unsaved_exit'], self)
                if dialog.exec() == 0:
                    event.ignore()
                    return

        self.terminal_process.kill()
        self.terminal_process.waitForFinished()
        event.accept()

if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            import ctypes
            myappid = u'com.danielkaliski.editcode.1.0.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    if hasattr(sys, '_MEIPASS'):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(os.path.abspath(__file__))
        
    icon_path = os.path.join(basedir, 'icon.ico')
    app_icon = QIcon(icon_path)
    
    app.setWindowIcon(app_icon)
    
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(18, 18, 18))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)
    
    window = EditCode()
    
    window.setWindowIcon(app_icon) 
    
    window.show()
    sys.exit(app.exec())