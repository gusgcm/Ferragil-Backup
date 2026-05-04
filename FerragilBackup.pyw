# FerragilBackup.pyw
# Toda atualizacao de UI e feita pela fila processada no mainloop (after())

import os
import sys
import shutil
import threading
import time
import datetime
import json
import ctypes

# ---------------------------------------------------------------------------
# Compatibilidade Python 2.7 / 3.x
# ---------------------------------------------------------------------------
PY2 = sys.version_info[0] == 2

if PY2:
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    from Tkinter import IntVar, Checkbutton
    import ttk
    import _winreg as winreg
    from collections import deque
    string_types = (str, unicode)
else:
    import tkinter as tk
    from tkinter import filedialog, messagebox, IntVar, Checkbutton, ttk
    import winreg
    from collections import deque
    string_types = (str,)


# ---------------------------------------------------------------------------
# Recursos embutidos (base64) -- sem dependencia de arquivos externos
# GIF: compativel com Tk 8.4 (XP);  ICO: carregado via WinAPI
# ---------------------------------------------------------------------------
import base64 as _b64

_LOGO_GIF_B64 = "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"
_LOGO_ICO_B64 = "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"

def _gif_data():
    return _b64.b64decode(_LOGO_GIF_B64)

def _ico_data():
    return _b64.b64decode(_LOGO_ICO_B64)

CONFIG_FILE = "config.json"


def makedirs_compat(path):
    """os.makedirs sem exist_ok (nao existe no Python 2.7 / 3.3-)"""
    if not os.path.exists(path):
        os.makedirs(path)


def thread_compat(target, args=(), daemon=True):
    """Cria thread compativel com Python 2 e 3"""
    t = threading.Thread(target=target, args=args)
    if hasattr(t, 'daemon'):
        t.daemon = daemon
    else:
        t.setDaemon(daemon)
    return t


# ---------------------------------------------------------------------------
# Constantes para tipo de mensagem na fila
# ---------------------------------------------------------------------------
MSG_PROGRESS = "progress"  # (item, percentage, time_str, files_copied, total_files)
MSG_STATUS   = "status"    # (text, is_error)
MSG_INFO     = "info"      # (title, text)
MSG_WARN     = "warn"      # (title, text)
MSG_ERROR    = "error"     # (title, text)
MSG_DONE     = "done"      # (total_copied, elapsed)


class FileCopierApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Ferragil - Backup")

        # Configurar icone
        self.set_window_icon()

        self.automation_var = IntVar()
        self.stop_automation = threading.Event()
        self.directory_pairs = []
        self.copying = False
        self.progress_bars = {}
        self.scheduled_times = []
        self.running = True
        self.last_backup_date = {}

        # Fila unica thread-safe para TODAS as atualizacoes de UI
        self._ui_queue = deque()
        self._ui_lock  = threading.Lock()

        self.load_config()

        # Fonte compativel com XP e windows mais novos
        self.master.option_add('*Font', 'Tahoma 8')

        # ------------------------------------------------------------------
        # Frame superior
        # ------------------------------------------------------------------
        top_frame = tk.Frame(self.master)
        top_frame.pack(padx=10, pady=5, fill=tk.X)

        control_frame = tk.Frame(top_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Linha unica de botoes (incluindo Automacao e Configurar Horarios)
        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="Adicionar Par",       command=self.add_pair).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remover Selecionado", command=self.remove_pair).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Editar Selecionado",  command=self.edit_pair).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Copiar Todos",        command=self.start_copy_all).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Configurar Horarios", command=self.configurar_horarios).pack(side=tk.LEFT, padx=5)
        Checkbutton(button_frame, text="Automacao",         variable=self.automation_var, command=self.toggle_automation).pack(side=tk.LEFT, padx=5)

        # Linha de horarios programados
        schedule_frame = tk.Frame(control_frame)
        schedule_frame.pack(fill=tk.X, pady=2)
        tk.Label(schedule_frame, text="Horarios Programados:", font=('Tahoma', 8, 'bold')).pack(side=tk.LEFT, padx=5)
        self.schedule_label = tk.Label(schedule_frame, text="", font=('Tahoma', 8), fg="blue")
        self.schedule_label.pack(side=tk.LEFT, padx=5)
        self.update_schedule_display()

        # Linha de status
        status_frame = tk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=2)
        self.status_label = tk.Label(status_frame, text="Pronto", font=('Tahoma', 7), fg="green")
        self.status_label.pack(side=tk.LEFT, padx=5)

        # Logo (sem texto fallback "Ferragil Backup")
        image_frame = tk.Frame(top_frame)
        image_frame.pack(side=tk.RIGHT, padx=10)
        self.logo_photo = None
        self._try_load_logo(image_frame)

        # ------------------------------------------------------------------
        # Treeview principal
        # ------------------------------------------------------------------
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("Source", "Destination", "Progress", "Percentage", "Time", "Files"),
            show="headings",
            height=15
        )
        self.tree.heading("Source",      text="Origem")
        self.tree.heading("Destination", text="Destino")
        self.tree.heading("Progress",    text="Progresso")
        self.tree.heading("Percentage",  text="%")
        self.tree.heading("Time",        text="Tempo Restante")
        self.tree.heading("Files",       text="Arquivos")
        self.tree.column("Source",      width=200)
        self.tree.column("Destination", width=200)
        self.tree.column("Progress",    width=150)
        self.tree.column("Percentage",  width=50)
        self.tree.column("Time",        width=100)
        self.tree.column("Files",       width=80)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for pair in self.config_data.get("directory_pairs", []):
            item = self.tree.insert("", tk.END, values=(pair["source"], pair["destination"], "", "0%", "--:--", "0"))
            self.directory_pairs.append({"source": pair["source"], "destination": pair["destination"], "item": item})
            self.progress_bars[item] = ttk.Progressbar(self.tree, length=140, mode="determinate")
            self.tree.set(item, "Progress",    "")
            self.tree.set(item, "Percentage",  "0%")
            self.tree.set(item, "Time",        "--:--")
            self.tree.set(item, "Files",       "0")

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        if self.config_data.get("automation", False):
            self.automation_var.set(1)
            self.start_automation()

        # Inicia o pump da fila de UI (roda no mainloop, thread-safe)
        self._pump_ui_queue()

    # ------------------------------------------------------------------
    # Logo
    # ------------------------------------------------------------------
    def _try_load_logo(self, frame):
        try:
            gif_bytes = _gif_data()
            self.logo_photo = tk.PhotoImage(data=_LOGO_GIF_B64)
            tk.Label(frame, image=self.logo_photo).pack()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Icone da janela e barra de tarefas (usando ICO embutido em base64)
    # ------------------------------------------------------------------
    def set_window_icon(self):
        import tempfile

        self._ico_tmp = None  # caminho do temp; apagado em on_close()

        def _write_ico_tmp():
            """Grava bytes do ICO em arquivo temporario e retorna o caminho."""
            try:
                ico_bytes = _ico_data()
                fd, path = tempfile.mkstemp(suffix=".ico")
                os.write(fd, ico_bytes)
                os.close(fd)
                return path
            except Exception:
                return None

        ico_path = _write_ico_tmp()
        self._ico_tmp = ico_path

        # --- iconbitmap: barra de titulo ---
        if ico_path:
            try:
                self.master.iconbitmap(ico_path)
            except Exception:
                pass

        # --- WinAPI LoadImage/SendMessage: barra de tarefas ---
        def _set_taskbar_icon():
            try:
                if not ico_path or not os.path.exists(ico_path):
                    return
                ico_abs = os.path.abspath(ico_path)
                HWND = ctypes.windll.user32.GetParent(self.master.winfo_id())
                if HWND == 0:
                    self.master.after(300, _set_taskbar_icon)
                    return
                flags = 0x00000010 | 0x00000040  # LR_LOADFROMFILE | LR_DEFAULTSIZE
                hIcon = ctypes.windll.user32.LoadImageW(
                    None, ico_abs, 1, 0, 0, flags
                )
                if hIcon:
                    WM_SETICON = 0x0080
                    ctypes.windll.user32.SendMessageW(HWND, WM_SETICON, 0, hIcon)  # ICON_SMALL
                    ctypes.windll.user32.SendMessageW(HWND, WM_SETICON, 1, hIcon)  # ICON_BIG
            except Exception:
                pass

        self.master.after(400, _set_taskbar_icon)
        
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                u"Ferragil.Backup.Application"
            )
        except Exception:
            pass


    # ------------------------------------------------------------------
    # Fila de atualizacao de UI  -- UNICO ponto de contato com Tkinter
    # vindo de threads secundarias.  Roda 100% no mainloop (after).
    # ------------------------------------------------------------------
    def _push(self, msg_type, payload):
        """Threads secundarias chamam isso para enfileirar atualizacoes."""
        with self._ui_lock:
            self._ui_queue.append((msg_type, payload))

    def _pump_ui_queue(self):
        """Processado pelo mainloop a cada 100 ms -- nunca bloqueia."""
        try:
            limit = 50  # max mensagens por ciclo para nao travar a UI
            with self._ui_lock:
                batch = []
                for _ in range(limit):
                    if not self._ui_queue:
                        break
                    batch.append(self._ui_queue.popleft())

            for msg_type, payload in batch:
                if msg_type == MSG_PROGRESS:
                    item, pct, time_str, copied, total = payload
                    if item in self.progress_bars:
                        self.progress_bars[item]["value"] = pct
                        self.tree.set(item, "Percentage", "{0:.1f}%".format(pct))
                        self.tree.set(item, "Time",       time_str)
                        if total > 0:
                            self.tree.set(item, "Files", "{0}/{1}".format(copied, total))
                        elif copied > 0:
                            self.tree.set(item, "Files", "{0}".format(copied))

                elif msg_type == MSG_STATUS:
                    text, is_error = payload
                    color = "red" if is_error else "green"
                    self.status_label.config(text=text, fg=color)

                elif msg_type == MSG_INFO:
                    title, text = payload
                    messagebox.showinfo(title, text)

                elif msg_type == MSG_WARN:
                    title, text = payload
                    messagebox.showwarning(title, text)

                elif msg_type == MSG_ERROR:
                    title, text = payload
                    messagebox.showerror(title, text)

                elif msg_type == MSG_DONE:
                    total_copied, elapsed = payload
                    for pair in self.directory_pairs:
                        item = pair["item"]
                        if item in self.progress_bars:
                            self.progress_bars[item]["value"] = 0
                            self.tree.set(item, "Percentage", "0%")
                            self.tree.set(item, "Time",       "--:--")
        except Exception:
            pass

        if self.running:
            self.master.after(100, self._pump_ui_queue)

    # Helpers para threads secundarias -----------------------------------
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

    # ------------------------------------------------------------------
    # Exibicao de horarios
    # ------------------------------------------------------------------
    def update_schedule_display(self):
        if self.scheduled_times:
            schedule_text = " | ".join(self.scheduled_times)
        else:
            schedule_text = "Nenhum horario programado"
        self.schedule_label.config(text=schedule_text)

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------
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
        self.config_data["automation"] = bool(self.automation_var.get())
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            print("Erro ao salvar config: {0}".format(e))

    # ------------------------------------------------------------------
    # Horarios
    # ------------------------------------------------------------------
    def configurar_horarios(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Horarios de Automacao")
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.geometry("350x300")
        self.apply_icon_to_window(dialog)

        current_frame = tk.LabelFrame(dialog, text="Horarios Atuais", padx=10, pady=10)
        current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.current_times_listbox = tk.Listbox(current_frame, height=6)
        self.current_times_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        current_buttons_frame = tk.Frame(current_frame)
        current_buttons_frame.pack(fill=tk.X, pady=5)
        tk.Button(current_buttons_frame, text="Remover Selecionado",
                  command=self.remove_schedule_time, bg="#ffcccc").pack(side=tk.LEFT, padx=5)

        add_frame = tk.LabelFrame(dialog, text="Adicionar Novo Horario", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(add_frame, text="Horario (HH:MM):").pack(side=tk.LEFT, padx=5)
        self.time_entry = tk.Entry(add_frame, width=10)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(add_frame, text="Adicionar",
                  command=self.add_schedule_time, bg="#ccffcc").pack(side=tk.LEFT, padx=5)

        self.update_schedule_listbox()

        help_frame = tk.Frame(dialog)
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(help_frame, text="Dica: Use formato 24h (ex: 09:30, 17:00)",
                 font=('Tahoma', 7), fg="gray").pack()

        tk.Button(dialog, text="Fechar", command=dialog.destroy).pack(pady=10)

    def apply_icon_to_window(self, window):
        """Aplica o icone embutido a janelas filhas (dialogs)."""
        if self._ico_tmp and os.path.exists(self._ico_tmp):
            try:
                window.iconbitmap(self._ico_tmp)
            except Exception:
                pass

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
                messagebox.showwarning("Horario Duplicado", "Este horario ja esta programado.")
        except ValueError:
            messagebox.showwarning("Formato Invalido", "Use o formato HH:MM (ex: 17:30).")

    def remove_schedule_time(self):
        selection = self.current_times_listbox.curselection()
        if selection:
            t = self.current_times_listbox.get(selection[0])
            self.scheduled_times.remove(t)
            self.update_schedule_listbox()
            self.update_schedule_display()
            self.save_config()
        else:
            messagebox.showwarning("Nenhum Selecionado", "Por favor, selecione um horario para remover.")

    # ------------------------------------------------------------------
    # Pares de diretorios
    # ------------------------------------------------------------------
    def add_pair(self):
        if len(self.directory_pairs) >= 200:
            messagebox.showwarning("Limite Atingido", "Voce atingiu o limite de 200 pares de diretorios.")
            return

        dialog = tk.Toplevel(self.master)
        dialog.title("Adicionar Par de Diretorios")
        dialog.transient(self.master)
        dialog.grab_set()
        self.apply_icon_to_window(dialog)

        tk.Label(dialog, text="Origem:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        source_entry = tk.Entry(dialog, width=50)
        source_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(dialog, text="Selecionar",
                  command=lambda: self.choose_directory(source_entry)).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(dialog, text="Destino:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        dest_entry = tk.Entry(dialog, width=50)
        dest_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(dialog, text="Selecionar",
                  command=lambda: self.choose_directory(dest_entry)).grid(row=1, column=2, padx=5, pady=5)

        def confirm():
            source = source_entry.get().strip()
            destination = dest_entry.get().strip()
            if source and destination:
                item = self.tree.insert("", tk.END, values=(source, destination, "", "0%", "--:--", "0"))
                self.directory_pairs.append({"source": source, "destination": destination, "item": item})
                self.progress_bars[item] = ttk.Progressbar(self.tree, length=140, mode="determinate")
                self.save_config()
                dialog.destroy()
            else:
                messagebox.showwarning("Entrada Invalida", "Por favor, selecione ambos os diretorios.")

        tk.Button(dialog, text="Confirmar", command=confirm).grid(row=2, column=0, columnspan=3, pady=10)

    def remove_pair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Nenhum Selecionado", "Por favor, selecione um par para remover.")
            return
        for item in selected:
            index = self.tree.index(item)
            self.directory_pairs.pop(index)
            self.tree.delete(item)
            self.progress_bars.pop(item, None)
        self.save_config()

    def edit_pair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Nenhum Selecionado", "Por favor, selecione um par para editar.")
            return
        if len(selected) > 1:
            messagebox.showwarning("Selecao Invalida", "Por favor, selecione apenas um par para editar.")
            return

        item = selected[0]
        index = self.tree.index(item)
        pair = self.directory_pairs[index]

        dialog = tk.Toplevel(self.master)
        dialog.title("Editar Par de Diretorios")
        dialog.transient(self.master)
        dialog.grab_set()
        self.apply_icon_to_window(dialog)

        tk.Label(dialog, text="Origem:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        source_entry = tk.Entry(dialog, width=50)
        source_entry.insert(0, pair["source"])
        source_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(dialog, text="Selecionar",
                  command=lambda: self.choose_directory(source_entry)).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(dialog, text="Destino:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        dest_entry = tk.Entry(dialog, width=50)
        dest_entry.insert(0, pair["destination"])
        dest_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(dialog, text="Selecionar",
                  command=lambda: self.choose_directory(dest_entry)).grid(row=1, column=2, padx=5, pady=5)

        def confirm():
            source = source_entry.get().strip()
            destination = dest_entry.get().strip()
            if source and destination:
                self.directory_pairs[index] = {"source": source, "destination": destination, "item": item}
                self.tree.item(item, values=(source, destination, "", "0%", "--:--", "0"))
                self.save_config()
                dialog.destroy()
            else:
                messagebox.showwarning("Entrada Invalida", "Por favor, selecione ambos os diretorios.")

        tk.Button(dialog, text="Confirmar", command=confirm).grid(row=2, column=0, columnspan=3, pady=10)

    def choose_directory(self, entry):
        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)

    # ------------------------------------------------------------------
    # Logica de copia (passagem unica, thread-safe, sem chamadas Tkinter)
    # ------------------------------------------------------------------
    @staticmethod
    def _precisa_copiar(origem_path, destino_path):
        """Retorna True se o arquivo de origem deve ser copiado para o destino.
        Usa uma unica chamada os.stat por lado para minimizar I/O.
        Regras:
          - destino nao existe           -> copiar
          - origem mais recente (> 1 s)  -> copiar
          - caso contrario               -> nao copiar
        """
        try:
            src_st = os.stat(origem_path)
        except OSError:
            return False  # origem inacessivel; nao tenta copiar
        try:
            dst_st = os.stat(destino_path)
        except OSError:
            return True   # destino nao existe
        return (src_st.st_mtime - dst_st.st_mtime) > 1.0

    def copy_files_singlepass(self, origem, destino, item):
        """Percorre a origem UMA unica vez: verifica e copia na mesma passagem.
        Nao ha pre-contagem; o progresso e atualizado a cada segundo (throttle
        por tempo), o que evita sobrecarga de I/O em pastas com muitos arquivos.
        Retorna o numero de arquivos copiados.
        """
        if not os.path.isdir(origem):
            self._status("Erro: Origem nao encontrada - {0}".format(origem), True)
            return 0

        files_copied  = 0
        files_seen    = 0
        start_time    = time.time()
        last_ui_time  = start_time  # throttle: atualiza UI no maximo 1x/s

        try:
            makedirs_compat(destino)

            for root, dirs, files in os.walk(origem):
                if not self.copying:
                    break

                rel_path  = os.path.relpath(root, origem)
                dest_root = os.path.join(destino, rel_path) if rel_path != '.' else destino

                for arquivo in files:
                    if not self.copying:
                        return files_copied

                    files_seen   += 1
                    origem_path   = os.path.join(root, arquivo)
                    destino_path  = os.path.join(dest_root, arquivo)

                    if self._precisa_copiar(origem_path, destino_path):
                        try:
                            makedirs_compat(dest_root)
                            shutil.copy2(origem_path, destino_path)
                            files_copied += 1
                        except Exception as e:
                            print("Erro ao copiar {0}: {1}".format(origem_path, e))

                    # Atualiza UI no maximo 1x por segundo (throttle por tempo)
                    now = time.time()
                    if now - last_ui_time >= 1.0:
                        last_ui_time = now
                        elapsed = now - start_time
                        self._progress(item, 0, "--:--", files_copied, files_seen)
                        self._status("Copiando: {0} copiados / {1} verificados".format(
                            files_copied, files_seen))

        except Exception as e:
            print("Erro geral na copia: {0}".format(e))
            self._status("Erro durante copia: {0}".format(str(e)[:60]), True)

        return files_copied

    def start_copy_all(self):
        if self.copying:
            messagebox.showwarning("Em Progresso", "A copia ja esta em andamento.")
            return
        t = thread_compat(target=self.copiar_todos_optimized, daemon=True)
        t.start()

    def copiar_todos_optimized(self, show_message=True):
        if self.copying:
            return

        self.copying    = True
        total_start     = time.time()
        total_copied    = 0

        try:
            self._status("Iniciando backup...")

            for pair in self.directory_pairs:
                if not self.copying:
                    break
                src = pair.get("source", "")
                dst = pair.get("destination", "")
                if src and dst:
                    # Reseta visual do par antes de comecar
                    self._progress(pair["item"], 0, "--:--", 0, 0)
                    copied = self.copy_files_singlepass(src, dst, pair["item"])
                    total_copied += copied
                    # Marca par como concluido
                    self._progress(pair["item"], 100, "00:00", copied, copied)

            # Registra horario do backup
            current_time = datetime.datetime.now().strftime("%H:%M")
            self.last_backup_date[current_time] = datetime.datetime.now().date()

            elapsed = time.time() - total_start
            self._status("Backup concluido! {0} arquivo(s) copiado(s) em {1:.1f}s".format(
                total_copied, elapsed))
            self._push(MSG_DONE, (total_copied, elapsed))

            if show_message:
                if total_copied == 0:
                    self._msginfo("Backup", "Nenhum arquivo novo ou modificado encontrado.")
                else:
                    self._msginfo(
                        "Concluido",
                        "Backup finalizado!\nArquivos copiados: {0}\nTempo: {1:.1f} segundos".format(
                            total_copied, elapsed)
                    )

        except Exception as e:
            self._status("Erro durante backup: {0}".format(str(e)[:60]), True)
            if show_message:
                self._msgerror("Erro", "Erro durante backup: {0}".format(e))
        finally:
            self.copying = False

    # ------------------------------------------------------------------
    # Automacao
    # ------------------------------------------------------------------
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
        """Adiciona ou remove entrada no registro para iniciar com o Windows."""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "FerragilBackup"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enable:
                exe_path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, '"' + exe_path + '"')
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except (WindowsError, OSError):
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print("Erro ao configurar autostart: {0}".format(e))

    def start_automation(self):
        """Inicia threads de automacao: loop de horarios + backup ao abrir."""
        self.stop_automation.clear()
        t1 = thread_compat(target=self._automation_loop, daemon=True)
        t1.start()
        # Backup imediato ao abrir (pequeno delay para a UI ficar pronta)
        t2 = thread_compat(target=self._backup_on_startup, daemon=True)
        t2.start()

    def _automation_loop(self):
        """Verifica horarios programados sem desperdicar CPU.
        Dorme ate o proximo minuto inteiro; acorda e verifica o horario atual."""
        last_triggered = {}  # hora_str -> date

        while not self.stop_automation.is_set() and self.running:
            now = datetime.datetime.now()
            current_time_str = "{0:02d}:{1:02d}".format(now.hour, now.minute)
            current_date     = now.date()

            if current_time_str in self.scheduled_times:
                if last_triggered.get(current_time_str) != current_date:
                    # Evita disparar duas vezes no mesmo minuto
                    last_triggered[current_time_str] = current_date
                    # Usa tambem self.last_backup_date para compatibilidade
                    self.last_backup_date[current_time_str] = current_date
                    if not self.copying:
                        t = thread_compat(target=self.copiar_todos_optimized, args=(False,), daemon=True)
                        t.start()

            # Dorme ate o proximo minuto inteiro (overhead minimo)
            next_minute   = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
            sleep_seconds = max(5, (next_minute - now).total_seconds())
            # Usa stop_automation.wait() para acordar cedo se o evento for setado
            self.stop_automation.wait(timeout=sleep_seconds)

    def _backup_on_startup(self):
        """Faz um backup ao iniciar o software (com pequeno delay)."""
        time.sleep(3)
        if self.running and not self.copying:
            self.copiar_todos_optimized(show_message=False)

    # ------------------------------------------------------------------
    # Fechamento
    # ------------------------------------------------------------------
    def on_close(self):
        self.running = False
        self.stop_automation.set()
        self.save_config()
        # Remove arquivo temporario do ICO
        try:
            if self._ico_tmp and os.path.exists(self._ico_tmp):
                os.remove(self._ico_tmp)
        except Exception:
            pass
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopierApp(root)
    root.mainloop()
