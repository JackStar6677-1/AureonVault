import ctypes
import os
import pathlib
import string
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk


APP_NAME = "AureonVault"
BG = "#09040f"
PANEL = "#160a23"
PANEL_ALT = "#1f1031"
CARD = "#281544"
CARD_BRIGHT = "#34195a"
GOLD = "#ffd36a"
GOLD_SOFT = "#ffebb0"
PURPLE = "#b160ff"
PURPLE_SOFT = "#d8b5ff"
TEXT = "#f6edff"
MUTED = "#c2b1d8"
ACCENT = "#7df2ff"
ROW_HOVER = "#2d1750"
ROW_ACTIVE = "#3c1f67"
BORDER = "#3a2458"
SUCCESS = "#89f7b8"
WARNING = "#ff9ed9"
FONT = "Segoe UI"


def human_size(size: int) -> str:
    if size <= 0:
        return "--"
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024
        index += 1
    if index == 0:
        return f"{int(value)} {units[index]}"
    return f"{value:.1f} {units[index]}"


def format_dt(timestamp: float) -> str:
    if not timestamp:
        return "--"
    try:
        return datetime.fromtimestamp(timestamp).strftime("%d-%m-%Y %H:%M")
    except OSError:
        return "--"


def get_drives() -> list[str]:
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def reveal_in_explorer(path: str) -> None:
    if not os.path.exists(path):
        return
    subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])


