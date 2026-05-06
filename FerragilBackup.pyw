import os
import sys
import shutil
import threading
import time
import datetime
import json
import ctypes
import ctypes.wintypes
import stat as _stat_mod

PY2 = sys.version_info[0] == 2

if PY2:
    import Tkinter as tk
    import tkMessageBox as messagebox
    from Tkinter import IntVar, Checkbutton
    import ttk
    import _winreg as winreg
    from collections import deque
    string_types = (str, unicode)
else:
    import tkinter as tk
    from tkinter import messagebox, IntVar, Checkbutton, ttk
    import winreg
    from collections import deque
    string_types = (str,)

CONFIG_FILE = "config.json"
COPY_BUFFER = 1024 * 1024

MSG_PROGRESS = "progress"
MSG_STATUS   = "status"
MSG_INFO     = "info"
MSG_WARN     = "warn"
MSG_ERROR    = "error"
MSG_DONE     = "done"


def makedirs_compat(path):
    if not os.path.exists(path):
        os.makedirs(path)


def thread_compat(target, args=(), daemon=True):
    t = threading.Thread(target=target, args=args)
    if hasattr(t, 'daemon'):
        t.daemon = daemon
    else:
        t.setDaemon(daemon)
    return t


def _get_app_dir():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(sys.executable)
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()


def _find_icon_path():
    app_dir = _get_app_dir()
    for name in ("FerragilBackup.ico", "logoF.ico", "icon.ico"):
        p = os.path.join(app_dir, name)
        if os.path.exists(p):
            return p
    return None


def _load_hicon(size=32):
    u32 = ctypes.windll.user32
    LR_LOADFROMFILE = 0x00000010
    LR_DEFAULTSIZE  = 0x00000040
    LR_SHARED       = 0x00008000
    IMAGE_ICON      = 1
    IDI_APPLICATION = 32512

    ico_path = _find_icon_path()
    if ico_path:
        try:
            h = u32.LoadImageW(
                None,
                ico_path if not PY2 else unicode(ico_path),
                IMAGE_ICON, size, size, LR_LOADFROMFILE)
            if h:
                return h
        except Exception:
            pass

    if getattr(sys, 'frozen', False):
        try:
            hmod = ctypes.windll.kernel32.GetModuleHandleW(None)
            h = u32.LoadIconW(hmod, ctypes.c_wchar_p(1))
            if h:
                return h
        except Exception:
            pass

    try:
        h = u32.LoadImageW(None, ctypes.c_wchar_p(IDI_APPLICATION),
                           IMAGE_ICON, 0, 0, LR_SHARED | LR_DEFAULTSIZE)
        if h:
            return h
    except Exception:
        pass
    return None


def _browse_folder_win(hwnd_owner=0, title=u"Selecionar Pasta"):
    try:
        s32 = ctypes.windll.shell32
        ole = ctypes.windll.ole32

        BIF_RETURNONLYFSDIRS = 0x0001
        BIF_NEWDIALOGSTYLE   = 0x0040
        BIF_EDITBOX          = 0x0010
        BIF_USENEWUI         = BIF_NEWDIALOGSTYLE | BIF_EDITBOX

        BrowseCallbackProc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_void_p, ctypes.c_uint,
            ctypes.c_void_p, ctypes.c_void_p)

        class BROWSEINFO(ctypes.Structure):
            _fields_ = [
                ("hwndOwner",      ctypes.c_void_p),
                ("pidlRoot",       ctypes.c_void_p),
                ("pszDisplayName", ctypes.c_wchar * 260),
                ("lpszTitle",      ctypes.c_wchar_p),
                ("ulFlags",        ctypes.c_uint),
                ("lpfn",           BrowseCallbackProc),
                ("lParam",         ctypes.c_void_p),
                ("iImage",         ctypes.c_int),
            ]

        ole.CoInitialize(None)

        bi = BROWSEINFO()
        bi.hwndOwner = hwnd_owner if hwnd_owner else None
        bi.pidlRoot  = None
        bi.lpszTitle = title
        bi.ulFlags   = BIF_USENEWUI | BIF_RETURNONLYFSDIRS
        bi.lpfn      = BrowseCallbackProc(0)
        bi.lParam    = None

        pidl = s32.SHBrowseForFolderW(ctypes.byref(bi))

        result = u""
        if pidl:
            path_buf = ctypes.create_unicode_buffer(32768)
            if s32.SHGetPathFromIDListW(pidl, path_buf):
                result = path_buf.value
            try:
                ole.CoTaskMemFree(pidl)
            except Exception:
                pass

        try:
            ole.CoUninitialize()
        except Exception:
            pass

        return result

    except Exception as e:
        print("browse error: {0}".format(e))
        return u""


