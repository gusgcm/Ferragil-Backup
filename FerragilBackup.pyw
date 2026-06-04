# -*- coding: utf-8 -*-
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
    from Tkinter import IntVar, StringVar, Checkbutton
    import ttk
    import _winreg as winreg
    from collections import deque
    string_types = (str, unicode)
    text_type = unicode
else:
    import tkinter as tk
    from tkinter import messagebox, IntVar, StringVar, Checkbutton, ttk
    import winreg
    from collections import deque
    string_types = (str,)
    text_type = str

CONFIG_APP_DIR = "FerragilBackup"
COPY_BUFFER    = 1024 * 1024

MSG_PROGRESS = "progress"
MSG_STATUS   = "status"
MSG_INFO     = "info"
MSG_WARN     = "warn"
MSG_ERROR    = "error"
MSG_DONE     = "done"

# ---------------------------------------------------------------------------
# Traduções / Translations / Traducciones
# ---------------------------------------------------------------------------
LANGUAGES = {
    "pt_BR": u"Português (BR)",
    "en":    u"English",
    "es":    u"Español",
    "fr":    u"Français",
    "de":    u"Deutsch",
}

TRANSLATIONS = {
    # ----- Português Brasileiro -----
    "pt_BR": {
        "app_title":               u"Ferragil - Backup",
        "btn_add_pair":            u"Adicionar Par",
        "btn_remove":              u"Remover Selecionado",
        "btn_edit":                u"Editar Selecionado",
        "btn_copy_all":            u"Copiar Todos",
        "btn_schedule":            u"Configurar Horários",
        "chk_automation":          u"Automação",
        "chk_systray":             u"Systray",
        "lbl_scheduled":           u"Horários Programados:",
        "lbl_no_schedule":         u"Nenhum horário programado",
        "lbl_ready":               u"Pronto",
        "col_source":              u"Origem",
        "col_dest":                u"Destino",
        "col_files":               u"Arquivos",
        "dlg_sched_title":         u"Horários de Automação",
        "lbl_current_times":       u"Horários Atuais",
        "lbl_add_time":            u"Adicionar Novo Horário",
        "lbl_time_hhmm":           u"Horário (HH:MM):",
        "btn_add":                 u"Adicionar",
        "btn_close":               u"Fechar",
        "tip_format_24h":          u"Dica: Use formato 24h (ex: 09:30, 17:00)",
        "lbl_source":              u"Origem:",
        "lbl_dest":                u"Destino:",
        "btn_select":              u"Selecionar...",
        "btn_confirm":             u"Confirmar",
        "dlg_add_pair":            u"Adicionar Par de Diretórios",
        "dlg_edit_pair":           u"Editar Par de Diretórios",
        "browse_source":           u"Selecionar Pasta de Origem",
        "browse_dest":             u"Selecionar Pasta de Destino",
        "browse_folder":           u"Selecionar Pasta",
        "warn_limit_title":        u"Limite Atingido",
        "warn_limit_msg":          u"Você atingiu o limite de 200 pares de diretórios.",
        "warn_none_sel_title":     u"Nenhum Selecionado",
        "warn_none_sel_pair":      u"Por favor, selecione um par para remover.",
        "warn_none_sel_edit":      u"Por favor, selecione um par para editar.",
        "warn_multi_sel_title":    u"Seleção Inválida",
        "warn_multi_sel_msg":      u"Por favor, selecione apenas um par para editar.",
        "warn_invalid_title":      u"Entrada Inválida",
        "warn_invalid_dirs":       u"Por favor, selecione ambos os diretórios.",
        "warn_dup_time_title":     u"Horário Duplicado",
        "warn_dup_time_msg":       u"Este horário já está programado.",
        "warn_bad_fmt_title":      u"Formato Inválido",
        "warn_bad_fmt_msg":        u"Use o formato HH:MM (ex: 17:30).",
        "warn_none_sel_time":      u"Por favor, selecione um horário para remover.",
        "warn_in_progress_title":  u"Em Progresso",
        "warn_in_progress_msg":    u"A cópia já está em andamento.",
        "status_verifying":        u"Verificando {0}...",
        "status_copying":          u"Copiando {0}: {1}/{2} arquivo(s)",
        "status_done":             u"Backup concluído! {0} arquivo(s) em {1:.1f}s",
        "status_err_src":          u"Erro: Origem não encontrada - {0}",
        "status_err_backup":       u"Erro durante backup: {0}",
        "info_no_files_title":     u"Backup",
        "info_no_files_msg":       u"Nenhum arquivo novo ou modificado encontrado.",
        "info_done_title":         u"Concluído",
        "info_done_msg":           u"Backup finalizado!\nArquivos copiados: {0}\nTempo: {1:.1f}s",
        "err_backup_title":        u"Erro",
        "err_backup_msg":          u"Erro durante backup: {0}",
        "tray_restore":            u"Restaurar",
        "tray_quit":               u"Sair",
        "menu_theme":              u"Tema",
        "menu_theme_light":        u"Claro",
        "menu_theme_dark":         u"Escuro",
        "menu_language":           u"Idioma",
        "btn_theme_toggle":        u"☀ Tema",
        "lbl_theme":               u"Tema:",
        "opt_theme_light":         u"Claro",
        "opt_theme_dark":          u"Escuro",
        "lbl_language":            u"Idioma:",
    },
    # ----- English -----
    "en": {
        "app_title":               u"Ferragil - Backup",
        "btn_add_pair":            u"Add Pair",
        "btn_remove":              u"Remove Selected",
        "btn_edit":                u"Edit Selected",
        "btn_copy_all":            u"Copy All",
        "btn_schedule":            u"Configure Schedule",
        "chk_automation":          u"Automation",
        "chk_systray":             u"Systray",
        "lbl_scheduled":           u"Scheduled Times:",
        "lbl_no_schedule":         u"No scheduled times",
        "lbl_ready":               u"Ready",
        "col_source":              u"Source",
        "col_dest":                u"Destination",
        "col_files":               u"Files",
        "dlg_sched_title":         u"Automation Schedule",
        "lbl_current_times":       u"Current Times",
        "lbl_add_time":            u"Add New Time",
        "lbl_time_hhmm":           u"Time (HH:MM):",
        "btn_add":                 u"Add",
        "btn_close":               u"Close",
        "tip_format_24h":          u"Tip: Use 24h format (e.g. 09:30, 17:00)",
        "lbl_source":              u"Source:",
        "lbl_dest":                u"Destination:",
        "btn_select":              u"Browse...",
        "btn_confirm":             u"Confirm",
        "dlg_add_pair":            u"Add Directory Pair",
        "dlg_edit_pair":           u"Edit Directory Pair",
        "browse_source":           u"Select Source Folder",
        "browse_dest":             u"Select Destination Folder",
        "browse_folder":           u"Select Folder",
        "warn_limit_title":        u"Limit Reached",
        "warn_limit_msg":          u"You have reached the limit of 200 directory pairs.",
        "warn_none_sel_title":     u"Nothing Selected",
        "warn_none_sel_pair":      u"Please select a pair to remove.",
        "warn_none_sel_edit":      u"Please select a pair to edit.",
        "warn_multi_sel_title":    u"Invalid Selection",
        "warn_multi_sel_msg":      u"Please select only one pair to edit.",
        "warn_invalid_title":      u"Invalid Input",
        "warn_invalid_dirs":       u"Please select both directories.",
        "warn_dup_time_title":     u"Duplicate Time",
        "warn_dup_time_msg":       u"This time is already scheduled.",
        "warn_bad_fmt_title":      u"Invalid Format",
        "warn_bad_fmt_msg":        u"Use HH:MM format (e.g. 17:30).",
        "warn_none_sel_time":      u"Please select a time to remove.",
        "warn_in_progress_title":  u"In Progress",
        "warn_in_progress_msg":    u"Copy is already running.",
        "status_verifying":        u"Checking {0}...",
        "status_copying":          u"Copying {0}: {1}/{2} file(s)",
        "status_done":             u"Backup done! {0} file(s) in {1:.1f}s",
        "status_err_src":          u"Error: Source not found - {0}",
        "status_err_backup":       u"Error during backup: {0}",
        "info_no_files_title":     u"Backup",
        "info_no_files_msg":       u"No new or modified files found.",
        "info_done_title":         u"Done",
        "info_done_msg":           u"Backup complete!\nFiles copied: {0}\nTime: {1:.1f}s",
        "err_backup_title":        u"Error",
        "err_backup_msg":          u"Error during backup: {0}",
        "tray_restore":            u"Restore",
        "tray_quit":               u"Quit",
        "menu_theme":              u"Theme",
        "menu_theme_light":        u"Light",
        "menu_theme_dark":         u"Dark",
        "menu_language":           u"Language",
        "btn_theme_toggle":        u"☀ Theme",
        "lbl_theme":               u"Theme:",
        "opt_theme_light":         u"Light",
        "opt_theme_dark":          u"Dark",
        "lbl_language":            u"Language:",
    },
    # ----- Español -----
    "es": {
        "app_title":               u"Ferragil - Copia de Seguridad",
        "btn_add_pair":            u"Agregar Par",
        "btn_remove":              u"Eliminar Seleccionado",
        "btn_edit":                u"Editar Seleccionado",
        "btn_copy_all":            u"Copiar Todo",
        "btn_schedule":            u"Configurar Horarios",
        "chk_automation":          u"Automatización",
        "chk_systray":             u"Bandeja",
        "lbl_scheduled":           u"Horarios Programados:",
        "lbl_no_schedule":         u"Sin horarios programados",
        "lbl_ready":               u"Listo",
        "col_source":              u"Origen",
        "col_dest":                u"Destino",
        "col_files":               u"Archivos",
        "dlg_sched_title":         u"Horarios de Automatización",
        "lbl_current_times":       u"Horarios Actuales",
        "lbl_add_time":            u"Agregar Nuevo Horario",
        "lbl_time_hhmm":           u"Horario (HH:MM):",
        "btn_add":                 u"Agregar",
        "btn_close":               u"Cerrar",
        "tip_format_24h":          u"Consejo: Use formato 24h (ej: 09:30, 17:00)",
        "lbl_source":              u"Origen:",
        "lbl_dest":                u"Destino:",
        "btn_select":              u"Seleccionar...",
        "btn_confirm":             u"Confirmar",
        "dlg_add_pair":            u"Agregar Par de Directorios",
        "dlg_edit_pair":           u"Editar Par de Directorios",
        "browse_source":           u"Seleccionar Carpeta de Origen",
        "browse_dest":             u"Seleccionar Carpeta de Destino",
        "browse_folder":           u"Seleccionar Carpeta",
        "warn_limit_title":        u"Límite Alcanzado",
        "warn_limit_msg":          u"Ha alcanzado el límite de 200 pares de directorios.",
        "warn_none_sel_title":     u"Nada Seleccionado",
        "warn_none_sel_pair":      u"Por favor, seleccione un par para eliminar.",
        "warn_none_sel_edit":      u"Por favor, seleccione un par para editar.",
        "warn_multi_sel_title":    u"Selección Inválida",
        "warn_multi_sel_msg":      u"Por favor, seleccione solo un par para editar.",
        "warn_invalid_title":      u"Entrada Inválida",
        "warn_invalid_dirs":       u"Por favor, seleccione ambos directorios.",
        "warn_dup_time_title":     u"Horario Duplicado",
        "warn_dup_time_msg":       u"Este horario ya está programado.",
        "warn_bad_fmt_title":      u"Formato Inválido",
        "warn_bad_fmt_msg":        u"Use el formato HH:MM (ej: 17:30).",
        "warn_none_sel_time":      u"Por favor, seleccione un horario para eliminar.",
        "warn_in_progress_title":  u"En Progreso",
        "warn_in_progress_msg":    u"La copia ya está en curso.",
        "status_verifying":        u"Verificando {0}...",
        "status_copying":          u"Copiando {0}: {1}/{2} archivo(s)",
        "status_done":             u"¡Copia completada! {0} archivo(s) en {1:.1f}s",
        "status_err_src":          u"Error: Origen no encontrado - {0}",
        "status_err_backup":       u"Error durante copia de seguridad: {0}",
        "info_no_files_title":     u"Copia de Seguridad",
        "info_no_files_msg":       u"No se encontraron archivos nuevos o modificados.",
        "info_done_title":         u"Completado",
        "info_done_msg":           u"¡Copia de seguridad finalizada!\nArchivos copiados: {0}\nTiempo: {1:.1f}s",
        "err_backup_title":        u"Error",
        "err_backup_msg":          u"Error durante copia de seguridad: {0}",
        "tray_restore":            u"Restaurar",
        "tray_quit":               u"Salir",
        "menu_theme":              u"Tema",
        "menu_theme_light":        u"Claro",
        "menu_theme_dark":         u"Oscuro",
        "menu_language":           u"Idioma",
        "btn_theme_toggle":        u"☀ Tema",
        "lbl_theme":               u"Tema:",
        "opt_theme_light":         u"Claro",
        "opt_theme_dark":          u"Oscuro",
        "lbl_language":            u"Idioma:",
    },
    # ----- Français -----
    "fr": {
        "app_title":               u"Ferragil - Sauvegarde",
        "btn_add_pair":            u"Ajouter Paire",
        "btn_remove":              u"Supprimer Sélection",
        "btn_edit":                u"Modifier Sélection",
        "btn_copy_all":            u"Tout Copier",
        "btn_schedule":            u"Configurer Horaires",
        "chk_automation":          u"Automatisation",
        "chk_systray":             u"Systray",
        "lbl_scheduled":           u"Horaires Programmés:",
        "lbl_no_schedule":         u"Aucun horaire programmé",
        "lbl_ready":               u"Prêt",
        "col_source":              u"Source",
        "col_dest":                u"Destination",
        "col_files":               u"Fichiers",
        "dlg_sched_title":         u"Horaires d'Automatisation",
        "lbl_current_times":       u"Horaires Actuels",
        "lbl_add_time":            u"Ajouter Nouvel Horaire",
        "lbl_time_hhmm":           u"Horaire (HH:MM):",
        "btn_add":                 u"Ajouter",
        "btn_close":               u"Fermer",
        "tip_format_24h":          u"Astuce: Utilisez le format 24h (ex: 09:30, 17:00)",
        "lbl_source":              u"Source:",
        "lbl_dest":                u"Destination:",
        "btn_select":              u"Parcourir...",
        "btn_confirm":             u"Confirmer",
        "dlg_add_pair":            u"Ajouter Paire de Répertoires",
        "dlg_edit_pair":           u"Modifier Paire de Répertoires",
        "browse_source":           u"Sélectionner Dossier Source",
        "browse_dest":             u"Sélectionner Dossier Destination",
        "browse_folder":           u"Sélectionner Dossier",
        "warn_limit_title":        u"Limite Atteinte",
        "warn_limit_msg":          u"Vous avez atteint la limite de 200 paires de répertoires.",
        "warn_none_sel_title":     u"Rien Sélectionné",
        "warn_none_sel_pair":      u"Veuillez sélectionner une paire à supprimer.",
        "warn_none_sel_edit":      u"Veuillez sélectionner une paire à modifier.",
        "warn_multi_sel_title":    u"Sélection Invalide",
        "warn_multi_sel_msg":      u"Veuillez sélectionner une seule paire à modifier.",
        "warn_invalid_title":      u"Entrée Invalide",
        "warn_invalid_dirs":       u"Veuillez sélectionner les deux répertoires.",
        "warn_dup_time_title":     u"Horaire Dupliqué",
        "warn_dup_time_msg":       u"Cet horaire est déjà programmé.",
        "warn_bad_fmt_title":      u"Format Invalide",
        "warn_bad_fmt_msg":        u"Utilisez le format HH:MM (ex: 17:30).",
        "warn_none_sel_time":      u"Veuillez sélectionner un horaire à supprimer.",
        "warn_in_progress_title":  u"En Cours",
        "warn_in_progress_msg":    u"La copie est déjà en cours.",
        "status_verifying":        u"Vérification de {0}...",
        "status_copying":          u"Copie de {0}: {1}/{2} fichier(s)",
        "status_done":             u"Sauvegarde terminée! {0} fichier(s) en {1:.1f}s",
        "status_err_src":          u"Erreur: Source non trouvée - {0}",
        "status_err_backup":       u"Erreur pendant la sauvegarde: {0}",
        "info_no_files_title":     u"Sauvegarde",
        "info_no_files_msg":       u"Aucun fichier nouveau ou modifié trouvé.",
        "info_done_title":         u"Terminé",
        "info_done_msg":           u"Sauvegarde terminée!\nFichiers copiés: {0}\nTemps: {1:.1f}s",
        "err_backup_title":        u"Erreur",
        "err_backup_msg":          u"Erreur pendant la sauvegarde: {0}",
        "tray_restore":            u"Restaurer",
        "tray_quit":               u"Quitter",
        "menu_theme":              u"Thème",
        "menu_theme_light":        u"Clair",
        "menu_theme_dark":         u"Sombre",
        "menu_language":           u"Langue",
        "btn_theme_toggle":        u"☀ Thème",
        "lbl_theme":               u"Thème:",
        "opt_theme_light":         u"Clair",
        "opt_theme_dark":          u"Sombre",
        "lbl_language":            u"Langue:",
    },
    # ----- Deutsch -----
    "de": {
        "app_title":               u"Ferragil - Sicherung",
        "btn_add_pair":            u"Paar hinzufügen",
        "btn_remove":              u"Auswahl entfernen",
        "btn_edit":                u"Auswahl bearbeiten",
        "btn_copy_all":            u"Alle kopieren",
        "btn_schedule":            u"Zeitplan konfigurieren",
        "chk_automation":          u"Automatisierung",
        "chk_systray":             u"Systray",
        "lbl_scheduled":           u"Geplante Zeiten:",
        "lbl_no_schedule":         u"Keine geplanten Zeiten",
        "lbl_ready":               u"Bereit",
        "col_source":              u"Quelle",
        "col_dest":                u"Ziel",
        "col_files":               u"Dateien",
        "dlg_sched_title":         u"Automatisierungszeiten",
        "lbl_current_times":       u"Aktuelle Zeiten",
        "lbl_add_time":            u"Neue Zeit hinzufügen",
        "lbl_time_hhmm":           u"Zeit (HH:MM):",
        "btn_add":                 u"Hinzufügen",
        "btn_close":               u"Schließen",
        "tip_format_24h":          u"Tipp: 24h-Format verwenden (z.B. 09:30, 17:00)",
        "lbl_source":              u"Quelle:",
        "lbl_dest":                u"Ziel:",
        "btn_select":              u"Durchsuchen...",
        "btn_confirm":             u"Bestätigen",
        "dlg_add_pair":            u"Verzeichnispaar hinzufügen",
        "dlg_edit_pair":           u"Verzeichnispaar bearbeiten",
        "browse_source":           u"Quellordner auswählen",
        "browse_dest":             u"Zielordner auswählen",
        "browse_folder":           u"Ordner auswählen",
        "warn_limit_title":        u"Limit erreicht",
        "warn_limit_msg":          u"Sie haben das Limit von 200 Verzeichnispaaren erreicht.",
        "warn_none_sel_title":     u"Nichts ausgewählt",
        "warn_none_sel_pair":      u"Bitte wählen Sie ein Paar zum Entfernen aus.",
        "warn_none_sel_edit":      u"Bitte wählen Sie ein Paar zum Bearbeiten aus.",
        "warn_multi_sel_title":    u"Ungültige Auswahl",
        "warn_multi_sel_msg":      u"Bitte wählen Sie nur ein Paar zum Bearbeiten aus.",
        "warn_invalid_title":      u"Ungültige Eingabe",
        "warn_invalid_dirs":       u"Bitte wählen Sie beide Verzeichnisse aus.",
        "warn_dup_time_title":     u"Doppelte Zeit",
        "warn_dup_time_msg":       u"Diese Zeit ist bereits geplant.",
        "warn_bad_fmt_title":      u"Ungültiges Format",
        "warn_bad_fmt_msg":        u"Verwenden Sie das Format HH:MM (z.B. 17:30).",
        "warn_none_sel_time":      u"Bitte wählen Sie eine Zeit zum Entfernen aus.",
        "warn_in_progress_title":  u"In Bearbeitung",
        "warn_in_progress_msg":    u"Kopiervorgang läuft bereits.",
        "status_verifying":        u"Überprüfe {0}...",
        "status_copying":          u"Kopiere {0}: {1}/{2} Datei(en)",
        "status_done":             u"Sicherung abgeschlossen! {0} Datei(en) in {1:.1f}s",
        "status_err_src":          u"Fehler: Quelle nicht gefunden - {0}",
        "status_err_backup":       u"Fehler bei der Sicherung: {0}",
        "info_no_files_title":     u"Sicherung",
        "info_no_files_msg":       u"Keine neuen oder geänderten Dateien gefunden.",
        "info_done_title":         u"Fertig",
        "info_done_msg":           u"Sicherung abgeschlossen!\nKopierte Dateien: {0}\nZeit: {1:.1f}s",
        "err_backup_title":        u"Fehler",
        "err_backup_msg":          u"Fehler bei der Sicherung: {0}",
        "tray_restore":            u"Wiederherstellen",
        "tray_quit":               u"Beenden",
        "menu_theme":              u"Design",
        "menu_theme_light":        u"Hell",
        "menu_theme_dark":         u"Dunkel",
        "menu_language":           u"Sprache",
        "btn_theme_toggle":        u"☀ Design",
        "lbl_theme":               u"Design:",
        "opt_theme_light":         u"Hell",
        "opt_theme_dark":          u"Dunkel",
        "lbl_language":            u"Sprache:",
    },
}

