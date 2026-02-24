"""
Gallery-DL GUI  v1.0.0
gallery-dl のモダンな GUI ラッパー。
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import re
import json
import glob
from typing import Optional, List, Any

APP_VERSION = "v1.0.0"

# ──────────────────────────────────────────────
# テーマパレット  (VS Code Dark+)
# ──────────────────────────────────────────────
BG_COLOR     = "#1e1e1e"
FG_COLOR     = "#d4d4d4"
ACCENT_COLOR = "#007acc"
ACCENT_HOVER = "#005f9e"
ENTRY_BG     = "#2d2d30"
PANEL_BG     = "#252526"
BORDER_COLOR = "#3e3e42"
SUCCESS_COLOR = "#4ec9b0"
WARNING_COLOR = "#ce9178"
ERROR_COLOR   = "#f48771"
DIM_COLOR     = "#6a6a6a"

FONT_MAIN  = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SUB   = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 9)
FONT_SMALL = ("Segoe UI", 8)


def resource_path(relative_path: str) -> str:
    """開発環境と PyInstaller ビルドの両方でパスを解決する。"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def app_dir() -> str:
    """アプリ（または .exe）が存在するディレクトリ。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class GalleryDLApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"Gallery-DL GUI  {APP_VERSION}")
        self.root.geometry("860x640")
        self.root.minsize(720, 540)
        self.root.configure(bg=BG_COLOR)

        # ウィンドウアイコンの設定を試みる
        try:
            ico = resource_path("assets/icon.ico")
            if os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass

        # ── 作業ディレクトリ = exe またはスクリプトの場所 ──
        os.chdir(app_dir())

        # ── 状態 ──
        self.process: Optional[subprocess.Popen] = None
        self.fail_count: int = 0
        self.download_count: int = 0
        self.retry_count: int = 0
        self._stop_flag: bool = False
        self.cookie_files: List[str] = []
        self._worker_thread: Optional[threading.Thread] = None
        self._last_activity_time: float = 0.0
        self.TIMEOUT_SECONDS: int = 120  # 応答なし判定秒数
        self.MAX_RETRIES: int = 10        # 最大リトライ回数
        self.current_download_path: Optional[str] = None # 現在ダウンロード中のパス

        self.cookie_dir    = "cookies"
        self.json_input_dir = "json_input"
        self.download_dir  = "DownloadData"

        # ── Tkinter 変数 ──
        self.url_var        = tk.StringVar()
        self.use_cookie_var = tk.BooleanVar(value=False)
        self.cookie_var     = tk.StringVar()
        self.status_var     = tk.StringVar(value="Ready")
        self.stats_var      = tk.StringVar(value="")

        # ── ウィジェット参照 ──
        self.url_entry:     Any = None
        self.cookie_combo:  Any = None
        self.start_btn:     Any = None
        self.stop_btn:      Any = None
        self.log_text:      Any = None
        self.failed_text:   Any = None
        self.notebook:      Any = None
        self.progress_bar:  Any = None

        self._apply_theme()
        self._create_widgets()

        for d in (self.download_dir, self.cookie_dir, self.json_input_dir):
            os.makedirs(d, exist_ok=True)

        self._load_cookies()

    # テーマ
    # ──────────────────────────────────────────────
    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".",           background=BG_COLOR,  foreground=FG_COLOR,   font=FONT_MAIN)
        style.configure("TFrame",      background=BG_COLOR)
        style.configure("Panel.TFrame",background=PANEL_BG)

        # Labels
        style.configure("TLabel",      background=BG_COLOR,  foreground=FG_COLOR,   font=FONT_MAIN)
        style.configure("Title.TLabel",font=FONT_TITLE,      foreground=ACCENT_COLOR)
        style.configure("Sub.TLabel",  font=FONT_SUB,        foreground=DIM_COLOR,  background=BG_COLOR)
        style.configure("Stat.TLabel", font=FONT_BOLD,       foreground=SUCCESS_COLOR, background=BG_COLOR)
        style.configure("Err.TLabel",  font=FONT_BOLD,       foreground=ERROR_COLOR,   background=BG_COLOR)
        style.configure("Status.TLabel",font=FONT_SMALL,     foreground=DIM_COLOR,     background=PANEL_BG)
        style.configure("Ver.TLabel",  font=FONT_SMALL,      foreground=DIM_COLOR,     background=BG_COLOR)

        # Buttons
        style.configure("TButton",
                        background=ACCENT_COLOR, foreground="#ffffff",
                        font=FONT_BOLD, borderwidth=0, focusthickness=0, padding=(10, 6))
        style.map("TButton",
                  background=[("active", ACCENT_HOVER), ("disabled", "#333338")],
                  foreground=[("disabled", "#666666")])

        style.configure("Danger.TButton",
                        background="#7a2020", foreground="#ffffff",
                        font=FONT_BOLD, borderwidth=0, padding=(10, 6))
        style.map("Danger.TButton",
                  background=[("active", "#5a1515"), ("disabled", "#333338")],
                  foreground=[("disabled", "#666666")])

        style.configure("Small.TButton",
                        background=ENTRY_BG, foreground=FG_COLOR,
                        font=FONT_SUB, borderwidth=0, focusthickness=0, padding=(6, 4))
        style.map("Small.TButton",
                  background=[("active", BORDER_COLOR), ("disabled", "#333338")],
                  foreground=[("disabled", "#666666")])

        # Entry / Combobox
        style.configure("TEntry",    fieldbackground=ENTRY_BG, foreground=FG_COLOR,
                         borderwidth=1, relief="flat", padding=6)
        style.map("TEntry", fieldbackground=[("focus", ENTRY_BG)],
                  bordercolor=[("focus", ACCENT_COLOR)])

        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=ENTRY_BG,
                         foreground=FG_COLOR, arrowcolor=FG_COLOR, padding=6)
        style.map("TCombobox",
                  fieldbackground=[("readonly", ENTRY_BG)],
                  selectbackground=[("readonly", ENTRY_BG)],
                  selectforeground=[("readonly", FG_COLOR)])

        # Checkbutton
        style.configure("TCheckbutton", background=BG_COLOR, foreground=FG_COLOR, font=FONT_MAIN)
        style.map("TCheckbutton",
                  background=[("active", BG_COLOR)],
                  indicatorcolor=[("selected", ACCENT_COLOR)])

        # LabelFrame
        style.configure("TLabelframe",       background=BG_COLOR, bordercolor=BORDER_COLOR)
        style.configure("TLabelframe.Label",  background=BG_COLOR, foreground=ACCENT_COLOR,
                         font=FONT_BOLD)

        # Notebook
        style.configure("TNotebook",      background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab",  background=PANEL_BG, foreground=DIM_COLOR,
                         padding=(12, 5), font=FONT_MAIN)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_COLOR)],
                  foreground=[("selected", FG_COLOR)])

        # Progressbar
        style.configure("TProgressbar", troughcolor=PANEL_BG, background=ACCENT_COLOR,
                         borderwidth=0, thickness=4)

        # Separator
        style.configure("TSeparator", background=BORDER_COLOR)

    # ウィジェット作成
    # ──────────────────────────────────────────────
    def _create_widgets(self):
        # ── ステータスバー（最初に配置して、押し出されないようにする） ──
        statusbar = ttk.Frame(self.root, style="Panel.TFrame")
        statusbar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Separator(statusbar, orient="horizontal").pack(fill=tk.X)
        _sb_inner = ttk.Frame(statusbar, style="Panel.TFrame", padding=(12, 4))
        _sb_inner.pack(fill=tk.X)
        ttk.Label(_sb_inner, textvariable=self.status_var, style="Status.TLabel").pack(side=tk.LEFT)
        ttk.Label(_sb_inner, text=f"Gallery-DL GUI {APP_VERSION}", style="Status.TLabel").pack(side=tk.RIGHT)

        # ── メインスクロールエリア ──
        outer = ttk.Frame(self.root, padding="16 14 16 10")
        outer.pack(fill=tk.BOTH, expand=True)

        # ── ヘッダー ──
        hdr = ttk.Frame(outer)
        hdr.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(hdr, text="Gallery-DL  GUI", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(hdr, text=APP_VERSION, style="Ver.TLabel").pack(side=tk.LEFT, padx=(8, 0), anchor="s", pady=(0, 3))

        # ── 設定フレーム ──
        settings = ttk.LabelFrame(outer, text=" Settings ", padding=12)
        settings.pack(fill=tk.X, pady=(0, 10))

        # URL行
        url_row = ttk.Frame(settings)
        url_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(url_row, text="Target URL").pack(anchor=tk.W, pady=(0, 4))

        url_input_row = ttk.Frame(url_row)
        url_input_row.pack(fill=tk.X)
        self.url_entry = tk.Entry(
            url_input_row, textvariable=self.url_var,
            bg=ENTRY_BG, fg=FG_COLOR, insertbackground=FG_COLOR,
            font=FONT_MONO, relief=tk.FLAT, bd=6, highlightthickness=1,
            highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_COLOR
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_entry.bind("<Return>", lambda _: self._start_download())

        ttk.Button(url_input_row, text="Paste", style="Small.TButton",
                   command=self._paste_url).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(url_input_row, text="Clear", style="Small.TButton",
                   command=lambda: self.url_var.set("")).pack(side=tk.LEFT, padx=(4, 0))

        # クッキー行
        ck_row = ttk.Frame(settings)
        ck_row.pack(fill=tk.X)

        ck_top = ttk.Frame(ck_row)
        ck_top.pack(fill=tk.X, pady=(0, 6))
        ttk.Checkbutton(ck_top, text="Use Cookie", variable=self.use_cookie_var,
                         command=self._toggle_cookie).pack(side=tk.LEFT, padx=(0, 10))
        self.cookie_combo = ttk.Combobox(ck_top, textvariable=self.cookie_var,
                                          state="disabled", font=FONT_MAIN)
        self.cookie_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ck_btns = ttk.Frame(ck_row)
        ck_btns.pack(fill=tk.X)
        ttk.Button(ck_btns, text="Convert JSON → Cookie",
                   command=self._convert_cookies).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(ck_btns, text="Reload List",
                   style="Small.TButton",
                   command=lambda: self._load_cookies(feedback=True)).pack(side=tk.LEFT)

        # ── アクションボタン ──
        act_row = ttk.Frame(outer)
        act_row.pack(fill=tk.X, pady=(0, 8))

        self.start_btn = ttk.Button(act_row, text="▶  Start Download",
                                    command=self._start_download, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        self.stop_btn = ttk.Button(act_row, text="■  Stop",
                                   command=self._stop_download, state="disabled",
                                   style="Danger.TButton", cursor="hand2")
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), ipady=6)

        # ── プログレスバー ──
        self.progress_bar = ttk.Progressbar(outer, mode="indeterminate", style="TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))

        # ── 統計行 ──
        stats_row = ttk.Frame(outer)
        stats_row.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(stats_row, textvariable=self.stats_var, style="Stat.TLabel").pack(side=tk.LEFT)

        # ── フォルダクイックアクセスボタン ──
        fld = ttk.LabelFrame(outer, text=" Quick Open ", padding=6)
        fld.pack(fill=tk.X, pady=(0, 10))
        for label, d in [("📁 Cookies", self.cookie_dir),
                          ("📁 JSON Input", self.json_input_dir),
                          ("📁 Downloads", self.download_dir)]:
            ttk.Button(fld, text=label, style="Small.TButton",
                       command=lambda _d=d: self._open_folder(_d)).pack(
                side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        # ── 出力ノートブック ──
        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # タブ 1 – ログ
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="  Log  ")

        log_ctrl = ttk.Frame(log_tab)
        log_ctrl.pack(fill=tk.X, pady=(6, 2))
        ttk.Button(log_ctrl, text="Clear Log", style="Small.TButton",
                   command=self._clear_log).pack(side=tk.RIGHT, padx=4)

        self.log_text = scrolledtext.ScrolledText(
            log_tab, bg=BG_COLOR, fg=FG_COLOR,
            insertbackground=FG_COLOR, font=FONT_MONO,
            state="disabled", relief=tk.FLAT, bd=0,
            selectbackground=ACCENT_COLOR, selectforeground="#ffffff"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self._configure_log_tags()

        # タブ 2 – 失敗アイテム
        failed_tab = ttk.Frame(self.notebook)
        self.notebook.add(failed_tab, text="  Failed Items  ")

        failed_ctrl = ttk.Frame(failed_tab)
        failed_ctrl.pack(fill=tk.X, pady=(6, 2))
        ttk.Button(failed_ctrl, text="Copy All", style="Small.TButton",
                   command=self._copy_failed).pack(side=tk.RIGHT, padx=4)
        ttk.Button(failed_ctrl, text="Clear", style="Small.TButton",
                   command=self._clear_failed).pack(side=tk.RIGHT, padx=2)

        self.failed_text = scrolledtext.ScrolledText(
            failed_tab, bg=BG_COLOR, fg=ERROR_COLOR,
            insertbackground=FG_COLOR, font=FONT_MONO,
            state="disabled", relief=tk.FLAT, bd=0,
            selectbackground=ACCENT_COLOR, selectforeground="#ffffff"
        )
        self.failed_text.pack(fill=tk.BOTH, expand=True)

    def _configure_log_tags(self):
        self.log_text.tag_configure("info",    foreground=FG_COLOR)
        self.log_text.tag_configure("success", foreground=SUCCESS_COLOR)
        self.log_text.tag_configure("warning", foreground=WARNING_COLOR)
        self.log_text.tag_configure("error",   foreground=ERROR_COLOR)
        self.log_text.tag_configure("dim",     foreground=DIM_COLOR)
        self.log_text.tag_configure("accent",  foreground=ACCENT_COLOR)

    # クッキーヘルパー
    # ──────────────────────────────────────────────
    def _load_cookies(self, feedback=False):
        self.cookie_files = []
        if os.path.isdir(self.cookie_dir):
            try:
                files = sorted(
                    f for f in os.listdir(self.cookie_dir)
                    if os.path.isfile(os.path.join(self.cookie_dir, f)) and f.endswith(".txt")
                )
                self.cookie_files = files
                self.cookie_combo["values"] = files
                if files:
                    self.cookie_combo.current(0)
                if feedback:
                    self._log(f"Cookie list refreshed — {len(files)} file(s) found.", "success")
            except Exception as e:
                self._log(f"Error loading cookies: {e}", "error")
        else:
            if feedback:
                self._log(f"Cookie directory not found: {self.cookie_dir}", "warning")

    def _convert_cookies(self):
        """JSON クッキーファイルを Netscape 形式にインラインで変換する（外部スクリプト不要）。"""
        json_files = glob.glob(os.path.join(self.json_input_dir, "*.json"))
        if not json_files:
            self._log(f"No JSON files found in {self.json_input_dir}/", "warning")
            return

        os.makedirs(self.cookie_dir, exist_ok=True)
        self._log(f"Found {len(json_files)} JSON file(s). Starting conversion…", "accent")

        def _run():
            converted = {"count": 0}
            for json_path in json_files:
                try:
                    filename = os.path.basename(json_path)
                    stem = os.path.splitext(filename)[0]

                    # ファイル名が汎用的な場合のみ名前変更を促す
                    if stem.lower() in ("cookies", "cookie"):
                        new_name = self._ask_string(
                            "Rename Cookie",
                            f'"{filename}" is a generic name.\nEnter a descriptive name (no extension):'
                        )
                        if not new_name:
                            self.root.after(0, lambda p=filename: self._log(f"Skipped: {p} (no name given)", "dim"))
                            continue
                        stem = "".join(
                            c for c in new_name if c.isalnum() or c in (" ", ".", "_", "-")
                        ).strip() or stem

                    txt_path = os.path.join(self.cookie_dir, f"{stem}.txt")
                    with open(json_path, "r", encoding="utf-8") as f:
                        cookies = json.load(f)

                    with open(txt_path, "w", encoding="utf-8", newline="\n") as f:
                        f.write("# Netscape HTTP Cookie File\n")
                        f.write("# Converted by Gallery-DL GUI\n\n")
                        for c in cookies:
                            domain  = c.get("domain", "")
                            flag    = "FALSE" if c.get("hostOnly", False) else "TRUE"
                            path    = c.get("path", "/")
                            secure  = "TRUE" if c.get("secure", False) else "FALSE"
                            expiry  = str(int(c.get("expiry") or c.get("expirationDate") or 0))
                            name    = c.get("name", "")
                            value   = c.get("value", "")
                            f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n")

                    os.remove(json_path)
                    converted["count"] += 1
                    self.root.after(0, lambda s=stem: self._log(f"Converted → cookies/{s}.txt", "success"))

                except Exception as e:
                    self.root.after(0, lambda p=json_path, err=e: self._log(f"Error converting {p}: {err}", "error"))

            self.root.after(0, self._load_cookies)
            n = converted["count"]
            msg = f"{n} cookie file(s) converted successfully."
            self.root.after(0, lambda m=msg: messagebox.showinfo("Conversion Complete", m))

        threading.Thread(target=_run, daemon=True).start()

    def _ask_string(self, title: str, prompt: str) -> Optional[str]:
        """tk.simpledialog を使用したスレッドセーフな文字列ダイアログ。"""
        result: List[Optional[str]] = [None]
        done = threading.Event()

        def _show():
            from tkinter import simpledialog
            result[0] = simpledialog.askstring(title, prompt, parent=self.root)
            done.set()

        self.root.after(0, _show)
        done.wait(timeout=120)
        return result[0]

    def _toggle_cookie(self):
        state = "readonly" if self.use_cookie_var.get() else "disabled"
        self.cookie_combo.configure(state=state)

    # ダウンロード
    # ──────────────────────────────────────────────
    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a URL.")
            return

        # gallery-dl の引数を構築
        conf_path = os.path.abspath("gallery-dl.conf")
        gallery_dl_args = [
            "--config", conf_path,
            "--retries", str(self.MAX_RETRIES),
            url,
        ]

        if self.use_cookie_var.get():
            cookie_file = self.cookie_var.get()
            if cookie_file:
                cookie_path = os.path.abspath(os.path.join(self.cookie_dir, cookie_file))
                gallery_dl_args = ["--cookies", cookie_path] + gallery_dl_args
            else:
                self._log("Warning: no cookie file selected, continuing without cookies.", "warning")

        # UIをリセット
        self.fail_count = 0
        self.download_count = 0
        self.retry_count = 0
        self._stop_flag = False
        self.stats_var.set("")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set("Downloading…")

        self._reset_log()
        self._reset_failed()

        self._log("─" * 56, "dim")
        self._log(f"gallery-dl {' '.join(gallery_dl_args)}", "dim")
        self._log("─" * 56, "dim")

        self.progress_bar.start(12)

        # 実行モードの選択: 常にポータブル python.exe 経由でサブプロセスを使用
        # ベースディレクトリ（スクリプトまたはビルド済み exe）を解決
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        python_exe = os.path.join(base_dir, "python", "python.exe")
        if os.path.exists(python_exe):
            cmd = [python_exe, "-m", "gallery_dl"] + gallery_dl_args
        else:
            # バンドルされた Python がない開発環境用のフォールバック
            cmd = ["gallery-dl"] + gallery_dl_args

        threading.Thread(target=self._run_process, args=(cmd,), daemon=True).start()

    def _stop_download(self, reason: str = "ユーザーによる停止"):
        self._stop_flag = True
        if self.process:
            try:
                self._log("強制終了を試みています...", "warning")
                self.process.kill() # 即座に停止
            except Exception as e:
                self._log(f"プロセス終了エラー: {e}", "error")

        # 書きかけのファイルを削除
        if self.current_download_path and os.path.exists(self.current_download_path):
            try:
                # 削除を試みる。使用中の場合は少し待つ
                import time
                time.sleep(0.1)
                os.remove(self.current_download_path)
                self._log(f"不完全なファイルを削除しました: {os.path.basename(self.current_download_path)}", "dim")
            except Exception as e:
                self._log(f"ファイル削除に失敗: {e}", "dim")
            finally:
                self.current_download_path = None

        self._log(f"停止中… ({reason})", "warning")
        self.stop_btn.configure(state="disabled")

        # _run_gallery_dl_inprocess は、ビルド済み EXE ではサブプロセスモードの方が信頼性が高いため削除されました。

    _HTTP_ERR_RE = re.compile(r'\b([45]\d{2})\b')
    _RETRY_RE    = re.compile(r'Retrying\s+(\d+)/(\d+)', re.IGNORECASE)
    _SKIP_RE     = re.compile(r'\bskipping\b|\bskipped\b',  re.IGNORECASE)
    # パス判定 (gallery-dlのパス出力形式に合わせる。絶対・相対パス両方考慮)
    _PATH_RE     = re.compile(r'(?:#\s*\d+\s+)([^\s\'"<>{}|\\^~\[\]`]+)')

    def _process_output_line(self, line: str, last_url: Optional[str]):
        """単一の出力行を分類して UI に送る共通ロジック。"""
        url_match = re.search(r'https?://[^\s\'"<>{}|\\^~\[\]`]+', line)
        low = line.lower()

        # リトライ検出
        retry_m = self._RETRY_RE.search(line)
        if retry_m:
            cur   = int(retry_m.group(1))
            total = int(retry_m.group(2))
            self.retry_count += 1
            http_m   = self._HTTP_ERR_RE.search(line)
            code_str = f" (HTTP {http_m.group(1)})" if http_m else ""
            rline = f"🔄 リトライ {cur}/{total}{code_str} — {line.strip()}"
            stats = (f"Downloaded: {self.download_count}  |  "
                     f"Failed: {self.fail_count}  |  Retry: {self.retry_count}")
            self.root.after(0, lambda l=rline: self._log(l, "warning"))
            self.root.after(0, lambda s=stats: self.stats_var.set(s))
            return

        # パス捕捉 (ダウンロード開始)
        path_m = self._PATH_RE.search(line)
        if path_m:
            captured_path = path_m.group(1)
            # 実際にダウンロード対象のファイルっぽいか簡易チェック
            if "." in os.path.basename(captured_path):
                self.current_download_path = os.path.abspath(captured_path)

        # スキップ検出（10回失敗後にgallery-dlが自動スキップ）
        if self._SKIP_RE.search(line) and "[" in line:
            http_m   = self._HTTP_ERR_RE.search(line)
            code_str = f" HTTP {http_m.group(1)}" if http_m else ""
            sline    = f"⏭ Skip{code_str}: {line.strip()}"
            cur_url  = url_match.group(0) if url_match else last_url
            fi       = f"{sline} | URL: {cur_url}" if cur_url else sline
            self.fail_count += 1
            stats = (f"Downloaded: {self.download_count}  |  "
                     f"Failed: {self.fail_count}  |  Retry: {self.retry_count}")
            self.root.after(0, lambda l=sline: self._log(l, "error"))
            self.root.after(0, lambda f=fi, s=stats:
                            (self._log_failed(f), self.stats_var.set(s)))
            return

        # 通常のエラー判定（エラーキーワード or HTTP 4xx/5xx）
        http_m   = self._HTTP_ERR_RE.search(line)
        is_error = ("[error]" in low or "failed" in low
                    or "exception" in low or http_m is not None)

        if re.match(r"#\s*\d+", line):
            self.download_count += 1

        failed_item = None
        if is_error:
            self.fail_count += 1
            code_str = f" [HTTP {http_m.group(1)}]" if http_m else ""
            m = re.search(r"'(.*?)'", line)
            if m:
                desc = m.group(1) + code_str
            elif "[error]" in low:
                desc = line.split("[error]", 1)[1].strip() + code_str
            else:
                desc = line + code_str
            cur_url = url_match.group(0) if url_match else last_url
            if cur_url:
                failed_item = (f"URL: {cur_url}" if (not desc or cur_url in desc)
                               else f"{desc} | URL: {cur_url}")
            else:
                failed_item = desc
            if http_m and http_m.group(1) not in line:
                line = f"{line.rstrip()}  [HTTP {http_m.group(1)}]"

        if is_error:
            tag = "error"
        elif "[warning]" in low:
            tag = "warning"
        elif line.startswith("#"):
            tag = "success"
        elif line.startswith("─") or line.startswith("-"):
            tag = "dim"
        else:
            tag = "info"

        speed_m = re.search(r'(\d+\.?\d*\s*\w+/s)', line)
        speed = speed_m.group(1) if speed_m else ""
        stats = f"Failed: {self.fail_count}  |  Retry: {self.retry_count}"
        if speed:
            stats += f"  |  {speed}"

        self.root.after(0, lambda l=line, t=tag, fi=failed_item, s=stats:
                        self._update_all(l, t, fi, s))

    def _watch_timeout(self, worker_thread: threading.Thread, proc):
        """応答なし・ダウンロード停止を監視して自動停止する。"""
        import time
        while worker_thread.is_alive() and not self._stop_flag:
            time.sleep(1)
            if self._stop_flag:
                break
            elapsed = time.monotonic() - self._last_activity_time
            if elapsed >= self.TIMEOUT_SECONDS:
                msg = f"\u23f1 {self.TIMEOUT_SECONDS}\u79d2\u9593\u5fdc\u7b54\u304c\u306a\u3044\u305f\u3081\u81ea\u52d5\u505c\u6b62\u3057\u307e\u3059\u3002"
                self.root.after(0, lambda m=msg: self._log(m, "warning"))
                self._stop_download(reason=f"\u30bf\u30a4\u30e0\u30a2\u30a6\u30c8 ({self.TIMEOUT_SECONDS}\u79d2)")
                _p = proc
                if _p is not None:
                    try:
                        _p.terminate()
                    except Exception:
                        pass
                break

    def _run_process(self, cmd: List[str]):
        import time
        self._last_activity_time = time.monotonic()
        try:
            si = None
            if os.name == "nt":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            env = os.environ.copy()
            env.update({"PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"})

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, universal_newlines=True,
                startupinfo=si, env=env,
                encoding="utf-8", errors="replace"
            )
            proc = self.process
            stdout = proc.stdout
            if not stdout:
                return

            # タイムアウト監視スレッド
            wt = threading.current_thread()
            threading.Thread(
                target=self._watch_timeout,
                args=(wt, proc),
                daemon=True
            ).start()

            last_url: Optional[str] = None

            for raw_line in stdout:
                if self._stop_flag:
                    break
                line = raw_line.rstrip()
                if not line:
                    continue

                self._last_activity_time = time.monotonic()  # 活動時刻を更新

                # 最後に確認したURLを追跡
                url_match = re.search(r'https?://[^\s\'"<>{}|\\^~\[\]`]+', line)
                if url_match:
                    last_url = url_match.group(0)

                low = line.lower()
                is_error = "[error]" in low or "failed" in low or "exception" in low

                # ダウンロードを検出（gallery-dl はダウンロード時に "#" プレフィックスを出力する）
                if re.match(r"#\s*\d+", line):
                    self.download_count += 1

                failed_item = None
                if is_error:
                    self.fail_count += 1
                    m = re.search(r"'(.*?)'", line)
                    if m:
                        desc = m.group(1)
                    elif "[error]" in low:
                        desc = line.split("[error]", 1)[1].strip()
                    else:
                        desc = line

                    cur_url = url_match.group(0) if url_match else last_url
                    if cur_url:
                        failed_item = (f"URL: {cur_url}" if (not desc or cur_url in desc)
                                       else f"{desc} | URL: {cur_url}")
                    else:
                        failed_item = desc

                # タグを選択
                if is_error:
                    tag = "error"
                elif "[warning]" in low:
                    tag = "warning"
                elif line.startswith("#"):
                    tag = "success"
                elif line.startswith("─") or line.startswith("-"):
                    tag = "dim"
                else:
                    tag = "info"

                # 速度検出
                speed_m = re.search(r'(\d+\.?\d*\s*\w+/s)', line)
                speed = speed_m.group(1) if speed_m else ""

                stats = f"Failed: {self.fail_count}"
                if speed:
                    stats += f"  |  {speed}"

                self.root.after(0, lambda l=line, t=tag, fi=failed_item, s=stats:
                                self._update_all(l, t, fi, s))

            proc.wait()
            code = proc.returncode
            if self._stop_flag:
                msg = "停止しました"
                final_tag = "warning"
                final_status = "Stopped"
            else:
                msg = f"Finished  —  exit code {code}"
                final_tag = "success" if code == 0 else "warning"
                final_status = "Done" if code == 0 else f"Done with errors (code {code})"
            final_stats = f"Failed: {self.fail_count}"

            self.root.after(0, lambda: self._update_all(msg, final_tag, None, final_stats))
            self.root.after(0, lambda: self.status_var.set(final_status))

        except FileNotFoundError:
            self.root.after(0, lambda: self._log("Error: gallery-dl not found.", "error"))
            self.root.after(0, lambda: self.status_var.set("Error"))
        except Exception as exc:
            msg = str(exc)
            self.root.after(0, lambda m=msg: self._log(f"Error: {m}", "error"))
            self.root.after(0, lambda: self.status_var.set("Error"))
        finally:
            self.process = None
            self.root.after(0, self._finish_download)

    def _finish_download(self):
        self.progress_bar.stop()
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _update_all(self, line: str, tag: str, failed_item: Optional[str], stats: str):
        self._log(line, tag)
        if failed_item:
            self._log_failed(failed_item)
        self.stats_var.set(stats)

    # ログヘルパー
    # ──────────────────────────────────────────────
    def _log(self, message: str, tag: str = "info"):
        if not self.log_text:
            return
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def _log_failed(self, message: str):
        if not self.failed_text:
            return
        self.failed_text.configure(state="normal")
        self.failed_text.insert(tk.END, message + "\n")
        self.failed_text.see(tk.END)
        self.failed_text.configure(state="disabled")
        # アクティブでない場合はタブにマークを付ける
        if self.notebook.index(self.notebook.select()) != 1:
            self.notebook.tab(1, text="  ⚠ Failed Items  ")

    def _reset_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def _reset_failed(self):
        self.failed_text.configure(state="normal")
        self.failed_text.delete("1.0", tk.END)
        self.failed_text.configure(state="disabled")
        self.notebook.tab(1, text="  Failed Items  ")

    def _clear_log(self):
        self._reset_log()
        self._log("Log cleared.", "dim")

    def _clear_failed(self):
        self._reset_failed()

    def _copy_failed(self):
        content = self.failed_text.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self._log("Failed items copied to clipboard.", "success")
        else:
            self._log("Nothing to copy.", "dim")

    def _on_tab_change(self, _event=None):
        # ユーザーが確認したときに失敗タブの通知マークをリセットする
        if self.notebook.index(self.notebook.select()) == 1:
            self.notebook.tab(1, text="  Failed Items  ")

    # その他
    # ──────────────────────────────────────────────
    def _paste_url(self):
        try:
            text = self.root.clipboard_get()
            self.url_var.set(text.strip())
        except Exception:
            pass

    def _open_folder(self, folder: str):
        path = os.path.abspath(folder)
        os.makedirs(path, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(path)
            else:
                subprocess.Popen(["open", path])
        except Exception as e:
            self._log(f"Could not open folder: {e}", "error")


if __name__ == "__main__":
    root = tk.Tk()
    app = GalleryDLApp(root)
    root.mainloop()