def _pct_bar(pct, width=12):
    filled = int(round(pct / 100.0 * width))
    filled = max(0, min(width, filled))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


class FileCopierApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Ferragil - Backup")

        self._hicon_small = None
        self._hicon_large = None
        self._set_window_icon()

        self.automation_var   = IntVar()
        self.systray_var      = IntVar()
        self.stop_automation  = threading.Event()
        self.directory_pairs  = []
        self.copying          = False
        self.scheduled_times  = []
        self.running          = True
        self.last_backup_date = {}

        self._tray_active = False
        self._tray_hwnd   = None
        self._tray_thread = None

        self._ui_queue = deque()
        self._ui_lock  = threading.Lock()

        self.load_config()

        self.master.option_add('*Font', 'Tahoma 8')

        top_frame = tk.Frame(self.master)
        top_frame.pack(padx=10, pady=5, fill=tk.X)

        control_frame = tk.Frame(top_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="Adicionar Par",
                  command=self.add_pair).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remover Selecionado",
                  command=self.remove_pair).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Editar Selecionado",
                  command=self.edit_pair).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Copiar Todos",
                  command=self.start_copy_all).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Configurar Horarios",
                  command=self.configurar_horarios).pack(side=tk.LEFT, padx=5)
        Checkbutton(button_frame, text="Automacao",
                    variable=self.automation_var,
                    command=self.toggle_automation).pack(side=tk.LEFT, padx=5)
        Checkbutton(button_frame, text="Systray",
                    variable=self.systray_var,
                    command=self.toggle_systray).pack(side=tk.LEFT, padx=2)

        schedule_frame = tk.Frame(control_frame)
        schedule_frame.pack(fill=tk.X, pady=2)
        tk.Label(schedule_frame, text="Horarios Programados:",
                 font=('Tahoma', 8, 'bold')).pack(side=tk.LEFT, padx=5)
        self.schedule_label = tk.Label(schedule_frame, text="",
                                       font=('Tahoma', 8), fg="blue")
        self.schedule_label.pack(side=tk.LEFT, padx=5)
        self.update_schedule_display()

        status_frame = tk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=2)
        self.status_label = tk.Label(status_frame, text="Pronto",
                                     font=('Tahoma', 7), fg="blue")
        self.status_label.pack(side=tk.LEFT, padx=5)

        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("Source", "Destination", "Files"),
            show="headings",
            height=15
        )
        self.tree.heading("Source",      text="Origem")
        self.tree.heading("Destination", text="Destino")
        self.tree.heading("Files",       text="Arquivos")
        self.tree.column("Source",      width=240, anchor="w")
        self.tree.column("Destination", width=240, anchor="w")
        self.tree.column("Files",       width=80,  anchor="center")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for pair in self.config_data.get("directory_pairs", []):
            item = self.tree.insert("", tk.END,
                values=(pair["source"], pair["destination"], "0"))
            self.directory_pairs.append({
                "source":      pair["source"],
                "destination": pair["destination"],
                "item":        item
            })

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Unmap>", self._on_unmap)

        if self.config_data.get("automation", False):
            self.automation_var.set(1)
            self.start_automation()

        if self.config_data.get("systray", False):
            self.systray_var.set(1)
            self.master.after(300, self._hide_to_tray)

        self._pump_ui_queue()

    def _set_window_icon(self):
        u32        = ctypes.windll.user32
        WM_SETICON = 0x0080

        self._hicon_small = _load_hicon(16)
        self._hicon_large = _load_hicon(32)

        ico_path = _find_icon_path()
        if ico_path:
            try:
                self.master.iconbitmap(ico_path)
            except Exception:
                pass

        def _apply_taskbar():
            try:
                hwnd = u32.GetParent(self.master.winfo_id())
                if hwnd == 0:
                    self.master.after(200, _apply_taskbar)
                    return
                if self._hicon_small:
                    u32.SendMessageW(hwnd, WM_SETICON, 0, self._hicon_small)
                if self._hicon_large:
                    u32.SendMessageW(hwnd, WM_SETICON, 1, self._hicon_large)
            except Exception:
                pass

        self.master.after(300, _apply_taskbar)

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                u"Ferragil.Backup.Application")
        except Exception:
            pass

    def _apply_icon_to_dialog(self, window):
        u32        = ctypes.windll.user32
        WM_SETICON = 0x0080
        ico_path   = _find_icon_path()
        if ico_path:
            try:
                window.iconbitmap(ico_path)
            except Exception:
                pass

        def _apply():
            try:
                hwnd = u32.GetParent(window.winfo_id())
                if hwnd == 0:
                    window.after(100, _apply)
                    return
                if self._hicon_small:
                    u32.SendMessageW(hwnd, WM_SETICON, 0, self._hicon_small)
                if self._hicon_large:
                    u32.SendMessageW(hwnd, WM_SETICON, 1, self._hicon_large)
            except Exception:
                pass

        window.after(100, _apply)

    def _push(self, msg_type, payload):
        with self._ui_lock:
            self._ui_queue.append((msg_type, payload))

    def _pump_ui_queue(self):
        try:
            with self._ui_lock:
                batch = []
                for _ in range(60):
                    if not self._ui_queue:
                        break
                    batch.append(self._ui_queue.popleft())

            for msg_type, payload in batch:
                if msg_type == MSG_PROGRESS:
                    item, pct, time_str, copied, total = payload
                    
                    if total > 0:
                        self.tree.set(item, "Files", "{0}/{1}".format(copied, total))
                    elif copied > 0:
                        self.tree.set(item, "Files", str(copied))

                elif msg_type == MSG_STATUS:
                    text, is_error = payload
                    self.status_label.config(
                        text=text, fg="red" if is_error else "blue")

                elif msg_type == MSG_INFO:
                    title, text = payload
                    messagebox.showinfo(title, text)

                elif msg_type == MSG_WARN:
                    title, text = payload
                    messagebox.showwarning(title, text)

                elif msg_type == MSG_ERROR:
                    title, text = payload
                    messagebox.showerror(title, text)

        except Exception:
            pass

        if self.running:
            self.master.after(80, self._pump_ui_queue)

    def _status(self, text, is_error=False):
        self._push(MSG_STATUS, (text, is_error))

    def _progress(self, item, pct, time_str, copied=0, total=0):
        self._push(MSG_PROGRESS, (item, pct, time_str, copied, total))

    def _msginfo(self, title, text):
        self._push(MSG_INFO, (title, text))

    def _msgwarn(self, title, text):
        self._push(MSG_WARN, (title, text))

    def _msgerror(self, title, text):
        self._push(MSG_ERROR, (title, text))

    def update_schedule_display(self):
        if self.scheduled_times:
            self.schedule_label.config(text=" | ".join(self.scheduled_times))
        else:
            self.schedule_label.config(text="Nenhum horario programado")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config_data = json.load(f)
            except Exception:
                self.config_data = {}
        else:
            self.config_data = {}
        self.scheduled_times = self.config_data.get("scheduled_times", [])

    def save_config(self):
        self.config_data["directory_pairs"] = [
            {"source": p["source"], "destination": p["destination"]}
            for p in self.directory_pairs
        ]
        self.config_data["scheduled_times"] = self.scheduled_times
        self.config_data["automation"]       = bool(self.automation_var.get())
        self.config_data["systray"]          = bool(self.systray_var.get())
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            print("Erro ao salvar config: {0}".format(e))

    def configurar_horarios(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Horarios de Automacao")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.geometry("350x300")
        self._apply_icon_to_dialog(dialog)

        current_frame = tk.LabelFrame(dialog, text="Horarios Atuais",
                                      padx=10, pady=10)
        current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.current_times_listbox = tk.Listbox(current_frame, height=6)
        self.current_times_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        current_buttons_frame = tk.Frame(current_frame)
        current_buttons_frame.pack(fill=tk.X, pady=5)
        tk.Button(current_buttons_frame, text="Remover Selecionado",
                  command=self.remove_schedule_time,
                  bg="#ffcccc").pack(side=tk.LEFT, padx=5)

        add_frame = tk.LabelFrame(dialog, text="Adicionar Novo Horario",
                                  padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(add_frame, text="Horario (HH:MM):").pack(side=tk.LEFT, padx=5)
        self.time_entry = tk.Entry(add_frame, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(add_frame, text="Adicionar",
                  command=self.add_schedule_time,
                  bg="#ccffcc").pack(side=tk.LEFT, padx=5)

        self.update_schedule_listbox()

        tk.Label(dialog, text="Dica: Use formato 24h (ex: 09:30, 17:00)",
                 font=('Tahoma', 7), fg="gray").pack(padx=10, pady=2)
        tk.Button(dialog, text="Fechar",
                  command=dialog.destroy).pack(pady=8)

    def update_schedule_listbox(self):
        self.current_times_listbox.delete(0, tk.END)
        for t in self.scheduled_times:
            self.current_times_listbox.insert(tk.END, t)

    def add_schedule_time(self):
        t = self.time_entry.get().strip()
        try:
            time.strptime(t, '%H:%M')
            if t not in self.scheduled_times:
                self.scheduled_times.append(t)
                self.scheduled_times.sort()
                self.update_schedule_listbox()
                self.update_schedule_display()
                self.save_config()
                self.time_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Horario Duplicado",
                                       "Este horario ja esta programado.")
        except ValueError:
            messagebox.showwarning("Formato Invalido",
                                   "Use o formato HH:MM (ex: 17:30).")

    def remove_schedule_time(self):
        selection = self.current_times_listbox.curselection()
        if selection:
            t = self.current_times_listbox.get(selection[0])
            self.scheduled_times.remove(t)
            self.update_schedule_listbox()
            self.update_schedule_display()
            self.save_config()
        else:
            messagebox.showwarning("Nenhum Selecionado",
                                   "Por favor, selecione um horario para remover.")

    def _make_pair_dialog(self, title, source_val="", dest_val="",
                          on_confirm=None):
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.resizable(False, False)
        self._apply_icon_to_dialog(dialog)

        tk.Label(dialog, text="Origem:").grid(
            row=0, column=0, padx=8, pady=8, sticky="e")
        source_entry = tk.Entry(dialog, width=52)
        source_entry.insert(0, source_val)
        source_entry.grid(row=0, column=1, padx=5, pady=8)

        def pick_src():
            hwnd = 0
            try:
                hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
            except Exception:
                pass
            r = _browse_folder_win(hwnd_owner=hwnd,
                                   title=u"Selecionar Pasta de Origem")
            if r:
                source_entry.delete(0, tk.END)
                source_entry.insert(0, r)

        tk.Button(dialog, text="Selecionar...",
                  command=pick_src).grid(row=0, column=2, padx=5, pady=8)

        tk.Label(dialog, text="Destino:").grid(
            row=1, column=0, padx=8, pady=8, sticky="e")
        dest_entry = tk.Entry(dialog, width=52)
        dest_entry.insert(0, dest_val)
        dest_entry.grid(row=1, column=1, padx=5, pady=8)

        def pick_dst():
            hwnd = 0
            try:
                hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
            except Exception:
                pass
            r = _browse_folder_win(hwnd_owner=hwnd,
                                   title=u"Selecionar Pasta de Destino")
            if r:
                dest_entry.delete(0, tk.END)
                dest_entry.insert(0, r)

        tk.Button(dialog, text="Selecionar...",
                  command=pick_dst).grid(row=1, column=2, padx=5, pady=8)

        def confirm():
            src = source_entry.get().strip()
            dst = dest_entry.get().strip()
            if src and dst:
                dialog.destroy()
                if on_confirm:
                    on_confirm(src, dst)
            else:
                messagebox.showwarning("Entrada Invalida",
                                       "Por favor, selecione ambos os diretorios.")

        tk.Button(dialog, text="Confirmar", width=12,
                  command=confirm).grid(row=2, column=0, columnspan=3, pady=10)

    def add_pair(self):
        if len(self.directory_pairs) >= 200:
            messagebox.showwarning("Limite Atingido",
                "Voce atingiu o limite de 200 pares de diretorios.")
            return

        def on_confirm(src, dst):
            item = self.tree.insert("", tk.END,
                values=(src, dst, "0"))
            self.directory_pairs.append({
                "source": src, "destination": dst, "item": item})
            self.save_config()

        self._make_pair_dialog("Adicionar Par de Diretorios",
                               on_confirm=on_confirm)

    def remove_pair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Nenhum Selecionado",
                "Por favor, selecione um par para remover.")
            return
        for item in selected:
            index = self.tree.index(item)
            self.directory_pairs.pop(index)
            self.tree.delete(item)
        self.save_config()

    def edit_pair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Nenhum Selecionado",
                "Por favor, selecione um par para editar.")
            return
        if len(selected) > 1:
            messagebox.showwarning("Selecao Invalida",
                "Por favor, selecione apenas um par para editar.")
            return

        item  = selected[0]
        index = self.tree.index(item)
        pair  = self.directory_pairs[index]

        def on_confirm(src, dst):
            self.directory_pairs[index] = {
                "source": src, "destination": dst, "item": item}
            self.tree.item(item,
                values=(src, dst, "0"))
            self.save_config()

        self._make_pair_dialog("Editar Par de Diretorios",
                               source_val=pair["source"],
                               dest_val=pair["destination"],
                               on_confirm=on_confirm)

    if hasattr(os, 'scandir'):
        @staticmethod
        def _iter_dir(path):
            try:
                for e in os.scandir(path):
                    try:
                        st = e.stat(follow_symlinks=False)
                    except OSError:
                        st = None
                    yield (e.name, e.path,
                           e.is_dir(follow_symlinks=False), st)
            except OSError:
                return
    else:
        @staticmethod
        def _iter_dir(path):
            try:
                nomes = os.listdir(path)
            except OSError:
                return
            for nome in nomes:
                full = os.path.join(path, nome)
                try:
                    st = os.stat(full)
                except OSError:
                    continue
                yield (nome, full, _stat_mod.S_ISDIR(st.st_mode), st)

    @staticmethod
    def _build_dest_index(dst_dir):
        idx   = {}
        pilha = [dst_dir]
        while pilha:
            cur = pilha.pop()
            for nome, full, is_dir, st in FileCopierApp._iter_dir(cur):
                if is_dir:
                    pilha.append(full)
                elif st is not None:
                    rel      = os.path.relpath(full, dst_dir)
                    idx[rel] = st.st_mtime
        return idx

    @staticmethod
    def _scan_pendentes(origem, destino):
        dst_idx   = FileCopierApp._build_dest_index(destino)
        pendentes = []
        pilha     = [(origem, destino)]
        while pilha:
            src_dir, dst_dir = pilha.pop()
            for nome, src_path, is_dir, src_st in FileCopierApp._iter_dir(src_dir):
                if is_dir:
                    pilha.append((src_path, os.path.join(dst_dir, nome)))
                    continue
                if src_st is None:
                    continue
                dst_path  = os.path.join(dst_dir, nome)
                rel       = os.path.relpath(dst_path, destino)
                dst_mtime = dst_idx.get(rel)
                if dst_mtime is None or src_st.st_mtime - dst_mtime > 1.0:
                    pendentes.append((src_path, dst_path,
                                      max(src_st.st_size, 0)))
        return pendentes

    @staticmethod
    def _copy_file_fast(src, dst):
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                while True:
                    buf = fsrc.read(COPY_BUFFER)
                    if not buf:
                        break
                    fdst.write(buf)
        try:
            shutil.copystat(src, dst)
        except Exception:
            pass

    def _copiar_par(self, src, dst, item):
        if not os.path.isdir(src):
            self._status(
                "Erro: Origem nao encontrada - {0}".format(src), True)
            return 0

        self._status(
            "Verificando {0}...".format(os.path.basename(src) or src))
        self._progress(item, 0, "", 0, 0)

        pendentes   = self._scan_pendentes(src, dst)
        total_arqs  = len(pendentes)
        total_bytes = sum(t[2] for t in pendentes)

        if total_arqs == 0:
            return 0

        makedirs_compat(dst)

        copiados       = 0
        bytes_copiados = 0
        t0             = time.time()
        t_ui           = t0 - 0.5

        for src_path, dst_path, tamanho in pendentes:
            if not self.copying:
                break
            try:
                makedirs_compat(os.path.dirname(dst_path))
                self._copy_file_fast(src_path, dst_path)
                copiados       += 1
                bytes_copiados += tamanho
            except Exception as ex:
                print("Erro ao copiar {0}: {1}".format(src_path, ex))

            agora = time.time()
            if agora - t_ui >= 0.4:
                t_ui    = agora
                self._progress(item, 0, "", copiados, total_arqs)
                self._status(
                    "Copiando {0}: {1}/{2} arquivo(s)".format(
                        os.path.basename(src) or src,
                        copiados,
                        total_arqs))

        return copiados

    def start_copy_all(self):
        if self.copying:
            messagebox.showwarning("Em Progresso",
                                   "A copia ja esta em andamento.")
            return
        thread_compat(target=self.copiar_todos_optimized, daemon=True).start()

    def copiar_todos_optimized(self, show_message=True):
        if self.copying:
            return
        self.copying   = True
        total_start    = time.time()
        total_copiados = 0
        try:
            for pair in self.directory_pairs:
                if not self.copying:
                    break
                src = pair.get("source", "")
                dst = pair.get("destination", "")
                if not src or not dst:
                    continue
                copiados = self._copiar_par(src, dst, pair["item"])
                total_copiados += copiados
                self._progress(pair["item"], 0, "",
                               copiados, copiados)

            elapsed = time.time() - total_start
            now_str = datetime.datetime.now().strftime("%H:%M")
            self.last_backup_date[now_str] = datetime.datetime.now().date()

            self._status(
                "Backup concluido! {0} arquivo(s) em {1:.1f}s".format(
                    total_copiados, elapsed))

            if show_message:
                if total_copiados == 0:
                    self._msginfo("Backup",
                        "Nenhum arquivo novo ou modificado encontrado.")
                else:
                    self._msginfo("Concluido",
                        "Backup finalizado!\nArquivos copiados: {0}"
                        "\nTempo: {1:.1f}s".format(total_copiados, elapsed))

        except Exception as e:
            self._status(
                "Erro durante backup: {0}".format(str(e)[:60]), True)
            if show_message:
                self._msgerror("Erro",
                               "Erro durante backup: {0}".format(e))
        finally:
            self.copying = False

    _WM_TRAY = 0x8001
    _TRAY_ID = 1

    def toggle_systray(self):
        self.save_config()

    def _hide_to_tray(self):
        if self._tray_active:
            return
        self._tray_active = True
        self.master.withdraw()
        if self._tray_thread is None or not self._tray_thread.is_alive():
            self._tray_thread = thread_compat(
                target=self._tray_loop, daemon=True)
            self._tray_thread.start()

    def _show_from_tray(self):
        self._stop_tray_loop()
        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()

    def _tray_loop(self):
        u32 = ctypes.windll.user32
        s32 = ctypes.windll.shell32
        k32 = ctypes.windll.kernel32

        WNDPROCTYPE = ctypes.WINFUNCTYPE(
            ctypes.c_long,
            ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)

        WM_DESTROY       = 0x0002
        WM_TRAY          = self._WM_TRAY
        WM_LBUTTONDBLCLK = 0x0203
        WM_RBUTTONUP     = 0x0205
        NIM_ADD          = 0x00000000
        NIM_DELETE       = 0x00000002
        NIF_MESSAGE      = 0x00000001
        NIF_ICON         = 0x00000002
        NIF_TIP          = 0x00000004
        TPM_RETURNCMD    = 0x0100
        TPM_RIGHTBUTTON  = 0x0002
        MF_STRING        = 0x0000
        IDM_RESTORE      = 1001
        IDM_QUIT         = 1002
        LR_LOADFROMFILE  = 0x00000010
        LR_DEFAULTSIZE   = 0x00000040
        LR_SHARED        = 0x00008000
        IMAGE_ICON       = 1
        IDI_APPLICATION  = 32512

        class WNDCLASSEX(ctypes.Structure):
            _fields_ = [
                ("cbSize",        ctypes.c_uint),
                ("style",         ctypes.c_uint),
                ("lpfnWndProc",   WNDPROCTYPE),
                ("cbClsExtra",    ctypes.c_int),
                ("cbWndExtra",    ctypes.c_int),
                ("hInstance",     ctypes.c_void_p),
                ("hIcon",         ctypes.c_void_p),
                ("hCursor",       ctypes.c_void_p),
                ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName",  ctypes.c_wchar_p),
                ("lpszClassName", ctypes.c_wchar_p),
                ("hIconSm",       ctypes.c_void_p),
            ]

        class NOTIFYICONDATA(ctypes.Structure):
            _fields_ = [
                ("cbSize",           ctypes.c_ulong),
                ("hWnd",             ctypes.c_void_p),
                ("uID",              ctypes.c_uint),
                ("uFlags",           ctypes.c_uint),
                ("uCallbackMessage", ctypes.c_uint),
                ("hIcon",            ctypes.c_void_p),
                ("szTip",            ctypes.c_wchar * 128),
            ]

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        class MSG(ctypes.Structure):
            _fields_ = [
                ("hwnd",    ctypes.c_void_p),
                ("message", ctypes.c_uint),
                ("wParam",  ctypes.c_void_p),
                ("lParam",  ctypes.c_void_p),
                ("time",    ctypes.c_ulong),
                ("pt",      POINT),
            ]

        hwnd_box  = [None]
        nid_box   = [None]
        cls_name  = u"FerragilTray_{0}".format(id(self))
        hinstance = k32.GetModuleHandleW(None)

        def wnd_proc(hwnd, msg, wparam, lparam):
            if msg == WM_TRAY:
                evt = lparam & 0xFFFF
                if evt == WM_LBUTTONDBLCLK:
                    self.master.after(0, self._show_from_tray)
                elif evt == WM_RBUTTONUP:
                    pt = POINT()
                    u32.GetCursorPos(ctypes.byref(pt))
                    hmenu = u32.CreatePopupMenu()
                    u32.AppendMenuW(hmenu, MF_STRING,
                                    IDM_RESTORE, u"Restaurar")
                    u32.AppendMenuW(hmenu, MF_STRING,
                                    IDM_QUIT,    u"Sair")
                    u32.SetForegroundWindow(hwnd)
                    cmd = u32.TrackPopupMenu(
                        hmenu, TPM_RETURNCMD | TPM_RIGHTBUTTON,
                        pt.x, pt.y, 0, hwnd, None)
                    u32.DestroyMenu(hmenu)
                    if cmd == IDM_RESTORE:
                        self.master.after(0, self._show_from_tray)
                    elif cmd == IDM_QUIT:
                        self.master.after(0, self._quit_app)
                return 0
            if msg == WM_DESTROY:
                return 0
            return u32.DefWindowProcW(hwnd, msg, wparam, lparam)

        wnd_proc_cb = WNDPROCTYPE(wnd_proc)

        try:
            wc = WNDCLASSEX()
            wc.cbSize        = ctypes.sizeof(WNDCLASSEX)
            wc.lpfnWndProc   = wnd_proc_cb
            wc.hInstance     = hinstance
            wc.lpszClassName = cls_name
            u32.RegisterClassExW(ctypes.byref(wc))

            hwnd = u32.CreateWindowExW(
                0, cls_name, u"Ferragil Tray",
                0, 0, 0, 0, 0, 0, 0, hinstance, None)
            hwnd_box[0]     = hwnd
            self._tray_hwnd = hwnd

            hicon = self._hicon_small

            if not hicon:
                ico_path = _find_icon_path()
                if ico_path:
                    hicon = u32.LoadImageW(
                        None,
                        ico_path if not PY2 else unicode(ico_path),
                        IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

            if not hicon and getattr(sys, 'frozen', False):
                hmod  = k32.GetModuleHandleW(None)
                hicon = u32.LoadIconW(hmod, ctypes.c_wchar_p(1))

            if not hicon:
                hicon = u32.LoadImageW(
                    None, ctypes.c_wchar_p(IDI_APPLICATION),
                    IMAGE_ICON, 0, 0, LR_SHARED | LR_DEFAULTSIZE)

            nid = NOTIFYICONDATA()
            nid.cbSize           = ctypes.sizeof(NOTIFYICONDATA)
            nid.hWnd             = hwnd
            nid.uID              = self._TRAY_ID
            nid.uFlags           = NIF_MESSAGE | NIF_ICON | NIF_TIP
            nid.uCallbackMessage = WM_TRAY
            nid.hIcon            = hicon if hicon else 0
            nid.szTip            = u"Ferragil Backup"
            nid_box[0]           = nid
            s32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))

            msg_struct = MSG()
            while self.running and self._tray_active:
                ret = u32.GetMessageW(
                    ctypes.byref(msg_struct), hwnd, 0, 0)
                if ret == 0 or ret == -1:
                    break
                u32.TranslateMessage(ctypes.byref(msg_struct))
                u32.DispatchMessageW(ctypes.byref(msg_struct))

        except Exception as ex:
            print("Erro tray_loop: {0}".format(ex))
        finally:
            try:
                if nid_box[0] is not None:
                    s32.Shell_NotifyIconW(NIM_DELETE,
                                         ctypes.byref(nid_box[0]))
            except Exception:
                pass
            try:
                u32.DestroyWindow(hwnd_box[0])
                u32.UnregisterClassW(cls_name, hinstance)
            except Exception:
                pass
            self._tray_active = False

    def _stop_tray_loop(self):
        self._tray_active = False
        try:
            if self._tray_hwnd:
                ctypes.windll.user32.PostMessageW(
                    self._tray_hwnd, 0x0012, 0, 0)
        except Exception:
            pass

    def toggle_automation(self):
        if self.automation_var.get() == 1:
            self.config_data["automation"] = True
            self.start_automation()
            self.set_autostart(True)
        else:
            self.config_data["automation"] = False
            self.stop_automation.set()
            self.set_autostart(False)
        self.save_config()

    def set_autostart(self, enable):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "FerragilBackup"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                                 winreg.KEY_SET_VALUE)
            if enable:
                exe_path = os.path.abspath(
                    sys.executable if getattr(sys, 'frozen', False)
                    else __file__)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ,
                                  '"' + exe_path + '"')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except (WindowsError, OSError):
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print("Erro ao configurar autostart: {0}".format(e))

    def start_automation(self):
        self.stop_automation.clear()
        thread_compat(target=self._automation_loop, daemon=True).start()
        thread_compat(target=self._backup_on_startup, daemon=True).start()

    def _automation_loop(self):
        last_triggered = {}
        while not self.stop_automation.is_set() and self.running:
            now              = datetime.datetime.now()
            current_time_str = "{0:02d}:{1:02d}".format(now.hour, now.minute)
            current_date     = now.date()

            if current_time_str in self.scheduled_times:
                if last_triggered.get(current_time_str) != current_date:
                    last_triggered[current_time_str]        = current_date
                    self.last_backup_date[current_time_str] = current_date
                    if not self.copying:
                        thread_compat(target=self.copiar_todos_optimized,
                                      args=(False,), daemon=True).start()

            next_minute   = (now + datetime.timedelta(minutes=1)).replace(
                second=0, microsecond=0)
            sleep_seconds = max(5, (next_minute - now).total_seconds())
            self.stop_automation.wait(timeout=sleep_seconds)

    def _backup_on_startup(self):
        time.sleep(3)
        if self.running and not self.copying:
            self.copiar_todos_optimized(show_message=False)

    def _on_unmap(self, event):
        if event.widget is not self.master:
            return
        if self.systray_var.get() == 1 and not self._tray_active:
            self.master.after(50, self._hide_to_tray)

    def on_close(self):
        if self.systray_var.get() == 1:
            self._hide_to_tray()
            return
        self._quit_app()

    def _quit_app(self):
        self.running      = False
        self._tray_active = False
        self.stop_automation.set()
        self._stop_tray_loop()
        self.save_config()
        try:
            self.master.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app  = FileCopierApp(root)
    root.mainloop()