def open_path(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    normalized = os.path.normpath(path)

    try:
        os.startfile(normalized)
        return
    except OSError:
        pass

    try:
        subprocess.Popen(["cmd", "/c", "start", "", normalized], shell=False)
        return
    except OSError:
        pass

    if os.path.isdir(normalized):
        subprocess.Popen(["explorer", normalized])
        return

    raise OSError(f"No se pudo abrir: {normalized}")


def is_hidden_folder(name: str) -> bool:
    return name.lower() in {"$recycle.bin", "system volume information"}


def is_previewable_text(path: str) -> bool:
    return pathlib.Path(path).suffix.lower() in {
        ".txt",
        ".md",
        ".ps1",
        ".bat",
        ".cmd",
        ".py",
        ".js",
        ".json",
        ".csv",
        ".html",
        ".css",
        ".xml",
        ".log",
        ".ini",
        ".yml",
        ".yaml",
    }


def read_preview(path: str, limit: int = 1400) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            data = handle.read(limit)
        return data.strip() or "(archivo de texto vacio)"
    except OSError:
        return ""


def shorten_path(value: str, limit: int = 42) -> str:
    if not value:
        return ""
    if len(value) <= limit:
        return value
    return f"...{value[-(limit - 3):]}"


def icon_for_item(item: dict) -> str:
    if item["is_dir"]:
        return "[DIR]"
    suffix = pathlib.Path(item["name"]).suffix.lower()
    mapping = {
        ".exe": "[APP]",
        ".msi": "[APP]",
        ".lnk": "[LNK]",
        ".txt": "[TXT]",
        ".md": "[TXT]",
        ".doc": "[DOC]",
        ".docx": "[DOC]",
        ".pdf": "[PDF]",
        ".xls": "[XLS]",
        ".xlsx": "[XLS]",
        ".ppt": "[PPT]",
        ".pptx": "[PPT]",
        ".png": "[IMG]",
        ".jpg": "[IMG]",
        ".jpeg": "[IMG]",
        ".gif": "[IMG]",
        ".mp3": "[AUD]",
        ".wav": "[AUD]",
        ".mp4": "[VID]",
        ".mkv": "[VID]",
        ".zip": "[ZIP]",
        ".rar": "[ZIP]",
        ".7z": "[ZIP]",
        ".py": "[CMD]",
        ".ps1": "[CMD]",
        ".bat": "[CMD]",
        ".cmd": "[CMD]",
        ".json": "[CFG]",
    }
    return mapping.get(suffix, "[FILE]")


class AureonVaultApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AureonVault")
        self.geometry("1460x920")
        self.minsize(1120, 720)
        self.configure(bg=BG)

        self.current_path = None
        self.current_items = []
        self.filtered_items = []
        self.selected_item = None
        self.items_by_path = {}
        self.search_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listando...")
        self.count_var = tk.StringVar(value="0")
        self.folder_count_var = tk.StringVar(value="0")
        self.file_count_var = tk.StringVar(value="0")
        self.current_path_var = tk.StringVar(value="Cargando...")
        self.sort_var = tk.StringVar(value="Nombre A-Z")
        self.console_cmd_var = tk.StringVar()
        self.console_mode_var = tk.StringVar(value="PowerShell")
        self.admin_var = tk.BooleanVar(value=False)

        self._configure_style()
        self._build_ui()
        self._bind_events()
        self._load_sidebar()
        initial = get_drives()[0] if get_drives() else pathlib.Path.home().anchor
        self.load_directory(initial)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Vault.Treeview",
            background=PANEL,
            fieldbackground=PANEL,
            foreground=TEXT,
            borderwidth=0,
            rowheight=31,
            font=(FONT, 10),
        )
        style.configure(
            "Vault.Treeview.Heading",
            background=PANEL_ALT,
            foreground=GOLD_SOFT,
            relief="flat",
            font=(FONT, 9, "bold"),
        )
        style.map(
            "Vault.Treeview",
            background=[("selected", ROW_ACTIVE)],
            foreground=[("selected", TEXT)],
        )
        style.configure(
            "Vault.TCombobox",
            fieldbackground="#12081d",
            background="#12081d",
            foreground=TEXT,
            arrowcolor=GOLD,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
        )
        style.configure(
            "Vault.TNotebook",
            background=PANEL_ALT,
            borderwidth=0,
        )
        style.configure(
            "Vault.TNotebook.Tab",
            background="#25133b",
            foreground=MUTED,
            padding=(16, 8),
            font=(FONT, 9, "bold"),
            borderwidth=0,
        )
        style.map(
            "Vault.TNotebook.Tab",
            background=[("selected", CARD_BRIGHT), ("active", "#3a1d61")],
            foreground=[("selected", TEXT), ("active", GOLD_SOFT)],
        )

    def _build_ui(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = tk.Frame(self, bg=PANEL_ALT, bd=0, highlightthickness=1, highlightbackground=BORDER)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.configure(width=262)
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(4, weight=1)

        brand = tk.Frame(sidebar, bg=CARD_BRIGHT)
        brand.grid(row=0, column=0, padx=14, pady=14, sticky="ew")
        brand.grid_columnconfigure(1, weight=1)
        logo = tk.Label(
            brand,
            text="AV",
            fg=BG,
            bg=GOLD,
            font=(FONT, 17, "bold"),
            width=3,
            height=2,
        )
        logo.grid(row=0, column=0, padx=(10, 12), pady=10)
        title_wrap = tk.Frame(brand, bg=CARD_BRIGHT)
        title_wrap.grid(row=0, column=1, sticky="w")
        tk.Label(title_wrap, text="JackStar Signature", fg=GOLD_SOFT, bg=CARD_BRIGHT, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(title_wrap, text="AureonVault", fg=TEXT, bg=CARD_BRIGHT, font=(FONT, 17, "bold")).pack(anchor="w")
        tk.Label(title_wrap, text="File admin premium", fg=MUTED, bg=CARD_BRIGHT, font=(FONT, 9)).pack(anchor="w")

        self.quick_frame = self._make_sidebar_section(sidebar, 1, "Acceso rapido")
        self.drives_frame = self._make_sidebar_section(sidebar, 2, "Unidades")

        actions = tk.Frame(sidebar, bg=PANEL_ALT)
        actions.grid(row=3, column=0, sticky="ew", padx=14, pady=(4, 0))
        tk.Button(actions, text="Abrir carpeta actual", command=self.open_current_dir, **self._btn_cfg()).pack(fill="x", pady=4)
        tk.Button(actions, text="Abrir seleccion", command=self.open_selected, **self._btn_cfg()).pack(fill="x", pady=4)

        footer = tk.Label(
            sidebar,
            text="Morado, dorado y hecho para JackStar.",
            fg=MUTED,
            bg=PANEL_ALT,
            font=(FONT, 8),
        )
        footer.grid(row=5, column=0, sticky="sw", padx=14, pady=14)

        main = tk.Frame(self, bg=BG)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(3, weight=1)

        hero = tk.Frame(main, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
        hero.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=0)

        hero_left = tk.Frame(hero, bg=CARD)
        hero_left.grid(row=0, column=0, sticky="w", padx=18, pady=16)
        tk.Label(hero_left, text="Explorador del sistema completo", fg=GOLD_SOFT, bg=CARD, font=(FONT, 8, "bold")).pack(anchor="w")
        tk.Label(
            hero_left,
            text="Un file manager con estilo propio, rapido y pensado para escritorio.",
            fg=TEXT,
            bg=CARD,
            font=(FONT, 16, "bold"),
            wraplength=620,
            justify="left",
        ).pack(anchor="w", pady=(4, 2))
        tk.Label(
            hero_left,
            text="Navega unidades, carpetas y archivos con una interfaz redimensionable, mas clara y mas viva.",
            fg=MUTED,
            bg=CARD,
            font=(FONT, 10),
            wraplength=700,
            justify="left",
        ).pack(anchor="w")

        hero_right = tk.Frame(hero, bg=CARD)
        hero_right.grid(row=0, column=1, sticky="e", padx=16, pady=16)
        self._make_stat(hero_right, "Ruta actual", self.current_path_var, 0)
        self._make_stat(hero_right, "Elementos visibles", self.count_var, 1)
        self._make_stat(hero_right, "Carpetas", self.folder_count_var, 2)
        self._make_stat(hero_right, "Archivos", self.file_count_var, 3)

        toolbar = tk.Frame(main, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        toolbar.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))
        toolbar.grid_columnconfigure(2, weight=1)
        toolbar.grid_columnconfigure(3, weight=1)
        toolbar.grid_columnconfigure(4, weight=0)

        tk.Button(toolbar, text="Subir", command=self.go_up, **self._btn_cfg()).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(toolbar, text="Refrescar", command=lambda: self.load_directory(self.current_path), **self._btn_cfg()).grid(row=0, column=1, padx=(0, 10), pady=10)

        self.path_entry = tk.Entry(toolbar, textvariable=self.path_var, bg="#12081d", fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 10))
        self.path_entry.grid(row=0, column=2, sticky="ew", padx=(0, 10), pady=10, ipady=8)

        self.search_entry = tk.Entry(toolbar, textvariable=self.search_var, bg="#12081d", fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 10))
        self.search_entry.grid(row=0, column=3, sticky="ew", padx=(0, 10), pady=10, ipadx=24, ipady=8)
        self.search_entry.insert(0, "")
        self.search_entry.configure(width=22)

        self.sort_combo = ttk.Combobox(
            toolbar,
            textvariable=self.sort_var,
            values=("Nombre A-Z", "Nombre Z-A", "Mas reciente", "Mas pesado", "Tipo"),
            state="readonly",
            style="Vault.TCombobox",
            width=18,
        )
        self.sort_combo.grid(row=0, column=4, padx=(0, 10), pady=10, ipady=4)

        breadcrumb_card = tk.Frame(main, bg=PANEL_ALT, highlightthickness=1, highlightbackground=BORDER)
        breadcrumb_card.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
        tk.Label(breadcrumb_card, text="Ruta navegable", fg=GOLD_SOFT, bg=PANEL_ALT, font=(FONT, 9, "bold")).pack(anchor="w", padx=14, pady=(10, 4))
        self.breadcrumb_frame = tk.Frame(breadcrumb_card, bg=PANEL_ALT)
        self.breadcrumb_frame.pack(fill="x", padx=10, pady=(0, 10))

        split = tk.PanedWindow(main, orient="horizontal", bg=BG, sashwidth=8, sashrelief="flat")
        split.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 12))

        left_panel = tk.Frame(split, bg=PANEL, highlightthickness=1, highlightbackground=BORDER)
        right_panel = tk.Frame(split, bg=PANEL_ALT, highlightthickness=1, highlightbackground=BORDER)
        split.add(left_panel, stretch="always", minsize=760)
        split.add(right_panel, minsize=320)

        left_panel.grid_rowconfigure(2, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        tk.Label(left_panel, text="Navegacion", fg=PURPLE_SOFT, bg=PANEL, font=(FONT, 9, "bold")).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        tk.Label(left_panel, textvariable=self.status_var, fg=GOLD_SOFT, bg=PANEL, font=(FONT, 8)).grid(row=0, column=0, sticky="e", padx=16, pady=(14, 8))

        self.tree = ttk.Treeview(
            left_panel,
            columns=("extension", "type", "size", "modified"),
            show="tree headings",
            style="Vault.Treeview",
            selectmode="browse",
        )
        self.tree.heading("#0", text="Nombre")
        self.tree.heading("extension", text="Ext")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("size", text="Tamano")
        self.tree.heading("modified", text="Modificado")
        self.tree.column("#0", width=400, stretch=True, anchor="w")
        self.tree.column("extension", width=70, stretch=False, anchor="center")
        self.tree.column("type", width=120, stretch=False, anchor="w")
        self.tree.column("size", width=110, stretch=False, anchor="e")
        self.tree.column("modified", width=155, stretch=False, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 16))

        tk.Label(right_panel, text="Panel lateral", fg=PURPLE_SOFT, bg=PANEL_ALT, font=(FONT, 9, "bold")).grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))

        right_notebook = ttk.Notebook(right_panel, style="Vault.TNotebook")
        right_notebook.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))

        detail_page = tk.Frame(right_notebook, bg=PANEL_ALT)
        console_page = tk.Frame(right_notebook, bg=PANEL_ALT)
        detail_page.grid_rowconfigure(1, weight=1)
        detail_page.grid_columnconfigure(0, weight=1)
        console_page.grid_rowconfigure(2, weight=1)
        console_page.grid_columnconfigure(0, weight=1)
        right_notebook.add(detail_page, text="Detalle")
        right_notebook.add(console_page, text="Consola")

        tk.Label(detail_page, text="Vista seleccionada", fg=GOLD_SOFT, bg=PANEL_ALT, font=(FONT, 8, "bold")).grid(row=0, column=0, sticky="ew", pady=(6, 10))
        self.detail = tk.Text(
            detail_page,
            bg=PANEL_ALT,
            fg=TEXT,
            relief="flat",
            wrap="word",
            font=(FONT, 10),
            spacing1=4,
            spacing2=2,
            spacing3=4,
        )
        self.detail.grid(row=1, column=0, sticky="nsew")
        self.detail.insert("1.0", "Selecciona un archivo o carpeta para ver su detalle.")
        self.detail.config(state="disabled")

        action_bar = tk.Frame(detail_page, bg=PANEL_ALT)
        action_bar.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        action_bar.grid_columnconfigure(0, weight=1)
        action_bar.grid_columnconfigure(1, weight=1)
        tk.Button(action_bar, text="Abrir", command=self.open_selected, **self._btn_cfg()).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        tk.Button(action_bar, text="Mostrar en carpeta", command=self.reveal_selected, **self._btn_cfg()).grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=4)
        tk.Button(action_bar, text="Entrar a carpeta", command=self.enter_selected, **self._btn_cfg()).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        tk.Button(action_bar, text="PowerShell admin", command=self.open_admin_terminal_here, **self._btn_cfg()).grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=4)

        tk.Label(console_page, text="Pagina operativa", fg=GOLD_SOFT, bg=PANEL_ALT, font=(FONT, 8, "bold")).grid(row=0, column=0, sticky="ew", pady=(6, 8))
        controls = tk.Frame(console_page, bg=PANEL_ALT)
        controls.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        controls.grid_columnconfigure(4, weight=1)
        tk.Label(controls, text="Motor", fg=TEXT, bg=PANEL_ALT, font=(FONT, 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.console_mode = ttk.Combobox(
            controls,
            textvariable=self.console_mode_var,
            values=("PowerShell", "CMD"),
            state="readonly",
            style="Vault.TCombobox",
            width=12,
        )
        self.console_mode.grid(row=0, column=1, sticky="w", padx=(0, 8))
        tk.Checkbutton(
            controls,
            text="Admin al abrir externa",
            variable=self.admin_var,
            bg=PANEL_ALT,
            fg=TEXT,
            activebackground=PANEL_ALT,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=(FONT, 8),
        ).grid(row=0, column=2, sticky="w", padx=(0, 8))
        tk.Button(controls, text="Abrir externa", command=self.open_admin_terminal_here, **self._btn_cfg()).grid(row=0, column=4, sticky="e")

        self.console_entry = tk.Entry(console_page, textvariable=self.console_cmd_var, bg="#12081d", fg=TEXT, insertbackground=TEXT, relief="flat", font=(FONT, 10))
        self.console_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10), ipady=8)

        console_actions = tk.Frame(console_page, bg=PANEL_ALT)
        console_actions.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        console_actions.grid_columnconfigure(0, weight=1)
        console_actions.grid_columnconfigure(1, weight=1)
        tk.Button(console_actions, text="Ejecutar aqui", command=self.run_console_command, **self._btn_cfg()).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        tk.Button(console_actions, text="Limpiar salida", command=self.clear_console, **self._btn_cfg()).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.console_output = tk.Text(
            console_page,
            bg="#0d0716",
            fg=SUCCESS,
            relief="flat",
            wrap="word",
            insertbackground=TEXT,
            font=("Consolas", 10),
        )
        self.console_output.grid(row=4, column=0, sticky="nsew")
        self.console_output.insert("1.0", "AureonVault Console ready.\n")
        self.console_output.config(state="disabled")

        footer = tk.Frame(main, bg=BG)
        footer.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 18))
        tk.Label(
            footer,
            text="Atajos: Enter/Doble clic abre, Alt+Arriba sube, Ctrl+L enfoca ruta, Ctrl+F enfoca filtro, F5 refresca.",
            fg=MUTED,
            bg=BG,
            font=(FONT, 9),
        ).pack(anchor="w")

    def _make_sidebar_section(self, parent, row, title):
        wrapper = tk.Frame(parent, bg=PANEL_ALT)
        wrapper.grid(row=row, column=0, sticky="ew", padx=14, pady=(0, 8))
        tk.Label(wrapper, text=title, fg=GOLD_SOFT, bg=PANEL_ALT, font=(FONT, 9, "bold")).pack(anchor="w", pady=(0, 6))
        frame = tk.Frame(wrapper, bg=PANEL_ALT)
        frame.pack(fill="x")
        return frame

    def _make_stat(self, parent, title, variable, column):
        card = tk.Frame(parent, bg="#12081d", highlightthickness=1, highlightbackground=BORDER)
        row = 0 if column < 2 else 1
        local_column = column if column < 2 else column - 2
        card.grid(row=row, column=local_column, padx=(0 if local_column == 0 else 10, 0), pady=(0 if row == 0 else 10, 0), sticky="nsew")
        tk.Label(card, text=title, fg=GOLD_SOFT, bg="#12081d", font=(FONT, 8, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        tk.Label(card, textvariable=variable, fg=TEXT, bg="#12081d", font=(FONT, 10, "bold"), wraplength=150, justify="left").pack(anchor="w", padx=14, pady=(0, 12))

    def _btn_cfg(self):
        return {
            "bg": "#2b1545",
            "fg": TEXT,
            "activebackground": "#3a1d61",
            "activeforeground": TEXT,
            "relief": "flat",
            "font": (FONT, 9, "bold"),
            "padx": 12,
            "pady": 7,
            "cursor": "hand2",
        }

    def _bind_events(self) -> None:
        self.search_var.trace_add("write", lambda *_: self.apply_filter())
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Return>", lambda _event: self.open_selected())
        self.path_entry.bind("<Return>", lambda _event: self.load_directory(self.path_var.get()))
        self.console_entry.bind("<Return>", lambda _event: self.run_console_command())
        self.search_entry.bind("<FocusIn>", self._search_placeholder_off)
        self.search_entry.bind("<FocusOut>", self._search_placeholder_on)
        self.sort_combo.bind("<<ComboboxSelected>>", lambda _event: self.apply_filter())
        self.bind_all("<F5>", lambda _event: self.load_directory(self.current_path))
        self.bind_all("<Alt-Up>", lambda _event: self.go_up())
        self.bind_all("<Control-l>", lambda _event: self.path_entry.focus_set())
        self.bind_all("<Control-f>", lambda _event: self.search_entry.focus_set())
        self._search_placeholder_on()

    def _search_placeholder_on(self, _event=None):
        if not self.search_var.get():
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, "Filtrar por nombre...")
            self.search_entry.config(fg=MUTED)

    def _search_placeholder_off(self, _event=None):
        if self.search_entry.get() == "Filtrar por nombre...":
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=TEXT)

    def _clear_buttons(self, frame: tk.Frame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _make_nav_button(self, parent: tk.Frame, name: str, target: str) -> None:
        btn = tk.Button(parent, text=name, anchor="w", command=lambda p=target: self.load_directory(p), **self._btn_cfg())
        btn.pack(fill="x", pady=4)

    def _load_sidebar(self) -> None:
        self._clear_buttons(self.quick_frame)
        self._clear_buttons(self.drives_frame)

        home = pathlib.Path.home()
        quick = [
            ("Desktop", str(home / "Desktop")),
            ("Documents", str(home / "Documents")),
            ("Downloads", str(home / "Downloads")),
            ("Pictures", str(home / "Pictures")),
            ("Music", str(home / "Music")),
            ("Videos", str(home / "Videos")),
            ("AppData", str(home / "AppData")),
            ("Temp", os.getenv("TEMP", "")),
        ]

        for label, target in quick:
            if target and os.path.exists(target):
                self._make_nav_button(self.quick_frame, label, target)

        for drive in get_drives():
            self._make_nav_button(self.drives_frame, drive, drive)

    def _refresh_breadcrumbs(self) -> None:
        for child in self.breadcrumb_frame.winfo_children():
            child.destroy()

        if not self.current_path:
            return

        current = pathlib.Path(self.current_path)
        parts = [current.anchor] if current.anchor else []
        if current.anchor:
            extras = [part for part in current.parts[1:] if part not in ("\\", "/")]
        else:
            extras = list(current.parts)
        parts.extend(extras)

        running = current.anchor.rstrip("\\") + "\\" if current.anchor else ""
        for index, part in enumerate(parts):
            if index == 0 and current.anchor:
                target = current.anchor
                label = current.anchor.rstrip("\\")
            else:
                running = os.path.join(running, part) if running else part
                target = running
                label = part

            button = tk.Button(
                self.breadcrumb_frame,
                text=label,
                command=lambda p=target: self.load_directory(p),
                bg="#25133b",
                fg=TEXT,
                activebackground="#41206c",
                activeforeground=TEXT,
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=6,
                font=(FONT, 9, "bold"),
            )
            button.pack(side="left", padx=(4, 0), pady=4)

            if index < len(parts) - 1:
                tk.Label(self.breadcrumb_frame, text=">", fg=GOLD, bg=PANEL_ALT, font=(FONT, 10, "bold")).pack(side="left", padx=6)

    def _update_folder_stats(self) -> None:
        folders = sum(1 for item in self.current_items if item["is_dir"])
        files = sum(1 for item in self.current_items if not item["is_dir"])
        self.folder_count_var.set(str(folders))
        self.file_count_var.set(str(files))

    def _sorted_items(self, items):
        mode = self.sort_var.get()
        if mode == "Nombre Z-A":
            return sorted(items, key=lambda item: (not item["is_dir"], item["name"].lower()), reverse=True)
        if mode == "Mas reciente":
            return sorted(items, key=lambda item: (not item["is_dir"], item["modified"]), reverse=True)
        if mode == "Mas pesado":
            return sorted(items, key=lambda item: (not item["is_dir"], item["size"]), reverse=True)
        if mode == "Tipo":
            return sorted(items, key=lambda item: (not item["is_dir"], pathlib.Path(item["name"]).suffix.lower(), item["name"].lower()))
        return sorted(items, key=lambda item: (not item["is_dir"], item["name"].lower()))

    def list_directory(self, target: str):
        resolved = os.path.normpath(target)
        entries = []
        with os.scandir(resolved) as iterator:
            for entry in iterator:
                if is_hidden_folder(entry.name):
                    continue
                try:
                    stats = entry.stat()
                    entries.append(
                        {
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": entry.is_dir(follow_symlinks=False),
                            "size": stats.st_size,
                            "modified": stats.st_mtime,
                        }
                    )
                except PermissionError:
                    entries.append(
                        {
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": entry.is_dir(follow_symlinks=False),
                            "size": 0,
                            "modified": 0,
                            "locked": True,
                        }
                    )

        entries.sort(key=lambda item: (not item["is_dir"], item["name"].lower()))
        return entries

    def load_directory(self, target: str) -> None:
        if not target:
            return

        target = os.path.normpath(target)
        try:
            self.current_items = self.list_directory(target)
        except Exception as error:
            messagebox.showerror(APP_NAME, f"No se pudo abrir la ruta:\n\n{target}\n\n{error}")
            return

        self.current_path = target
        self.current_path_var.set(shorten_path(target, 24))
        self.path_var.set(target)
        self.selected_item = None
        self.items_by_path = {item["path"]: item for item in self.current_items}
        self.status_var.set("Carpeta cargada")
        self._update_folder_stats()
        self._refresh_breadcrumbs()
        self.apply_filter()
        self.show_details(None)

    def apply_filter(self) -> None:
        query = self.search_entry.get().strip().lower()
        if query == "filtrar por nombre...":
            query = ""

        if query:
            self.filtered_items = [item for item in self.current_items if query in item["name"].lower()]
        else:
            self.filtered_items = list(self.current_items)

        self.filtered_items = self._sorted_items(self.filtered_items)
        self.count_var.set(str(len(self.filtered_items)))
        self.render_tree()

    def render_tree(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        for item in self.filtered_items:
            prefix = icon_for_item(item)
            label = f"{prefix} {item['name']}"
            extension = "" if item["is_dir"] else pathlib.Path(item["name"]).suffix.lower()
            item_type = "Carpeta" if item["is_dir"] else pathlib.Path(item["name"]).suffix.lower() or "Archivo"
            size = "--" if item["is_dir"] else human_size(item["size"])
            modified = format_dt(item["modified"])
            tags = ("dir",) if item["is_dir"] else ("file",)
            self.tree.insert("", "end", iid=item["path"], text=label, values=(extension, item_type, size, modified), tags=tags)
    def on_select(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            self.selected_item = None
            self.show_details(None)
            return

        path_value = selected[0]
        self.selected_item = self.items_by_path.get(path_value)
        self.show_details(self.selected_item)

    def on_double_click(self, event=None) -> None:
        item_id = self.tree.identify_row(event.y) if event else None
        if item_id:
            self.tree.selection_set(item_id)
            self.selected_item = self.items_by_path.get(item_id)
            self.show_details(self.selected_item)
        self.open_selected()

    def show_details(self, item) -> None:
        self.detail.config(state="normal")
        self.detail.delete("1.0", "end")

        if not item:
            self.detail.insert("1.0", "Selecciona un archivo o carpeta para ver su detalle.")
            self.detail.config(state="disabled")
            return

        lines = [
            f"Nombre: {item['name']}",
            "",
            f"Ruta: {item['path']}",
            f"Tipo: {'Carpeta' if item['is_dir'] else 'Archivo'}",
            f"Extension: {pathlib.Path(item['name']).suffix.lower() or '--'}",
            f"Tamano: {'--' if item['is_dir'] else human_size(item['size'])}",
            f"Modificado: {format_dt(item['modified'])}",
        ]

        if item.get("locked"):
            lines.extend(["", "Aviso: acceso parcial o restringido por permisos."])

        if not item["is_dir"] and is_previewable_text(item["path"]):
            preview = read_preview(item["path"])
            if preview:
                lines.extend(["", "Vista previa:", "--------------------", preview])

        if item["is_dir"]:
            lines.extend(
                [
                    "",
                    "Acciones sugeridas:",
                    "- Doble clic o Enter para entrar.",
                    "- Abrir para abrir la carpeta en Explorer.",
                    "- Mostrar en carpeta para ubicarla externamente.",
                ]
            )
        else:
            lines.extend(
                [
                    "",
                    "Acciones sugeridas:",
                    "- Abrir para lanzar el documento o programa.",
                    "- Mostrar en carpeta para ubicarlo rapidamente.",
                ]
            )

        self.detail.insert("1.0", "\n".join(lines))
        self.detail.config(state="disabled")

    def go_up(self) -> None:
        if not self.current_path:
            return
        parent = os.path.dirname(self.current_path)
        if not parent or parent == self.current_path:
            return
        self.load_directory(parent)

    def open_selected(self) -> None:
        if not self.selected_item:
            return
        try:
            if self.selected_item["is_dir"]:
                self.load_directory(self.selected_item["path"])
            else:
                open_path(self.selected_item["path"])
        except Exception as error:
            messagebox.showerror(APP_NAME, f"No se pudo abrir el elemento:\n\n{self.selected_item['path']}\n\n{error}")

    def open_current_dir(self) -> None:
        if self.current_path:
            try:
                open_path(self.current_path)
            except Exception as error:
                messagebox.showerror(APP_NAME, f"No se pudo abrir la carpeta actual.\n\n{error}")

    def reveal_selected(self) -> None:
        if self.selected_item:
            try:
                reveal_in_explorer(self.selected_item["path"])
            except Exception as error:
                messagebox.showerror(APP_NAME, f"No se pudo mostrar el elemento en Explorer.\n\n{error}")

    def enter_selected(self) -> None:
        if self.selected_item and self.selected_item["is_dir"]:
            self.load_directory(self.selected_item["path"])

    def _append_console(self, text: str, color: str | None = None) -> None:
        self.console_output.config(state="normal")
        if color:
            tag = color.replace("#", "c_")
            self.console_output.tag_configure(tag, foreground=color)
            self.console_output.insert("end", text, tag)
        else:
            self.console_output.insert("end", text)
        self.console_output.see("end")
        self.console_output.config(state="disabled")

    def clear_console(self) -> None:
        self.console_output.config(state="normal")
        self.console_output.delete("1.0", "end")
        self.console_output.insert("1.0", "AureonVault Console ready.\n")
        self.console_output.config(state="disabled")

    def run_console_command(self) -> None:
        command = self.console_cmd_var.get().strip()
        if not command:
            return

        workdir = self.current_path or str(pathlib.Path.home())
        mode = self.console_mode_var.get()
        self._append_console(f"\n[{mode} @ {workdir}]> {command}\n", GOLD)

        try:
            if mode == "CMD":
                result = subprocess.run(
                    ["cmd", "/c", command],
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=90,
                )
            else:
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=90,
                )

            if result.stdout:
                self._append_console(result.stdout, SUCCESS)
            if result.stderr:
                self._append_console(result.stderr, WARNING)
            self._append_console(f"[exit {result.returncode}]\n", MUTED)
        except subprocess.TimeoutExpired:
            self._append_console("[timeout] El comando tardó demasiado.\n", WARNING)
        except Exception as error:
            self._append_console(f"[error] {error}\n", WARNING)

    def open_admin_terminal_here(self) -> None:
        workdir = self.current_path or str(pathlib.Path.home())
        mode = self.console_mode_var.get()
        try:
            if self.admin_var.get():
                if mode == "CMD":
                    command = f'Start-Process cmd.exe -Verb RunAs -ArgumentList \'/k cd /d "{workdir}"\''
                else:
                    safe = workdir.replace("'", "''")
                    command = f"Start-Process powershell.exe -Verb RunAs -ArgumentList '-NoExit','-Command','Set-Location ''{safe}'''"
                subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command])
            else:
                if mode == "CMD":
                    subprocess.Popen(["cmd", "/k", f'cd /d "{workdir}"'], cwd=workdir)
                else:
                    subprocess.Popen(["powershell", "-NoExit", "-Command", f"Set-Location '{workdir}'"], cwd=workdir)
        except Exception as error:
            messagebox.showerror(APP_NAME, f"No se pudo abrir la terminal.\n\n{error}")


if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = AureonVaultApp()
    app.mainloop()
