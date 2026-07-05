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

import webview
from webview.menu import Menu, MenuAction
import sys
import os
import subprocess
import threading
import json
import platform

is_pl = False
try:
    if platform.system() == 'Darwin':
        out = subprocess.check_output(['defaults', 'read', '-g', 'AppleLanguages']).decode('utf-8')
        if 'pl' in out:
            is_pl = True
    elif platform.system() == 'Windows':
        import ctypes
        import locale
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        lang = locale.windows_locale.get(lang_id, 'en')
        if lang.lower().startswith('pl'):
            is_pl = True
    else:
        lang = os.environ.get('LANG', 'en')
        if lang.lower().startswith('pl'):
            is_pl = True
except:
    pass

T = {
    'err_open': "Nie można otworzyć pliku:" if is_pl else "Cannot open file:",
    'err_save': "Nie można zapisać pliku:" if is_pl else "Cannot save file:",
    'run_msg': "Uruchamianie:" if is_pl else "Running:",
    'done_msg': "Zakończono (Kod" if is_pl else "Finished (Code",
    'stop_msg': "Wymuszono zatrzymanie procesu." if is_pl else "Process forcefully stopped.",
    'err': "Błąd" if is_pl else "Error"
}

APP_WINDOW = None

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <style>
        :root { --bg: #121212; --panel: #1e1e1e; --text: #fff; --accent: #63bdf2; }
        body, html { margin: 0; padding: 0; height: 100%; display: flex; flex-direction: column; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
        
        #win-menu { display: flex; background: #151515; font-size: 13px; border-bottom: 1px solid #333; user-select: none; }
        .menu-item { position: relative; padding: 8px 14px; cursor: pointer; color: #ccc; }
        .menu-item:hover, .menu-item.active { background: #333; color: #fff; }
        .dropdown { display: none; position: absolute; top: 100%; left: 0; background: #252525; border: 1px solid #444; min-width: 220px; box-shadow: 0 8px 20px rgba(0,0,0,0.6); z-index: 1000; padding: 5px 0; border-radius: 0 4px 4px 4px; }
        .menu-item.active .dropdown { display: block; }
        .drop-item { padding: 8px 15px; display: flex; justify-content: space-between; color: #ccc; align-items: center; }
        .drop-item:hover { background: var(--accent); color: #000; font-weight: 500; }
        .shortcut { color: #888; font-size: 11px; margin-left: 20px;}
        .drop-item:hover .shortcut { color: #222; }
        
        #toolbar { background: var(--panel); padding: 10px 15px; display: flex; gap: 6px; align-items: center; border-bottom: 1px solid #333; }
        
        button.tool-btn { 
            border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; 
            font-size: 16px; transition: 0.2s; background: transparent; 
            display: flex; align-items: center; justify-content: center; color: #ffffff; 
        }
        button.tool-btn:hover { background: rgba(255, 255, 255, 0.1); color: #cccccc; }
        
        #tab-bar { display: flex; background: #1a1a1a; overflow-x: auto; border-bottom: 1px solid #333; height: 38px; }
        #tab-bar::-webkit-scrollbar { display: none; }
        
        .tab { padding: 0 14px; background: #222; color: #888; border-right: 1px solid #333; cursor: pointer; display: flex; align-items: center; font-size: 13px; min-width: 120px; max-width: 250px; white-space: nowrap; overflow: hidden; border-top: 2px solid transparent; box-sizing: border-box; height: 100%; }
        .tab.active { background: var(--bg); color: #fff; border-top: 2px solid var(--accent); }
        
        .tab-close { font-size: 16px; cursor: pointer; border-radius: 4px; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; margin-right: 8px; margin-left: 0; transition: 0.2s; }
        .tab-close:hover { background: #444; color: #f44336; }
        
        .tab-add { padding: 0 16px; cursor: pointer; color: #888; font-size: 18px; display: flex; align-items: center; height: 100%; font-weight: bold; }
        .tab-add:hover { color: #fff; }
        
        #editor-container { flex: 1; position: relative; background: var(--bg); }
        
        #terminal { height: 200px; background: #0a0a0a; color: #00ff00; padding: 15px; overflow-y: auto; font-family: 'Menlo', 'Consolas', monospace; font-size: 12px; border-top: 1px solid #333; white-space: pre-wrap; word-wrap: break-word; }
        
        #exit-overlay { 
            display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background: rgba(0, 0, 0, 0.65); z-index: 9999; 
            justify-content: center; align-items: center; backdrop-filter: blur(3px);
        }
        .exit-modal { 
            background: #1e1e1e; border: 1px solid #333; border-radius: 12px; 
            padding: 30px; width: 340px; box-shadow: 0 20px 45px rgba(0,0,0,0.6); 
            display: flex; flex-direction: column; align-items: center; text-align: center;
        }
        .exit-icon { font-size: 48px; margin-bottom: 15px; line-height: 1; }
        .exit-text { font-size: 15px; line-height: 1.5; color: #eee; margin-bottom: 25px; }
        .exit-buttons { display: flex; justify-content: center; gap: 12px; width: 100%; }
        
        .btn-modal { border: none; padding: 8px 24px; border-radius: 6px; cursor: pointer; font-size: 14px; transition: 0.2s; font-weight: bold; }
        .btn-cancel { background: #444; color: white; }
        .btn-cancel:hover { background: #555; }
        .btn-confirm { background: #F44336; color: white; }
        .btn-confirm:hover { background: #d32f2f; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.40.0/min/vs/loader.min.js"></script>
</head>
<body>
    <div id="toolbar">
        <button class="tool-btn" onclick="runCode()" id="btn-run" title="Uruchom (⌘Enter)"></button>
        <button class="tool-btn" onclick="stopCode()" id="btn-stop" title="Zatrzymaj"></button>
    </div>
    
    <div id="tab-bar"></div>
    <div id="editor-container" id="editor"></div>
    <div id="terminal"></div>

    <div id="exit-overlay">
        <div class="exit-modal">
            <div class="exit-icon" id="exit-icon">⚠️</div>
            <div class="exit-text" id="exit-msg">Masz niezapisane zmiany!<br>Czy na pewno chcesz zakończyć bez zapisywania?</div>
            <div class="exit-buttons">
                <button class="btn-modal btn-cancel" onclick="hideModal()" id="btn-cancel">Anuluj</button>
                <button class="btn-modal btn-confirm" onclick="confirmModal()" id="btn-confirm">Zakończ</button>
            </div>
        </div>
    </div>

    <script>
        const userLang = navigator.language || navigator.userLanguage;
        const isEN = !userLang.toLowerCase().startsWith('pl');
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        
        const UI = {
            newFile: isEN ? "Untitled" : "Nowy plik",
            closeTab: isEN ? "Close tab" : "Zamknij kartę",
            unsavedTab: isEN ? "File '{0}' has unsaved changes.<br>Close anyway?" : "Plik '{0}' ma niezapisane zmiany.<br>Zamknąć mimo to?",
            runBtn: "▶", 
            stopBtn: "■",
            termReady: isEN ? "> EditCode Terminal ready...\\n\\n" : "> Terminal EditCode gotowy...\\n\\n",
            errSave: isEN ? "\\n[Error] Save the file first (File -> Save) before running!\\n" : "\\n[Błąd] Najpierw zapisz plik (Plik -> Zapisz) przed jego uruchomieniem!\\n",
            openMsg: isEN ? "\\n[EditCode] Opened: " : "\\n[EditCode] Otwarto: ",
            saveMsg: isEN ? "\\n[EditCode] Saved: " : "\\n[EditCode] Zapisano: ",
            quitUnsaved: isEN ? "You have unsaved changes!<br>Are you sure you want to quit without saving?" : "Masz niezapisane zmiany!<br>Czy na pewno chcesz zakończyć bez zapisywania?",
            cancelBtn: isEN ? "Cancel" : "Anuluj",
            quitBtn: isEN ? "Quit" : "Zakończ",
            closeBtn: isEN ? "Close" : "Zamknij",
            
            mFile: isEN ? "File" : "Plik",
            mEdit: isEN ? "Edit" : "Edycja",
            mRun: isEN ? "Run" : "Uruchom",
            open: isEN ? "Open" : "Otwórz",
            save: isEN ? "Save" : "Zapisz",
            undo: isEN ? "Undo" : "Cofnij",
            redo: isEN ? "Redo" : "Ponów",
            copy: isEN ? "Copy" : "Kopiuj",
            paste: isEN ? "Paste" : "Wklej",
            find: isEN ? "Find" : "Znajdź",
            mStop: isEN ? "Stop" : "Zatrzymaj"
        };

        if (!isMac) {
            let winMenu = document.createElement('div');
            winMenu.id = 'win-menu';
            winMenu.innerHTML = `
            <div class="menu-item">${UI.mFile}
                <div class="dropdown">
                    <div class="drop-item" onclick="openFile()">${UI.open} <span class="shortcut">Ctrl+O</span></div>
                    <div class="drop-item" onclick="saveFile()">${UI.save} <span class="shortcut">Ctrl+S</span></div>
                    <div class="drop-item" onclick="checkQuit()">${UI.quitBtn} <span class="shortcut">Alt+F4</span></div>
                </div>
            </div>
            <div class="menu-item">${UI.mEdit}
                <div class="dropdown">
                    <div class="drop-item" onclick="if(editor)editor.trigger('keyboard', 'undo', null)">${UI.undo} <span class="shortcut">Ctrl+Z</span></div>
                    <div class="drop-item" onclick="if(editor)editor.trigger('keyboard', 'redo', null)">${UI.redo} <span class="shortcut">Ctrl+Y</span></div>
                    <div class="drop-item" onclick="if(editor)editor.trigger('keyboard', 'editor.action.clipboardCopyAction', null)">${UI.copy} <span class="shortcut">Ctrl+C</span></div>
                    <div class="drop-item" onclick="if(editor)editor.trigger('keyboard', 'editor.action.clipboardPasteAction', null)">${UI.paste} <span class="shortcut">Ctrl+V</span></div>
                    <div class="drop-item" onclick="triggerFind()">${UI.find} <span class="shortcut">Ctrl+F</span></div>
                </div>
            </div>
            <div class="menu-item">${UI.mRun}
                <div class="dropdown">
                    <div class="drop-item" onclick="runCode()">${UI.mRun} <span class="shortcut">Ctrl+Enter</span></div>
                    <div class="drop-item" onclick="stopCode()">${UI.mStop}</div>
                </div>
            </div>`;
            document.body.insertBefore(winMenu, document.body.firstChild);

            document.addEventListener('click', function(e) {
                let isMenu = e.target.closest('.menu-item');
                let isDropItem = e.target.closest('.drop-item');
                if (!isMenu || isDropItem) {
                    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
                } else {
                    let wasActive = isMenu.classList.contains('active');
                    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
                    if (!wasActive) isMenu.classList.add('active');
                }
            });

            document.addEventListener('mouseover', function(e) {
                let isMenu = e.target.closest('.menu-item');
                let anyActive = document.querySelector('.menu-item.active');
                if (isMenu && anyActive && anyActive !== isMenu) {
                    document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
                    isMenu.classList.add('active');
                }
            });
        }

        document.getElementById('btn-run').title = isEN ? (isMac ? "Run (⌘Enter)" : "Run (Ctrl+Enter)") : (isMac ? "Uruchom (⌘Enter)" : "Uruchom (Ctrl+Enter)");
        document.getElementById('btn-stop').title = isEN ? "Stop" : "Zatrzymaj";

        document.getElementById('btn-run').innerText = UI.runBtn;
        document.getElementById('btn-stop').innerText = UI.stopBtn;
        document.getElementById('terminal').innerText = UI.termReady;
        
        document.getElementById('btn-cancel').innerText = UI.cancelBtn;
        document.getElementById('btn-confirm').innerText = UI.quitBtn;

        let tabs = [];
        let activeTabId = null;
        let tabIdCounter = 0;
        let isSwitching = false;
        var editor;

        let syncTimer = null;
        function syncUnsavedState() {
            clearTimeout(syncTimer);
            syncTimer = setTimeout(function() {
                try {
                    if (window.pywebview && window.pywebview.api) {
                        let hasUnsaved = tabs.some(t => !t.saved);
                        pywebview.api.set_unsaved(hasUnsaved);
                    }
                } catch(e) {}
            }, 100);
        }

        function renderTabs() {
            let html = '';
            tabs.forEach(t => {
                let title = t.filename + (t.saved ? '' : ' *');
                let fullPath = t.filepath || UI.newFile;
                
                html += `<div class="tab ${t.id === activeTabId ? 'active' : ''}" onclick="switchTab(${t.id})" title="${fullPath}">
                            <span class="tab-close" onclick="event.stopPropagation(); closeTab(${t.id})" title="${UI.closeTab}">×</span>
                            <span>${title}</span>
                         </div>`;
            });
            html += `<div class="tab-add" onclick="addTab('', '', 'python')" title="${UI.newFile}">+</div>`;
            document.getElementById('tab-bar').innerHTML = html;
            
            syncUnsavedState();
        }

        function addTab(filepath, content, lang) {
            let id = tabIdCounter++;
            let filename = filepath ? filepath.split('/').pop().split('\\\\').pop() : UI.newFile;
            tabs.push({ id, filepath, filename, content, lang, saved: true });
            switchTab(id);
        }

        function switchTab(id) {
            if (activeTabId !== null && editor) {
                let activeTab = tabs.find(t => t.id === activeTabId);
                if (activeTab) activeTab.content = editor.getValue();
            }
            activeTabId = id;
            let tab = tabs.find(t => t.id === id);
            if (tab && editor) {
                isSwitching = true;
                editor.setValue(tab.content);
                monaco.editor.setModelLanguage(editor.getModel(), tab.lang);
                isSwitching = false;
            }
            renderTabs();
        }

        let pendingAction = null;
        let pendingData = null;

        function showModal(msg, action, data) {
            document.getElementById('exit-msg').innerHTML = msg;
            document.getElementById('exit-overlay').style.display = 'flex';
            pendingAction = action;
            pendingData = data;
            if (action === 'closeTab') {
                document.getElementById('btn-confirm').innerText = UI.closeBtn;
            } else {
                document.getElementById('btn-confirm').innerText = UI.quitBtn;
            }
        }

        function hideModal() { 
            document.getElementById('exit-overlay').style.display = 'none'; 
            pendingAction = null;
            pendingData = null;
        }

        function confirmModal() {
            if (pendingAction === 'quit') {
                document.getElementById('exit-overlay').style.display = 'none';
                setTimeout(function() { pywebview.api.force_quit(); }, 50);
            } else if (pendingAction === 'closeTab') {
                forceCloseTab(pendingData);
                hideModal();
            }
        }

        function closeTab(id) {
            let tab = tabs.find(t => t.id === id);
            if (!tab.saved) {
                let msg = UI.unsavedTab.replace('{0}', tab.filename);
                showModal(msg, 'closeTab', id);
                return;
            }
            forceCloseTab(id);
        }

        function forceCloseTab(id) {
            tabs = tabs.filter(t => t.id !== id);
            if (tabs.length === 0) {
                addTab('', '', 'python'); 
            } else if (activeTabId === id) {
                switchTab(tabs[tabs.length - 1].id);
            } else {
                renderTabs();
            }
        }

        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.40.0/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            
            monaco.languages.registerCompletionItemProvider('python', {
                provideCompletionItems: function(model, position) {
                    var word = model.getWordUntilPosition(position);
                    var range = { startLineNumber: position.lineNumber, endLineNumber: position.lineNumber, startColumn: word.startColumn, endColumn: word.endColumn };
                    return {
                        suggestions: [
                            { label: 'def', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'def ${1:name}(${2:args}):\\n\\t${3:pass}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Definicja funkcji', range: range },
                            { label: 'if', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'if ${1:condition}:\\n\\t${2:pass}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Instrukcja if', range: range },
                            { label: 'for', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'for ${1:item} in ${2:iterable}:\\n\\t${3:pass}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Pętla for', range: range },
                            { label: 'class', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'class ${1:Name}:\\n\\tdef __init__(self):\\n\\t\\t${2:pass}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Definicja klasy', range: range },
                            { label: 'while', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'while ${1:condition}:\\n\\t${2:pass}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Pętla while', range: range },
                            { label: 'try', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'try:\\n\\t${1:pass}\\nexcept ${2:Exception} as ${3:e}:\\n\\t${4:raise}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Blok try/except', range: range },
                            { label: 'main', kind: monaco.languages.CompletionItemKind.Snippet, insertText: 'if __name__ == "__main__":\\n\\t${1:main()}', insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet, documentation: 'Punkt wejścia programu', range: range }
                        ]
                    };
                }
            });
            
            editor = monaco.editor.create(document.getElementById('editor-container'), {
                value: '',
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true
            });
            
            editor.onDidChangeModelContent(function() {
                if (!isSwitching && activeTabId !== null) {
                    let tab = tabs.find(t => t.id === activeTabId);
                    if (tab && tab.saved) {
                        tab.saved = false;
                        renderTabs();
                    }
                }
            });

            if (!isEN) {
                setInterval(function() {
                    let findWidget = document.querySelector('.find-widget');
                    if (findWidget) {
                        findWidget.querySelectorAll('textarea[placeholder="Find"], input[placeholder="Find"]').forEach(function(e) { e.placeholder = 'Znajdź'; });
                        findWidget.querySelectorAll('textarea[placeholder="Replace"], input[placeholder="Replace"]').forEach(function(e) { e.placeholder = 'Zamień'; });
                        findWidget.querySelectorAll('.matchesCount').forEach(function(e) {
                            if (e.innerText === 'No results') e.innerText = 'Brak wyników';
                            else if (e.innerText.indexOf(' of ') !== -1) e.innerText = e.innerText.replace(' of ', ' z ');
                        });
                        const tooltips = [
                            ['Toggle Replace mode', 'Przełącz tryb zamiany'], ['Toggle Replace', 'Przełącz tryb zamiany'],
                            ['Replace All', 'Zamień wszystko'], ['Replace', 'Zamień'],
                            ['Find in Selection', 'Znajdź w zaznaczeniu'], ['Find in selection', 'Znajdź w zaznaczeniu'],
                            ['Previous match', 'Poprzedni wynik'], ['Next match', 'Następny wynik'],
                            ['Close (Escape)', 'Zamknij (Escape)'], ['Match Case', 'Uwzględniaj wielkość liter'],
                            ['Match Whole Word', 'Dopasuj całe słowo'], ['Use Regular Expression', 'Użyj wyrażeń regularnych'],
                            ['Preserve Case', 'Zachowaj wielkość liter']
                        ];
                        findWidget.querySelectorAll('[title]').forEach(function(e) {
                            tooltips.forEach(function(t) {
                                if (e.title.includes(t[0])) { e.title = e.title.replace(t[0], t[1]); }
                            });
                        });
                    }
                }, 1000); 
            }

            function loadStartupFile() {
                if (window.pywebview && window.pywebview.api) {
                    pywebview.api.get_startup_file().then(function(res) {
                        if (res && res.filepath) {
                            addTab(res.filepath, res.content, res.lang);
                            appendTerminal(UI.openMsg + res.filepath + "\\n");
                        } else {
                            let initialCode = isEN ? '# Welcome to EditCode!\\n' : '# Witaj w EditCode!\\n';
                            addTab('', initialCode, 'python');
                        }
                        
                        pywebview.api.app_ready();
                        
                    }).catch(function() {
                        let initialCode = isEN ? '# Welcome to EditCode!\\n' : '# Witaj w EditCode!\\n';
                        addTab('', initialCode, 'python');
                        pywebview.api.app_ready();
                    });
                } else {
                    setTimeout(loadStartupFile, 50);
                }
            }
            
            loadStartupFile();
        });

        function appendTerminal(text) {
            var term = document.getElementById('terminal');
            term.textContent += text;
            term.scrollTop = term.scrollHeight;
        }

        function openFile() {
            pywebview.api.open_file_dialog().then(function(result) {
                if(result) { addTab(result.filepath, result.content, result.lang); appendTerminal(UI.openMsg + result.filepath + "\\n"); }
            });
        }

        function saveFile() {
            if (activeTabId === null) return;
            let tab = tabs.find(t => t.id === activeTabId);
            tab.content = editor.getValue();
            pywebview.api.save_file_dialog(tab.content, tab.filepath).then(function(result) {
                if(result) { tab.filepath = result.filepath; tab.filename = result.filename; tab.saved = true; renderTabs(); appendTerminal(UI.saveMsg + tab.filename + "\\n"); }
            });
        }

        function triggerFind() { if (editor) { editor.trigger('keyboard', 'actions.find', null); } }
        
        function runCode() {
            if (activeTabId === null) return;
            let tab = tabs.find(t => t.id === activeTabId);
            tab.content = editor.getValue();
            if (!tab.saved || !tab.filepath) { appendTerminal(UI.errSave); return; }
            pywebview.api.run_code(tab.filepath);
        }

        function stopCode() { pywebview.api.stop_code(); }

        window.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                let key = e.key.toLowerCase();
                if (key === 's') { e.preventDefault(); saveFile(); }
                if (key === 'o') { e.preventDefault(); openFile(); }
                if (key === 'f') { e.preventDefault(); triggerFind(); }
                if (key === 'enter') { e.preventDefault(); runCode(); }
            }
        });

        function checkQuit() {
            let hasUnsaved = tabs.some(t => !t.saved);
            if (!hasUnsaved) {
                pywebview.api.force_quit();
            } else {
                showModal(UI.quitUnsaved, 'quit', null);
            }
        }
    </script>
</body>
</html>
"""

class BackendApi:
    def __init__(self):
        self.process = None
        self.allow_quit = False 
        self.has_unsaved = False 
        self._is_ready = False

    def app_ready(self):
        if self._is_ready: return
        self._is_ready = True
        
        if platform.system() == 'Darwin':
            def apply_fix():
                try:
                    from AppKit import NSApplication
                    app = NSApplication.sharedApplication()
                    main_menu = app.mainMenu()
                    if main_menu:
                        allowed_titles = ['Plik', 'Edycja', 'Uruchom'] if is_pl else ['File', 'Edit', 'Run']
                        seen_titles = set()                       
                        for i in range(main_menu.numberOfItems() - 1, 0, -1):
                            item = main_menu.itemAtIndex_(i)
                            if item:
                                title = str(item.title()).strip()
                                if title not in allowed_titles:
                                    main_menu.removeItemAtIndex_(i)
                                elif title in seen_titles:
                                    main_menu.removeItemAtIndex_(i)
                                else:
                                    seen_titles.add(title)
                except Exception:
                    pass

            if APP_WINDOW: APP_WINDOW.show()

            try:
                from PyObjCTools import AppHelper
                for delay in [0.1, 0.5, 1.2, 2.5]:
                    threading.Timer(delay, lambda: AppHelper.callAfter(apply_fix)).start()
            except:
                pass
        else:
            if APP_WINDOW: APP_WINDOW.show()

    def open_specific_file(self, filepath):
        if not APP_WINDOW: return
        if os.path.exists(filepath):
            content = ""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(filepath, 'r', encoding='mbcs', errors='replace') as f:
                        content = f.read()
                except Exception: pass
            except Exception: pass
            
            lang = self.get_lang(filepath)
            
            fp_json = json.dumps(filepath)
            ct_json = json.dumps(content)
            lg_json = json.dumps(lang)
            
            js = f"""
            (function() {{
                try {{
                    addTab({fp_json}, {ct_json}, {lg_json});
                    appendTerminal(UI.openMsg + {fp_json} + "\\n");
                }} catch(e) {{}}
            }})();
            """
            try:
                APP_WINDOW.evaluate_js(js)
            except:
                pass

    def get_startup_file(self):
        if len(sys.argv) > 1:
            filepath = None
            joined_path = " ".join(sys.argv[1:]).strip('"').strip("'")
            if os.path.exists(joined_path) and os.path.isfile(joined_path):
                filepath = joined_path
            else:
                for arg in sys.argv[1:]:
                    clean_arg = arg.strip('"').strip("'")
                    if os.path.exists(clean_arg) and os.path.isfile(clean_arg):
                        filepath = clean_arg
                        break

            if filepath:
                filepath = os.path.abspath(filepath)
                content = ""
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(filepath, 'r', encoding='mbcs', errors='replace') as f:
                            content = f.read()
                    except Exception: pass
                except Exception: pass
                
                return {'filepath': filepath, 'content': content, 'lang': self.get_lang(filepath)}
        return None

    def set_unsaved(self, state):
        self.has_unsaved = state

    def force_quit(self):
        self.allow_quit = True
        self.stop_code()
        
        def kill_app():
            import time
            time.sleep(0.3)
            if APP_WINDOW:
                try:
                    APP_WINDOW.destroy()
                except Exception:
                    pass
            if platform.system() == 'Windows':
                time.sleep(0.1)
                os._exit(0)
                
        threading.Thread(target=kill_app, daemon=True).start()

    def print_terminal(self, text):
        if APP_WINDOW:
            try:
                APP_WINDOW.evaluate_js(f"appendTerminal({json.dumps(text)})")
            except:
                pass

    def get_lang(self, filepath):
        if filepath.endswith('.py'): return 'python'
        if filepath.endswith('.js'): return 'javascript'
        if filepath.endswith('.html'): return 'html'
        if filepath.endswith('.css'): return 'css'
        return 'plaintext'

    def open_file_dialog(self):
        if not APP_WINDOW: return None
        result = APP_WINDOW.create_file_dialog(webview.FileDialog.OPEN)
        if result and len(result) > 0:
            filepath = result[0]
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {'filepath': filepath, 'content': content, 'lang': self.get_lang(filepath)}
            except Exception as e:
                self.print_terminal(f"\n[{T['err']}] {T['err_open']} {e}\n")
        return None

    def save_file_dialog(self, content, current_filepath):
        if not APP_WINDOW: return None
        filepath_to_save = current_filepath
        if not filepath_to_save:
            result = APP_WINDOW.create_file_dialog(webview.FileDialog.SAVE)
            if result and len(result) > 0:
                filepath_to_save = result[0]
            else:
                return None

        try:
            with open(filepath_to_save, 'w', encoding='utf-8') as f:
                f.write(content)
            filename = os.path.basename(filepath_to_save)
            return {'filepath': filepath_to_save, 'filename': filename}
        except Exception as e:
            self.print_terminal(f"\n[{T['err']}] {T['err_save']} {e}\n")
            return None

    def run_code(self, filepath):
        if not filepath: return
        abs_filepath = os.path.abspath(filepath)
        filename = os.path.basename(abs_filepath)
        self.print_terminal(f"\n[EditCode] {T['run_msg']} {filename}\n")
        
        def execute():
            try:
                env = os.environ.copy()
                if getattr(sys, 'frozen', False):
                    env.pop('PYTHONHOME', None)
                    env.pop('PYTHONPATH', None)
                    env.pop('DYLD_LIBRARY_PATH', None)
                    env.pop('LD_LIBRARY_PATH', None)
                    if platform.system() == 'Darwin':
                        env['PATH'] = '/usr/local/bin:/opt/homebrew/bin:' + env.get('PATH', '/usr/bin:/bin')
                        cmd = ['python3', abs_filepath]
                    else:
                        cmd = ['python', abs_filepath]
                else:
                    cmd = [sys.executable, abs_filepath]

                if abs_filepath.endswith('.js'):
                    cmd = ['node', abs_filepath]

                self.process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True, 
                    bufsize=1,
                    env=env,
                    cwd=os.path.dirname(abs_filepath)
                )
                
                for line in self.process.stdout:
                    self.print_terminal(line)
                    
                self.process.wait()
                self.print_terminal(f"\n[EditCode] {T['done_msg']} {self.process.returncode})\n")
            except Exception as e:
                self.print_terminal(f"\n[{T['err']}] Nie udało się uruchomić procesu: {str(e)}\n")

        threading.Thread(target=execute, daemon=True).start()

    def stop_code(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.print_terminal(f"\n[EditCode] {T['stop_msg']}\n")

def setup_macos_open_handler(api):
    if platform.system() != 'Darwin':
        return
        
    def apply_handler():
        try:
            from AppKit import NSAppleEventManager, NSObject
            import objc

            class OpenFileHandler(NSObject):
                @objc.typedSelector(b'v@:@@')
                def handleEvent_withReplyEvent_(self, event, replyEvent):
                    try:
                        desc = event.paramDescriptorForKeyword_(1128418861)
                        if not desc: return
                        
                        num_items = desc.numberOfItems()
                        if num_items > 0:
                            for i in range(1, num_items + 1):
                                url_desc = desc.descriptorAtIndex_(i)
                                if url_desc:
                                    url_str = url_desc.stringValue()
                                    if url_str and url_str.startswith('file://'):
                                        from urllib.parse import unquote
                                        filepath = unquote(url_str[7:])
                                        api.open_specific_file(filepath)
                        else:
                            url_str = desc.stringValue()
                            if url_str and url_str.startswith('file://'):
                                from urllib.parse import unquote
                                filepath = unquote(url_str[7:])
                                api.open_specific_file(filepath)
                    except Exception:
                        pass

            global macos_open_handler
            macos_open_handler = OpenFileHandler.alloc().init()
            manager = NSAppleEventManager.sharedAppleEventManager()
            
            manager.setEventHandler_andSelector_forEventClass_andEventID_(
                macos_open_handler,
                objc.selector(macos_open_handler.handleEvent_withReplyEvent_, signature=b'v@:@@'),
                1634039412,
                1868853091
            )
        except Exception:
            pass 

    from PyObjCTools import AppHelper
    AppHelper.callAfter(apply_handler)


def on_closing():
    if api.allow_quit:
        return True
        
    if not api.has_unsaved:
        api.stop_code()
        api.allow_quit = True
        return True
        
    if platform.system() == 'Windows':
        import ctypes
        res = ctypes.windll.user32.MessageBoxW(
            0, 
            "Masz niezapisane zmiany w edytorze.\nCzy na pewno chcesz zakończyć bez zapisywania?", 
            "EditCode - Ostrzeżenie", 
            262196
        )
        if res == 6: 
            api.stop_code()
            api.allow_quit = True
            return True
        return False
    else:
        import time
        def trigger_js():
            time.sleep(0.1)
            if APP_WINDOW:
                try:
                    APP_WINDOW.evaluate_js('checkQuit()')
                except:
                    pass
        threading.Thread(target=trigger_js, daemon=True).start()
        return False

def failsafe_show(api_instance):
    if not api_instance._is_ready and APP_WINDOW:
        api_instance.app_ready()

if __name__ == '__main__':
    api = BackendApi()
    
    APP_WINDOW = webview.create_window(
        title='EditCode', 
        html=HTML_CONTENT, 
        js_api=api, 
        width=1100, 
        height=750,
        background_color='#1e1e1e',
        confirm_close=False,
        hidden=True 
    )
    
    APP_WINDOW.events.closing += on_closing
    APP_WINDOW.events.loaded += lambda: setup_macos_open_handler(api)
    APP_WINDOW.events.loaded += lambda: threading.Timer(3.0, failsafe_show, args=(api,)).start()
    
    loc = {
        'mac.menu.about': 'O programie EditCode',
        'mac.menu.services': 'Usługi',
        'mac.menu.hide': 'Ukryj EditCode',
        'mac.menu.hideOthers': 'Ukryj inne',
        'mac.menu.showAll': 'Pokaż wszystkie',
        'mac.menu.quit': 'Zakończ EditCode'
    }

    if platform.system() == 'Darwin':
        CMD = '⌘'
        menu_items = [
            Menu('Plik' if is_pl else 'File', [
                MenuAction(f"Otwórz  ({CMD}O)", lambda: APP_WINDOW.evaluate_js('setTimeout(openFile, 10)')),
                MenuAction(f"Zapisz  ({CMD}S)", lambda: APP_WINDOW.evaluate_js('setTimeout(saveFile, 10)'))
            ]),
            Menu('Edycja' if is_pl else 'Edit', [
                MenuAction(f"Cofnij  ({CMD}Z)", lambda: APP_WINDOW.evaluate_js('setTimeout(function(){if(editor) editor.trigger("keyboard", "undo", null);}, 10)')),
                MenuAction(f"Ponów  ({CMD}Y)", lambda: APP_WINDOW.evaluate_js('setTimeout(function(){if(editor) editor.trigger("keyboard", "redo", null);}, 10)')),
                MenuAction(f"Kopiuj  ({CMD}C)", lambda: APP_WINDOW.evaluate_js('setTimeout(function(){if(editor) editor.trigger("keyboard", "editor.action.clipboardCopyAction", null);}, 10)')),
                MenuAction(f"Wytnij  ({CMD}X)", lambda: APP_WINDOW.evaluate_js('setTimeout(function(){if(editor) editor.trigger("keyboard", "editor.action.clipboardCutAction", null);}, 10)')),
                MenuAction(f"Wklej  ({CMD}V)", lambda: APP_WINDOW.evaluate_js('setTimeout(function(){if(editor) editor.trigger("keyboard", "editor.action.clipboardPasteAction", null);}, 10)')),
                MenuAction(f"Znajdź  ({CMD}F)", lambda: APP_WINDOW.evaluate_js('setTimeout(triggerFind, 10)'))
            ]),
            Menu('Uruchom' if is_pl else 'Run', [
                MenuAction(f"Uruchom  ({CMD}Enter)", lambda: APP_WINDOW.evaluate_js('setTimeout(runCode, 10)')),
                MenuAction("Zatrzymaj" if is_pl else "Stop", lambda: APP_WINDOW.evaluate_js('setTimeout(stopCode, 10)'))
            ])
        ]
        webview.start(menu=menu_items, localization=loc, debug=False)
    else:
        webview.start(localization=loc, debug=False)