# ---------------------------------------------------------------------------
# Paletas de tema
# ---------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg":            "#f0f0f0",
        "fg":            "#000000",
        "btn_bg":        "#e1e1e1",
        "btn_fg":        "#000000",
        "btn_active_bg": "#c8c8c8",
        "frame_bg":      "#f0f0f0",
        "label_bg":      "#f0f0f0",
        "label_fg":      "#000000",
        "status_fg":     "#0000cc",
        "status_err_fg": "#cc0000",
        "schedule_fg":   "#0000aa",
        "entry_bg":      "#ffffff",
        "entry_fg":      "#000000",
        "listbox_bg":    "#ffffff",
        "listbox_fg":    "#000000",
        "labelframe_fg": "#000000",
        "tree_bg":       "#ffffff",
        "tree_fg":       "#000000",
        "tree_select":   "#0078d7",
        "tree_field":    "#ffffff",
    },
    "dark": {
        "bg":            "#2b2b2b",
        "fg":            "#e8e8e8",
        "btn_bg":        "#3c3f41",
        "btn_fg":        "#e8e8e8",
        "btn_active_bg": "#515658",
        "frame_bg":      "#2b2b2b",
        "label_bg":      "#2b2b2b",
        "label_fg":      "#e8e8e8",
        "status_fg":     "#6ab4f5",
        "status_err_fg": "#ff6b6b",
        "schedule_fg":   "#82aaff",
        "entry_bg":      "#3c3f41",
        "entry_fg":      "#e8e8e8",
        "listbox_bg":    "#3c3f41",
        "listbox_fg":    "#e8e8e8",
        "labelframe_fg": "#e8e8e8",
        "tree_bg":       "#3c3f41",
        "tree_fg":       "#e8e8e8",
        "tree_select":   "#4a7096",
        "tree_field":    "#3c3f41",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def makedirs_compat(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            pass


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


def _get_real_exe_path():
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            try:
                return os.path.abspath(sys.argv[0])
            except Exception:
                pass
        try:
            return os.path.abspath(sys.executable)
        except Exception:
            pass
    try:
        return os.path.abspath(__file__)
    except Exception:
        return None


def _query_appdata_from_registry():
    try:
        if PY2:
            import _winreg as reg
        else:
            import winreg as reg
        key = reg.OpenKey(
            reg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        try:
            val, _ = reg.QueryValueEx(key, 'AppData')
        finally:
            reg.CloseKey(key)
        if val:
            return val
    except Exception:
        pass
    return None


def _get_appdata_dir():
    p = os.environ.get('APPDATA') or os.environ.get('appdata')
    if p:
        return p
    p = _query_appdata_from_registry()
    if p:
        return p
    try:
        p = os.path.expandvars(r'%APPDATA%')
        if p and p != r'%APPDATA%':
            return p
    except Exception:
        pass
    try:
        p = os.path.expanduser('~')
        if p:
            return p
    except Exception:
        pass
    return os.getcwd()


def _get_config_path():
    exe = _get_real_exe_path()
    if exe:
        return os.path.join(os.path.dirname(exe), 'config.json')
    try:
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'config.json')
    except Exception:
        return 'config.json'


def _to_utf8_bytes(s):
    if PY2:
        if isinstance(s, unicode):
            return s.encode('utf-8')
        try:
            return s.decode('mbcs').encode('utf-8')
        except Exception:
            try:
                return s.decode('utf-8').encode('utf-8')
            except Exception:
                return s
    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode('utf-8')
    return str(s).encode('utf-8')


def _from_utf8_bytes(b):
    if PY2:
        try:
            return b.decode('utf-8')
        except Exception:
            try:
                return b.decode('mbcs')
            except Exception:
                return b
    if isinstance(b, bytes):
        return b.decode('utf-8')
    return b


def load_config_from_disk():
    path = _get_config_path()
    if not os.path.isfile(path):
        return None
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        text = _from_utf8_bytes(raw)
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return None


def save_config_to_disk(config):
    path = _get_config_path()
    try:
        d = os.path.dirname(path)
        if d and not os.path.isdir(d):
            try:
                os.makedirs(d)
            except OSError:
                pass
        tmp_path = path + u".tmp"
        payload = json.dumps(config, indent=4, ensure_ascii=False)
        with open(tmp_path, 'wb') as f:
            f.write(_to_utf8_bytes(payload))
        if os.path.isfile(path):
            try:
                os.remove(path)
            except Exception:
                pass
        os.rename(tmp_path, path)
        return True, path
    except Exception as e:
        return False, u"{0}: {1}".format(path, e)


def _find_icon_path():
    seen = set()
    candidates = [_get_app_dir()]
    exe_path = _get_real_exe_path()
    if exe_path:
        candidates.append(os.path.dirname(exe_path))
    for base in candidates:
        if not base or base in seen:
            continue
        seen.add(base)
        for name in ("FerragilBackup.ico", "logoF.ico", "icon.ico"):
            p = os.path.join(base, name)
            if os.path.isfile(p):
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
                ico_path if not PY2 else text_type(ico_path),
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

        try:
            ole.CoInitialize(None)
        except Exception:
            pass

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


# ---------------------------------------------------------------------------
# Aplicação principal
# ---------------------------------------------------------------------------
class FileCopierApp:
    def __init__(self, master):
        self.master = master

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

        # Referências a widgets dinâmicos (para reaplicar tema/idioma)
        self._dynamic_widgets = []

        self.load_config()

        # Idioma e tema (lidos da config ou padrão)
        self._lang  = self.config_data.get("language", "pt_BR")
        if self._lang not in TRANSLATIONS:
            self._lang = "pt_BR"
        self._theme = self.config_data.get("theme", "light")
        if self._theme not in THEMES:
            self._theme = "light"

        self._build_ui()
        self._apply_theme()

        if self.config_data.get("automation", False):
            self.automation_var.set(1)
            self.start_automation()

        if self.config_data.get("systray", False):
            self.systray_var.set(1)
            self.master.after(300, self._hide_to_tray)

        self._pump_ui_queue()

    # ------------------------------------------------------------------
    # Tradução
    # ------------------------------------------------------------------
    def tr(self, key, *args):
        """Retorna string traduzida para o idioma atual."""
        lang_dict = TRANSLATIONS.get(self._lang, TRANSLATIONS["pt_BR"])
        text = lang_dict.get(key, TRANSLATIONS["pt_BR"].get(key, key))
        if args:
            try:
                text = text.format(*args)
            except Exception:
                pass
        return text

    # ------------------------------------------------------------------
    # Construção da UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.master.title(self.tr("app_title"))
        self.master.option_add('*Font', 'Tahoma 8')

        # ── Barra de ferramentas superior ──
        top_frame = tk.Frame(self.master)
        top_frame.pack(padx=10, pady=5, fill=tk.X)
        self._reg(top_frame)

        control_frame = tk.Frame(top_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._reg(control_frame)

        button_frame = tk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        self._reg(button_frame)

        self.btn_add_pair = tk.Button(
            button_frame, text=self.tr("btn_add_pair"),
            command=self.add_pair)
        self.btn_add_pair.pack(side=tk.LEFT, padx=5)

        self.btn_remove = tk.Button(
            button_frame, text=self.tr("btn_remove"),
            command=self.remove_pair)
        self.btn_remove.pack(side=tk.LEFT, padx=5)

        self.btn_edit = tk.Button(
            button_frame, text=self.tr("btn_edit"),
            command=self.edit_pair)
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        self.btn_copy_all = tk.Button(
            button_frame, text=self.tr("btn_copy_all"),
            command=self.start_copy_all)
        self.btn_copy_all.pack(side=tk.LEFT, padx=5)

        self.btn_schedule = tk.Button(
            button_frame, text=self.tr("btn_schedule"),
            command=self.configurar_horarios)
        self.btn_schedule.pack(side=tk.LEFT, padx=5)

        self.chk_automation = Checkbutton(
            button_frame, text=self.tr("chk_automation"),
            variable=self.automation_var,
            command=self.toggle_automation)
        self.chk_automation.pack(side=tk.LEFT, padx=5)

        self.chk_systray = Checkbutton(
            button_frame, text=self.tr("chk_systray"),
            variable=self.systray_var,
            command=self.toggle_systray)
        self.chk_systray.pack(side=tk.LEFT, padx=2)

        # ── Linha de tema e idioma ──
        settings_frame = tk.Frame(control_frame)
        settings_frame.pack(fill=tk.X, pady=2)
        self._reg(settings_frame)

        self.lbl_theme = tk.Label(settings_frame, text=self.tr("lbl_theme"),
                                  font=('Tahoma', 8))
        self.lbl_theme.pack(side=tk.LEFT, padx=5)

        self.btn_theme = tk.Button(
            settings_frame,
            text=self.tr("opt_theme_dark") if self._theme == "light" else self.tr("opt_theme_light"),
            width=8,
            command=self.toggle_theme)
        self.btn_theme.pack(side=tk.LEFT, padx=2)

        self.lbl_language = tk.Label(settings_frame, text=self.tr("lbl_language"),
                                     font=('Tahoma', 8))
        self.lbl_language.pack(side=tk.LEFT, padx=8)

        self._lang_var = StringVar(value=self._lang)
        lang_codes = list(LANGUAGES.keys())
        lang_labels = [LANGUAGES[c] for c in lang_codes]

        # OptionMenu compatível com Python 2/3
        self.lang_menu = tk.OptionMenu(
            settings_frame, self._lang_var,
            *lang_codes,
            command=self._on_language_change)
        # Exibir nome legível no botão
        self._lang_var.set(self._lang)
        self.lang_menu.config(width=14)
        self.lang_menu.pack(side=tk.LEFT, padx=2)

        # Atualiza o texto exibido no OptionMenu para mostrar o nome do idioma
        self._update_lang_menu_label()

        # ── Linha de horários ──
        schedule_frame = tk.Frame(control_frame)
        schedule_frame.pack(fill=tk.X, pady=2)
        self._reg(schedule_frame)

        self.lbl_scheduled_key = tk.Label(
            schedule_frame, text=self.tr("lbl_scheduled"),
            font=('Tahoma', 8, 'bold'))
        self.lbl_scheduled_key.pack(side=tk.LEFT, padx=5)

        self.schedule_label = tk.Label(
            schedule_frame, text="", font=('Tahoma', 8))
        self.schedule_label.pack(side=tk.LEFT, padx=5)
        self.update_schedule_display()

        # ── Status ──
        status_frame = tk.Frame(control_frame)
        status_frame.pack(fill=tk.X, pady=2)
        self._reg(status_frame)

        self.status_label = tk.Label(
            status_frame, text=self.tr("lbl_ready"),
            font=('Tahoma', 7))
        self.status_label.pack(side=tk.LEFT, padx=5)

        # ── Treeview ──
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self._reg(main_frame)

        self.tree = ttk.Treeview(
            main_frame,
            columns=("Source", "Destination", "Files"),
            show="headings",
            height=15)
        self.tree.heading("Source",      text=self.tr("col_source"))
        self.tree.heading("Destination", text=self.tr("col_dest"))
        self.tree.heading("Files",       text=self.tr("col_files"))
        self.tree.column("Source",      width=240, anchor="w")
        self.tree.column("Destination", width=240, anchor="w")
        self.tree.column("Files",       width=80,  anchor="center")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        for pair in self.config_data.get("directory_pairs", []):
            src = pair.get("source", "")
            dst = pair.get("destination", "")
            if src or dst:
                item = self.tree.insert("", tk.END,
                    values=(src, dst, "0"))
                self.directory_pairs.append({
                    "source":      src,
                    "destination": dst,
                    "item":        item
                })

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Unmap>", self._on_unmap)

    def _reg(self, widget):
        """Registra widget para recoloração de tema."""
        self._dynamic_widgets.append(widget)

    # ------------------------------------------------------------------
    # Tema
    # ------------------------------------------------------------------
    def toggle_theme(self):
        self._theme = "dark" if self._theme == "light" else "light"
        self.config_data["theme"] = self._theme
        self.save_config()
        self._apply_theme()
        # Atualiza texto do botão
        t = self.tr("opt_theme_dark") if self._theme == "light" else self.tr("opt_theme_light")
        try:
            self.btn_theme.config(text=t)
        except Exception:
            pass

    def _apply_theme(self):
        pal = THEMES.get(self._theme, THEMES["light"])

        # Janela raiz
        try:
            self.master.configure(bg=pal["bg"])
        except Exception:
            pass

        # Todos os frames/labels registrados
        for w in self._dynamic_widgets:
            try:
                cls = w.__class__.__name__
                if cls in ("Frame",):
                    w.configure(bg=pal["frame_bg"])
                elif cls in ("Label",):
                    w.configure(bg=pal["label_bg"], fg=pal["label_fg"])
            except Exception:
                pass

        # Botões da toolbar
        btn_list = [
            getattr(self, 'btn_add_pair',  None),
            getattr(self, 'btn_remove',    None),
            getattr(self, 'btn_edit',      None),
            getattr(self, 'btn_copy_all',  None),
            getattr(self, 'btn_schedule',  None),
            getattr(self, 'btn_theme',     None),
        ]
        for btn in btn_list:
            if btn:
                try:
                    btn.configure(
                        bg=pal["btn_bg"], fg=pal["btn_fg"],
                        activebackground=pal["btn_active_bg"],
                        activeforeground=pal["btn_fg"])
                except Exception:
                    pass

        # Checkbuttons
        for chk in [getattr(self, 'chk_automation', None),
                    getattr(self, 'chk_systray', None)]:
            if chk:
                try:
                    chk.configure(
                        bg=pal["frame_bg"], fg=pal["label_fg"],
                        activebackground=pal["frame_bg"],
                        selectcolor=pal["btn_bg"])
                except Exception:
                    pass

        # Labels especiais
        for attr, fg_key in [
            ('lbl_theme',         "label_fg"),
            ('lbl_language',      "label_fg"),
            ('lbl_scheduled_key', "label_fg"),
            ('schedule_label',    "schedule_fg"),
        ]:
            w = getattr(self, attr, None)
            if w:
                try:
                    w.configure(bg=pal["label_bg"], fg=pal[fg_key])
                except Exception:
                    pass

        # Status label (sem erro)
        if hasattr(self, 'status_label'):
            try:
                self.status_label.configure(
                    bg=pal["label_bg"], fg=pal["status_fg"])
            except Exception:
                pass

        # OptionMenu idioma
        if hasattr(self, 'lang_menu'):
            try:
                self.lang_menu.configure(
                    bg=pal["btn_bg"], fg=pal["btn_fg"],
                    activebackground=pal["btn_active_bg"],
                    highlightbackground=pal["btn_bg"])
            except Exception:
                pass

        # TTK Treeview via estilo
        self._apply_ttk_style(pal)

    def _apply_ttk_style(self, pal):
        """Aplica cores TTK ao Treeview — compatível com Python 2/3."""
        try:
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Treeview",
                background=pal["tree_bg"],
                foreground=pal["tree_fg"],
                fieldbackground=pal["tree_field"],
                font=('Tahoma', 8))
            style.map("Treeview",
                background=[("selected", pal["tree_select"])],
                foreground=[("selected", "#ffffff")])
            style.configure("Treeview.Heading",
                background=pal["btn_bg"],
                foreground=pal["btn_fg"],
                font=('Tahoma', 8, 'bold'))
            style.configure("Vertical.TScrollbar",
                background=pal["btn_bg"],
                troughcolor=pal["frame_bg"])
        except Exception:
            pass

    def _apply_theme_to_toplevel(self, window):
        """Aplica tema a uma janela Toplevel e todos os seus filhos."""
        pal = THEMES.get(self._theme, THEMES["light"])
        try:
            window.configure(bg=pal["bg"])
        except Exception:
            pass
        self._theme_widget_tree(window, pal)

    def _theme_widget_tree(self, parent, pal):
        """Percorre recursivamente os filhos e aplica o tema."""
        try:
            children = parent.winfo_children()
        except Exception:
            return
        for w in children:
            cls = w.__class__.__name__
            try:
                if cls == "Frame":
                    w.configure(bg=pal["frame_bg"])
                elif cls == "Label":
                    w.configure(bg=pal["label_bg"], fg=pal["label_fg"])
                elif cls == "Button":
                    w.configure(
                        bg=pal["btn_bg"], fg=pal["btn_fg"],
                        activebackground=pal["btn_active_bg"],
                        activeforeground=pal["btn_fg"])
                elif cls == "LabelFrame":
                    w.configure(
                        bg=pal["frame_bg"], fg=pal["labelframe_fg"])
                elif cls == "Entry":
                    w.configure(
                        bg=pal["entry_bg"], fg=pal["entry_fg"],
                        insertbackground=pal["entry_fg"])
                elif cls == "Listbox":
                    w.configure(
                        bg=pal["listbox_bg"], fg=pal["listbox_fg"],
                        selectbackground=pal["tree_select"],
                        selectforeground="#ffffff")
                elif cls == "Checkbutton":
                    w.configure(
                        bg=pal["frame_bg"], fg=pal["label_fg"],
                        activebackground=pal["frame_bg"],
                        selectcolor=pal["btn_bg"])
            except Exception:
                pass
            self._theme_widget_tree(w, pal)

    # ------------------------------------------------------------------
    # Idioma
    # ------------------------------------------------------------------
    def _on_language_change(self, selected_lang):
        """Chamado pelo OptionMenu quando o usuário muda o idioma."""
        if selected_lang in TRANSLATIONS:
            self._lang = selected_lang
            self.config_data["language"] = self._lang
            self.save_config()
            self._refresh_ui_texts()
            self._update_lang_menu_label()

    def _update_lang_menu_label(self):
        """Atualiza o texto exibido no OptionMenu para o nome legível."""
        try:
            self._lang_var.set(self._lang)
            # Recria o menu com os nomes completos
            menu = self.lang_menu["menu"]
            menu.delete(0, "end")
            for code in LANGUAGES.keys():
                menu.add_command(
                    label=LANGUAGES[code],
                    command=lambda c=code: self._on_language_change(c))
            # Exibe o nome legível no botão
            self.lang_menu.config(text=LANGUAGES.get(self._lang, self._lang))
        except Exception:
            pass

    def _refresh_ui_texts(self):
        """Atualiza todos os textos da UI para o idioma atual."""
        try:
            self.master.title(self.tr("app_title"))
        except Exception:
            pass

        pairs_text = {
            'btn_add_pair':        'btn_add_pair',
            'btn_remove':          'btn_remove',
            'btn_edit':            'btn_edit',
            'btn_copy_all':        'btn_copy_all',
            'btn_schedule':        'btn_schedule',
            'chk_automation':      'chk_automation',
            'chk_systray':         'chk_systray',
            'lbl_scheduled_key':   'lbl_scheduled',
            'lbl_theme':           'lbl_theme',
            'lbl_language':        'lbl_language',
        }
        for attr, key in pairs_text.items():
            w = getattr(self, attr, None)
            if w:
                try:
                    w.config(text=self.tr(key))
                except Exception:
                    pass

        # Botão tema
        try:
            t = self.tr("opt_theme_dark") if self._theme == "light" else self.tr("opt_theme_light")
            self.btn_theme.config(text=t)
        except Exception:
            pass

        # Colunas do treeview
        try:
            self.tree.heading("Source",      text=self.tr("col_source"))
            self.tree.heading("Destination", text=self.tr("col_dest"))
            self.tree.heading("Files",       text=self.tr("col_files"))
        except Exception:
            pass

        # Label de horários
        self.update_schedule_display()

        # Atualiza o menu de idioma
        self._update_lang_menu_label()

    # ------------------------------------------------------------------
    # Ícone da janela
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Fila de mensagens UI (thread-safe)
    # ------------------------------------------------------------------
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
                    try:
                        if total > 0:
                            self.tree.set(item, "Files",
                                          "{0}/{1}".format(copied, total))
                        elif copied > 0:
                            self.tree.set(item, "Files", str(copied))
                    except Exception:
                        pass

                elif msg_type == MSG_STATUS:
                    text, is_error = payload
                    pal = THEMES.get(self._theme, THEMES["light"])
                    fg  = pal["status_err_fg"] if is_error else pal["status_fg"]
                    try:
                        self.status_label.config(text=text, fg=fg)
                    except Exception:
                        pass

                elif msg_type == MSG_INFO:
                    title, text = payload
                    try:
                        messagebox.showinfo(title, text)
                    except Exception:
                        pass

                elif msg_type == MSG_WARN:
                    title, text = payload
                    try:
                        messagebox.showwarning(title, text)
                    except Exception:
                        pass

                elif msg_type == MSG_ERROR:
                    title, text = payload
                    try:
                        messagebox.showerror(title, text)
                    except Exception:
                        pass

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

    # ------------------------------------------------------------------
    # Horários
    # ------------------------------------------------------------------
    def update_schedule_display(self):
        try:
            if self.scheduled_times:
                self.schedule_label.config(
                    text=" | ".join(self.scheduled_times))
            else:
                self.schedule_label.config(text=self.tr("lbl_no_schedule"))
        except Exception:
            pass

    def load_config(self):
        data = load_config_from_disk()
        if isinstance(data, dict):
            self.config_data = data
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
        self.config_data["theme"]            = self._theme
        self.config_data["language"]         = self._lang
        ok, info = save_config_to_disk(self.config_data)
        if not ok:
            try:
                self._status(
                    u"ERRO salvando config: {0}".format(info), True)
            except Exception:
                pass

    def configurar_horarios(self):
        dialog = tk.Toplevel(self.master)
        dialog.title(self.tr("dlg_sched_title"))
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.geometry("350x320")
        self._apply_icon_to_dialog(dialog)

        pal = THEMES.get(self._theme, THEMES["light"])
        try:
            dialog.configure(bg=pal["bg"])
        except Exception:
            pass

        current_frame = tk.LabelFrame(
            dialog, text=self.tr("lbl_current_times"),
            padx=10, pady=10,
            bg=pal["frame_bg"], fg=pal["labelframe_fg"])
        current_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.current_times_listbox = tk.Listbox(
            current_frame, height=6,
            bg=pal["listbox_bg"], fg=pal["listbox_fg"],
            selectbackground=pal["tree_select"],
            selectforeground="#ffffff")
        self.current_times_listbox.pack(
            fill=tk.BOTH, expand=True, padx=5, pady=5)

        current_buttons_frame = tk.Frame(current_frame, bg=pal["frame_bg"])
        current_buttons_frame.pack(fill=tk.X, pady=5)

        tk.Button(
            current_buttons_frame,
            text=self.tr("btn_remove"),
            command=self.remove_schedule_time,
            bg="#994444" if self._theme == "dark" else "#ffcccc",
            fg=pal["btn_fg"],
            activebackground=pal["btn_active_bg"]
        ).pack(side=tk.LEFT, padx=5)

        add_frame = tk.LabelFrame(
            dialog, text=self.tr("lbl_add_time"),
            padx=10, pady=10,
            bg=pal["frame_bg"], fg=pal["labelframe_fg"])
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            add_frame, text=self.tr("lbl_time_hhmm"),
            bg=pal["label_bg"], fg=pal["label_fg"]
        ).pack(side=tk.LEFT, padx=5)

        self.time_entry = tk.Entry(
            add_frame, width=10,
            bg=pal["entry_bg"], fg=pal["entry_fg"],
            insertbackground=pal["entry_fg"])
        self.time_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(
            add_frame,
            text=self.tr("btn_add"),
            command=self.add_schedule_time,
            bg="#449944" if self._theme == "dark" else "#ccffcc",
            fg=pal["btn_fg"],
            activebackground=pal["btn_active_bg"]
        ).pack(side=tk.LEFT, padx=5)

        self.update_schedule_listbox()

        tk.Label(
            dialog, text=self.tr("tip_format_24h"),
            font=('Tahoma', 7), fg="gray",
            bg=pal["label_bg"]
        ).pack(padx=10, pady=2)

        tk.Button(
            dialog, text=self.tr("btn_close"),
            command=dialog.destroy,
            bg=pal["btn_bg"], fg=pal["btn_fg"],
            activebackground=pal["btn_active_bg"]
        ).pack(pady=8)

    def update_schedule_listbox(self):
        try:
            self.current_times_listbox.delete(0, tk.END)
            for t in self.scheduled_times:
                self.current_times_listbox.insert(tk.END, t)
        except Exception:
            pass

    def add_schedule_time(self):
        try:
            t = self.time_entry.get().strip()
        except Exception:
            return
        try:
            time.strptime(t, '%H:%M')
            if t not in self.scheduled_times:
                self.scheduled_times.append(t)
                self.scheduled_times.sort()
                self.update_schedule_listbox()
                self.update_schedule_display()
                self.save_config()
                try:
                    self.time_entry.delete(0, tk.END)
                except Exception:
                    pass
            else:
                messagebox.showwarning(
                    self.tr("warn_dup_time_title"),
                    self.tr("warn_dup_time_msg"))
        except ValueError:
            messagebox.showwarning(
                self.tr("warn_bad_fmt_title"),
                self.tr("warn_bad_fmt_msg"))

    def remove_schedule_time(self):
        try:
            selection = self.current_times_listbox.curselection()
        except Exception:
            selection = ()
        if selection:
            try:
                t = self.current_times_listbox.get(selection[0])
                if t in self.scheduled_times:
                    self.scheduled_times.remove(t)
                self.update_schedule_listbox()
                self.update_schedule_display()
                self.save_config()
            except Exception as e:
                messagebox.showerror("Erro", str(e))
        else:
            messagebox.showwarning(
                self.tr("warn_none_sel_title"),
                self.tr("warn_none_sel_time"))

    # ------------------------------------------------------------------
    # Diálogos de par
    # ------------------------------------------------------------------
    def _make_pair_dialog(self, title, source_val="", dest_val="",
                          on_confirm=None):
        dialog = tk.Toplevel(self.master)
        dialog.title(title)
        dialog.transient(self.master)
        dialog.grab_set()
        dialog.resizable(False, False)
        self._apply_icon_to_dialog(dialog)
        self._apply_theme_to_toplevel(dialog)

        pal = THEMES.get(self._theme, THEMES["light"])

        tk.Label(dialog, text=self.tr("lbl_source"),
                 bg=pal["label_bg"], fg=pal["label_fg"]
                 ).grid(row=0, column=0, padx=8, pady=8, sticky="e")

        source_entry = tk.Entry(
            dialog, width=52,
            bg=pal["entry_bg"], fg=pal["entry_fg"],
            insertbackground=pal["entry_fg"])
        source_entry.insert(0, source_val)
        source_entry.grid(row=0, column=1, padx=5, pady=8)

        def pick_src():
            hwnd = 0
            try:
                hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
            except Exception:
                pass
            r = _browse_folder_win(hwnd_owner=hwnd,
                                   title=self.tr("browse_source"))
            if r:
                source_entry.delete(0, tk.END)
                source_entry.insert(0, r)

        tk.Button(dialog, text=self.tr("btn_select"),
                  command=pick_src,
                  bg=pal["btn_bg"], fg=pal["btn_fg"],
                  activebackground=pal["btn_active_bg"]
                  ).grid(row=0, column=2, padx=5, pady=8)

        tk.Label(dialog, text=self.tr("lbl_dest"),
                 bg=pal["label_bg"], fg=pal["label_fg"]
                 ).grid(row=1, column=0, padx=8, pady=8, sticky="e")

        dest_entry = tk.Entry(
            dialog, width=52,
            bg=pal["entry_bg"], fg=pal["entry_fg"],
            insertbackground=pal["entry_fg"])
        dest_entry.insert(0, dest_val)
        dest_entry.grid(row=1, column=1, padx=5, pady=8)

        def pick_dst():
            hwnd = 0
            try:
                hwnd = ctypes.windll.user32.GetParent(dialog.winfo_id())
            except Exception:
                pass
            r = _browse_folder_win(hwnd_owner=hwnd,
                                   title=self.tr("browse_dest"))
            if r:
                dest_entry.delete(0, tk.END)
                dest_entry.insert(0, r)

        tk.Button(dialog, text=self.tr("btn_select"),
                  command=pick_dst,
                  bg=pal["btn_bg"], fg=pal["btn_fg"],
                  activebackground=pal["btn_active_bg"]
                  ).grid(row=1, column=2, padx=5, pady=8)

        def confirm():
            src = source_entry.get().strip()
            dst = dest_entry.get().strip()
            if src and dst:
                dialog.destroy()
                if on_confirm:
                    try:
                        on_confirm(src, dst)
                    except Exception as e:
                        messagebox.showerror("Erro", str(e))
            else:
                messagebox.showwarning(
                    self.tr("warn_invalid_title"),
                    self.tr("warn_invalid_dirs"))

        tk.Button(dialog, text=self.tr("btn_confirm"), width=12,
                  command=confirm,
                  bg=pal["btn_bg"], fg=pal["btn_fg"],
                  activebackground=pal["btn_active_bg"]
                  ).grid(row=2, column=0, columnspan=3, pady=10)

        # Centraliza o diálogo
        dialog.update_idletasks()
        try:
            x = self.master.winfo_x() + (self.master.winfo_width()  - dialog.winfo_width())  // 2
            y = self.master.winfo_y() + (self.master.winfo_height() - dialog.winfo_height()) // 2
            dialog.geometry("+{0}+{1}".format(max(0, x), max(0, y)))
        except Exception:
            pass

    def add_pair(self):
        if len(self.directory_pairs) >= 200:
            messagebox.showwarning(
                self.tr("warn_limit_title"),
                self.tr("warn_limit_msg"))
            return

        def on_confirm(src, dst):
            item = self.tree.insert("", tk.END,
                values=(src, dst, "0"))
            self.directory_pairs.append({
                "source": src, "destination": dst, "item": item})
            self.save_config()

        self._make_pair_dialog(
            self.tr("dlg_add_pair"), on_confirm=on_confirm)

    def remove_pair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.tr("warn_none_sel_title"),
                self.tr("warn_none_sel_pair"))
            return
        for item in selected:
            try:
                index = self.tree.index(item)
                if 0 <= index < len(self.directory_pairs):
                    self.directory_pairs.pop(index)
                self.tree.delete(item)
            except Exception:
                pass
        self.save_config()

    def edit_pair(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.tr("warn_none_sel_title"),
                self.tr("warn_none_sel_edit"))
            return
        if len(selected) > 1:
            messagebox.showwarning(
                self.tr("warn_multi_sel_title"),
                self.tr("warn_multi_sel_msg"))
            return

        item  = selected[0]
        try:
            index = self.tree.index(item)
        except Exception:
            return
        if index < 0 or index >= len(self.directory_pairs):
            return
        pair = self.directory_pairs[index]

        def on_confirm(src, dst):
            self.directory_pairs[index] = {
                "source": src, "destination": dst, "item": item}
            try:
                self.tree.item(item, values=(src, dst, "0"))
            except Exception:
                pass
            self.save_config()

        self._make_pair_dialog(
            self.tr("dlg_edit_pair"),
            source_val=pair["source"],
            dest_val=pair["destination"],
            on_confirm=on_confirm)

    # ------------------------------------------------------------------
    # Iteração de diretório (compat XP / Win7)
    # ------------------------------------------------------------------
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
        try:
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
        except (IOError, OSError) as e:
            raise e

    def _copiar_par(self, src, dst, item):
        if not os.path.isdir(src):
            self._status(
                self.tr("status_err_src", src), True)
            return 0

        self._status(
            self.tr("status_verifying",
                    os.path.basename(src) or src))
        self._progress(item, 0, "", 0, 0)

        try:
            pendentes = self._scan_pendentes(src, dst)
        except Exception as e:
            self._status(
                self.tr("status_err_backup", str(e)[:60]), True)
            return 0

        total_arqs  = len(pendentes)

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
                t_ui = agora
                self._progress(item, 0, "", copiados, total_arqs)
                self._status(
                    self.tr("status_copying",
                            os.path.basename(src) or src,
                            copiados,
                            total_arqs))

        return copiados

    def start_copy_all(self):
        if self.copying:
            messagebox.showwarning(
                self.tr("warn_in_progress_title"),
                self.tr("warn_in_progress_msg"))
            return
        thread_compat(
            target=self.copiar_todos_optimized, daemon=True).start()

    def copiar_todos_optimized(self, show_message=True):
        if self.copying:
            return
        self.copying   = True
        total_start    = time.time()
        total_copiados = 0
        try:
            for pair in list(self.directory_pairs):
                if not self.copying:
                    break
                src = pair.get("source", "")
                dst = pair.get("destination", "")
                if not src or not dst:
                    continue
                copiados = self._copiar_par(src, dst, pair["item"])
                total_copiados += copiados
                try:
                    self._progress(pair["item"], 0, "",
                                   copiados, copiados)
                except Exception:
                    pass

            elapsed = time.time() - total_start
            now_str = datetime.datetime.now().strftime("%H:%M")
            self.last_backup_date[now_str] = datetime.datetime.now().date()

            self._status(
                self.tr("status_done", total_copiados, elapsed))

            if show_message:
                if total_copiados == 0:
                    self._msginfo(
                        self.tr("info_no_files_title"),
                        self.tr("info_no_files_msg"))
                else:
                    self._msginfo(
                        self.tr("info_done_title"),
                        self.tr("info_done_msg",
                                total_copiados, elapsed))

        except Exception as e:
            self._status(
                self.tr("status_err_backup", str(e)[:60]), True)
            if show_message:
                self._msgerror(
                    self.tr("err_backup_title"),
                    self.tr("err_backup_msg", e))
        finally:
            self.copying = False

    # ------------------------------------------------------------------
    # System Tray
    # ------------------------------------------------------------------
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
        try:
            self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
        except Exception:
            pass

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

        # Captura as strings de menu no momento da criação
        lbl_restore = self.tr("tray_restore")
        lbl_quit    = self.tr("tray_quit")

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
                                    IDM_RESTORE, lbl_restore)
                    u32.AppendMenuW(hmenu, MF_STRING,
                                    IDM_QUIT, lbl_quit)
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
                        ico_path if not PY2 else text_type(ico_path),
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
                if hwnd_box[0]:
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

    # ------------------------------------------------------------------
    # Automação / Autostart
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

    def _get_autostart_cmd(self):
        """
        Retorna a string de comando para o autostart.
        - Executável compilado (frozen): usa sys.executable diretamente.
        - Script .pyw/.py: usa pythonw.exe (sem console) + caminho do script.
        """
        if getattr(sys, 'frozen', False):
            exe = None
            try:
                exe = os.path.abspath(sys.executable)
            except Exception:
                pass
            if not exe:
                exe = _get_real_exe_path()
            if exe:
                return u'"{0}"'.format(exe)
            return None

        script = _get_real_exe_path()
        if not script:
            return None

        python_dir = os.path.dirname(sys.executable)
        for candidate in ("pythonw.exe", "python.exe"):
            pythonw = os.path.join(python_dir, candidate)
            if os.path.isfile(pythonw):
                return u'"{0}" "{1}"'.format(pythonw, script)

        return u'"{0}" "{1}"'.format(sys.executable, script)

    def _get_startup_folder(self):
        """Localiza a pasta Startup do usuário atual (XP, 7, 10, 11)."""
        appdata = _get_appdata_dir()
        if appdata:
            startup = os.path.join(
                appdata,
                r"Microsoft\Windows\Start Menu\Programs\Startup")
            if os.path.isdir(startup):
                return startup

        try:
            if PY2:
                import _winreg as reg
            else:
                import winreg as reg
            key = reg.OpenKey(
                reg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
            try:
                val, _ = reg.QueryValueEx(key, "Startup")
            finally:
                reg.CloseKey(key)
            if val and os.path.isdir(val):
                return val
        except Exception:
            pass
        return None

    def _write_startup_shortcut(self, cmd):
        """
        Cria um arquivo .bat na pasta Startup como fallback ao registro.
        Compatível com Windows XP/7 sem necessidade de COM/WScript.
        """
        startup = self._get_startup_folder()
        if not startup:
            return False
        bat_path = os.path.join(startup, "FerragilBackup.bat")
        try:
            content = u'@echo off\r\nstart "" /B {0}\r\n'.format(cmd)
            with open(bat_path, 'wb') as f:
                f.write(_to_utf8_bytes(content))
            return True
        except Exception as e:
            print("Erro ao criar .bat startup: {0}".format(e))
            return False

    def _remove_startup_shortcut(self):
        """Remove o .bat da pasta Startup se existir."""
        startup = self._get_startup_folder()
        if not startup:
            return
        bat_path = os.path.join(startup, "FerragilBackup.bat")
        try:
            if os.path.isfile(bat_path):
                os.remove(bat_path)
        except Exception as e:
            print("Erro ao remover .bat startup: {0}".format(e))

    def set_autostart(self, enable):
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = u"FerragilBackup"
        cmd      = self._get_autostart_cmd() if enable else None
        reg_ok   = False

        try:
            KEY_WOW64_32KEY = getattr(winreg, 'KEY_WOW64_32KEY', 0x0200)
            access = winreg.KEY_SET_VALUE | KEY_WOW64_32KEY
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, key_path, 0, access)
            except (WindowsError, OSError):
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, key_path, 0,
                    winreg.KEY_SET_VALUE)
            try:
                if enable and cmd:
                    winreg.SetValueEx(key, app_name, 0,
                                      winreg.REG_SZ, cmd)
                    reg_ok = True
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except (WindowsError, OSError):
                        pass
                    reg_ok = True
            finally:
                winreg.CloseKey(key)
        except Exception as e:
            print("Erro ao configurar registro autostart: {0}".format(e))

        if enable:
            if not reg_ok and cmd:
                self._write_startup_shortcut(cmd)
            else:
                self._remove_startup_shortcut()
        else:
            self._remove_startup_shortcut()

    def start_automation(self):
        self.stop_automation.clear()
        thread_compat(target=self._automation_loop, daemon=True).start()
        thread_compat(target=self._backup_on_startup, daemon=True).start()

    def _automation_loop(self):
        last_triggered = {}
        while not self.stop_automation.is_set() and self.running:
            try:
                now              = datetime.datetime.now()
                current_time_str = "{0:02d}:{1:02d}".format(
                    now.hour, now.minute)
                current_date     = now.date()

                if current_time_str in self.scheduled_times:
                    if last_triggered.get(current_time_str) != current_date:
                        last_triggered[current_time_str]        = current_date
                        self.last_backup_date[current_time_str] = current_date
                        if not self.copying:
                            thread_compat(
                                target=self.copiar_todos_optimized,
                                args=(False,), daemon=True).start()

                next_minute   = (now + datetime.timedelta(minutes=1)).replace(
                    second=0, microsecond=0)
                sleep_seconds = max(5, (next_minute - now).total_seconds())
                self.stop_automation.wait(timeout=sleep_seconds)
            except Exception:
                self.stop_automation.wait(timeout=30)

    def _backup_on_startup(self):
        time.sleep(3)
        if self.running and not self.copying:
            self.copiar_todos_optimized(show_message=False)

    # ------------------------------------------------------------------
    # Eventos de janela
    # ------------------------------------------------------------------
    def _on_unmap(self, event):
        try:
            if event.widget is not self.master:
                return
        except Exception:
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


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app  = FileCopierApp(root)
    root.mainloop()
