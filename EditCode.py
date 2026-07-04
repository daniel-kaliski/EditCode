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
    else:
        import locale
        lang = os.environ.get('LANG', '') or locale.getdefaultlocale()[0] or 'en'
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
    'err': "Błąd" if is_pl else "Error",
    'file': "Plik" if is_pl else "File",
    'open': "Otwórz..." if is_pl else "Open...",
    'save': "Zapisz" if is_pl else "Save",
    'tools': "Narzędzia" if is_pl else "Tools",
    'find': "Szukaj" if is_pl else "Find"
}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <style>
        :root { --bg: #121212; --panel: #1e1e1e; --text: #fff; --accent: #63bdf2; }
        body, html { margin: 0; padding: 0; height: 100%; display: flex; flex-direction: column; background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
        
        #toolbar { background: var(--panel); padding: 10px 15px; display: flex; gap: 10px; align-items: center; }
        button { background: #2d2d2d; color: white; border: none; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; font-size: 13px; }
        button:hover { background: #3d3d3d; }
        .btn-run { color: #4CAF50; display: flex; align-items: center; gap: 5px; }
        .btn-stop { color: #F44336; }
        
        /* Styl dla wbudowanego menu (tylko Windows) */
        #win-menu { display: none; gap: 8px; margin-right: 15px; border-right: 1px solid #333; padding-right: 15px; }
        .btn-menu { background: transparent; color: #ccc; font-weight: normal; }
        .btn-menu:hover { background: #333; color: #fff; }
        
        #tab-bar { display: flex; background: #151515; overflow-x: auto; border-bottom: 1px solid #333; height: 38px; }
        #tab-bar::-webkit-scrollbar { display: none; }
        
        .tab { padding: 0 14px; background: #1a1a1a; color: #888; border-right: 1px solid #333; cursor: pointer; display: flex; align-items: center; font-size: 13px; min-width: 120px; max-width: 250px; white-space: nowrap; overflow: hidden; border-top: 2px solid transparent; box-sizing: border-box; height: 100%; }
        .tab.active { background: var(--bg); color: #fff; border-top: 2px solid var(--accent); }
        
        .tab-close { font-size: 16px; cursor: pointer; border-radius: 4px; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; margin-right: 8px; margin-left: 0; transition: 0.2s; }
        .tab-close:hover { background: #444; color: #f44336; }
        
        .tab-add { padding: 0 16px; cursor: pointer; color: #888; font-size: 18px; display: flex; align-items: center; height: 100%; font-weight: bold; }
        .tab-add:hover { color: #fff; }
        
        #editor-container { flex: 1; position: relative; background: var(--bg); }
        #terminal { height: 200px; background: #0a0a0a; color: #00ff00; padding: 15px; overflow-y: auto; font-family: 'Menlo', 'Consolas', monospace; font-size: 12px; border-top: 1px solid #333; white-space: pre-wrap; word-wrap: break-word; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.40.0/min/vs/loader.min.js"></script>
</head>
<body>
    <div id="toolbar">
        <div id="win-menu">
            <button class="btn-menu" onclick="openFile()" id="btn-open">Otwórz</button>
            <button class="btn-menu" onclick="saveFile()" id="btn-save">Zapisz</button>
            <button class="btn-menu" onclick="triggerFind()" id="btn-find">Szukaj</button>
        </div>
        
        <button class="btn-run" onclick="runCode()" id="btn-run">▶ Uruchom</button>
        <button class="btn-stop" onclick="stopCode()" id="btn-stop">■ Zatrzymaj</button>
    </div>
    
    <div id="tab-bar"></div>
    <div id="editor-container" id="editor"></div>
    <div id="terminal"></div>

    <script>
        // TŁUMACZENIA JS
        const userLang = navigator.language || navigator.userLanguage;
        const isEN = !userLang.toLowerCase().startsWith('pl');
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        
        const UI = {
            newFile: isEN ? "Untitled" : "Nowy plik",
            closeTab: isEN ? "Close tab" : "Zamknij kartę",
            unsaved: isEN ? "Tab '{0}' has unsaved changes. Close anyway?" : "Karta '{0}' ma niezapisane zmiany. Zamknąć mimo to?",
            runBtn: isEN ? "▶ Run" : "▶ Uruchom",
            stopBtn: isEN ? "■ Stop" : "■ Zatrzymaj",
            openBtn: isEN ? "Open" : "Otwórz",
            saveBtn: isEN ? "Save" : "Zapisz",
            findBtn: isEN ? "Find" : "Szukaj",
            termReady: isEN ? "> EditCode Terminal ready...\\n\\n" : "> Terminal EditCode gotowy...\\n\\n",
            errSave: isEN ? "\\n[Error] Save the file first (File -> Save) before running!\\n" : "\\n[Błąd] Najpierw zapisz plik (Plik -> Zapisz) przed jego uruchomieniem!\\n",
            openMsg: isEN ? "\\n[EditCode] Opened: " : "\\n[EditCode] Otwarto: ",
            saveMsg: isEN ? "\\n[EditCode] Saved: " : "\\n[EditCode] Zapisano: "
        };

        // Podpinanie tekstów
        document.getElementById('btn-run').innerText = UI.runBtn;
        document.getElementById('btn-stop').innerText = UI.stopBtn;
        document.getElementById('btn-open').innerText = UI.openBtn;
        document.getElementById('btn-save').innerText = UI.saveBtn;
        document.getElementById('btn-find').innerText = UI.findBtn;
        document.getElementById('terminal').innerText = UI.termReady;

        // Aktywacja menu wewnątrz aplikacji tylko dla systemu Windows
        if (!isMac) {
            document.getElementById('win-menu').style.display = 'flex';
        }

        // SYSTEM ZAKŁADEK (TABS)
        let tabs = [];
        let activeTabId = null;
        let tabIdCounter = 0;
        let isSwitching = false;
        var editor;

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

        function closeTab(id) {
            let tab = tabs.find(t => t.id === id);
            if (!tab.saved) {
                let msg = UI.unsaved.replace('{0}', tab.filename);
                if (!confirm(msg)) return;
            }
            tabs = tabs.filter(t => t.id !== id);
            if (tabs.length === 0) {
                addTab('', '', 'python'); 
            } else if (activeTabId === id) {
                switchTab(tabs[tabs.length - 1].id);
            } else {
                renderTabs();
            }
        }

        // INICJALIZACJA MONACO EDITOR
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.40.0/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            let initialCode = isEN ? '# Welcome to EditCode!' : '# Witaj w EditCode!';
            
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
                    document.querySelectorAll('textarea[placeholder="Find"], input[placeholder="Find"]').forEach(function(e) { e.placeholder = 'Znajdź'; });
                    document.querySelectorAll('textarea[placeholder="Replace"], input[placeholder="Replace"]').forEach(function(e) { e.placeholder = 'Zamień'; });
                    
                    document.querySelectorAll('.matchesCount').forEach(function(e) {
                        if (e.innerText === 'No results') e.innerText = 'Brak wyników';
                        else if (e.innerText.indexOf(' of ') !== -1) e.innerText = e.innerText.replace(' of ', ' z ');
                    });

                    const tooltips = [
                        ['Toggle Replace mode', 'Przełącz tryb zamiany'],
                        ['Toggle Replace', 'Przełącz tryb zamiany'],
                        ['Replace All', 'Zamień wszystko'],
                        ['Replace', 'Zamień'],
                        ['Find in Selection', 'Znajdź w zaznaczeniu'],
                        ['Find in selection', 'Znajdź w zaznaczeniu'],
                        ['Previous match', 'Poprzedni wynik'],
                        ['Next match', 'Następny wynik'],
                        ['Close (Escape)', 'Zamknij (Escape)'],
                        ['Match Case', 'Uwzględniaj wielkość liter'],
                        ['Match Whole Word', 'Dopasuj całe słowo'],
                        ['Use Regular Expression', 'Użyj wyrażeń regularnych'],
                        ['Preserve Case', 'Zachowaj wielkość liter']
                    ];
                    
                    document.querySelectorAll('[title]').forEach(function(e) {
                        tooltips.forEach(function(t) {
                            if (e.title.includes(t[0])) {
                                e.title = e.title.replace(t[0], t[1]);
                            }
                        });
                    });
                }, 200);
            }

            addTab('', initialCode, 'python');
        });

        function appendTerminal(text) {
            var term = document.getElementById('terminal');
            term.textContent += text;
            term.scrollTop = term.scrollHeight;
        }

        function openFile() {
            pywebview.api.open_file_dialog().then(function(result) {
                if(result) {
                    addTab(result.filepath, result.content, result.lang);
                    appendTerminal(UI.openMsg + result.filepath + "\\n");
                }
            });
        }

        function saveFile() {
            if (activeTabId === null) return;
            let tab = tabs.find(t => t.id === activeTabId);
            tab.content = editor.getValue();
            
            pywebview.api.save_file_dialog(tab.content, tab.filepath).then(function(result) {
                if(result) {
                    tab.filepath = result.filepath;
                    tab.filename = result.filename;
                    tab.saved = true;
                    renderTabs();
                    appendTerminal(UI.saveMsg + tab.filename + "\\n");
                }
            });
        }

        function triggerFind() {
            if (editor) { editor.trigger('keyboard', 'actions.find', null); }
        }

        function runCode() {
            if (activeTabId === null) return;
            let tab = tabs.find(t => t.id === activeTabId);
            tab.content = editor.getValue();
            
            if (!tab.saved || !tab.filepath) {
                appendTerminal(UI.errSave);
                return;
            }
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

    </script>
</body>
</html>
"""

class BackendApi:
    def __init__(self):
        self.window = None
        self.process = None

    def set_window(self, window):
        self.window = window

    def print_terminal(self, text):
        if self.window:
            self.window.evaluate_js(f"appendTerminal({json.dumps(text)})")

    def get_lang(self, filepath):
        if filepath.endswith('.py'): return 'python'
        if filepath.endswith('.js'): return 'javascript'
        if filepath.endswith('.html'): return 'html'
        if filepath.endswith('.css'): return 'css'
        return 'plaintext'

    def open_file_dialog(self):
        result = self.window.create_file_dialog(webview.FileDialog.OPEN)
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
        filepath_to_save = current_filepath
        if not filepath_to_save:
            result = self.window.create_file_dialog(webview.FileDialog.SAVE)
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

    def save_file_dialog(self, content, current_filepath):
        filepath_to_save = current_filepath
        if not filepath_to_save:
            result = self.window.create_file_dialog(webview.SAVE_DIALOG)
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

def fix_macos_menu():
    if platform.system() != 'Darwin':
        return
        
    def apply_fix():
        try:
            from AppKit import NSApplication
            app = NSApplication.sharedApplication()
            main_menu = app.mainMenu()
            if not main_menu: return

            main_menu.itemAtIndex_(0).setTitle_('EditCode')
            
            target_title = T['file']
            plik_index = -1
            for i in range(main_menu.numberOfItems()):
                if main_menu.itemAtIndex_(i).title() == target_title:
                    plik_index = i
                    break
            
            if plik_index > 1:
                plik_item = main_menu.itemAtIndex_(plik_index)
                edit_item = main_menu.itemAtIndex_(1)
                view_item = main_menu.itemAtIndex_(2)
                
                if is_pl:
                    edit_item.setTitle_('Edycja')
                    if edit_item.submenu(): edit_item.submenu().setTitle_('Edycja')
                    view_item.setTitle_('Widok')
                    if view_item.submenu(): view_item.submenu().setTitle_('Widok')
                
                main_menu.removeItemAtIndex_(plik_index)
                main_menu.insertItem_atIndex_(plik_item, 1)

        except Exception as e:
            pass 

    def delayed_execution():
        try:
            from PyObjCTools import AppHelper
            AppHelper.callAfter(apply_fix)
        except:
            apply_fix()

    threading.Timer(0.5, delayed_execution).start()

if __name__ == '__main__':
    api = BackendApi()
    

window = webview.create_window(
    'EditCode', 
    html=HTML_CONTENT, 
    js_api=api,
    confirm_close=True,
    min_size=(800, 600)
)

if platform.system() == 'Windows':
    import ctypes
    ctypes.windll.user32.SetMenu(ctypes.windll.user32.GetParent(window.native.handle), 0)

webview.start(debug=False)
