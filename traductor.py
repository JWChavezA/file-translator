import os
from pathlib import Path
from langdetect import detect
from googletrans import Translator
from pdfminer.high_level import extract_text
from docx import Document

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from plyer import notification
from collections import defaultdict

################################################################################
# Requisitos:
# 1) pip install googletrans==4.0.0-rc1 langdetect pdfminer.six python-docx plyer
# 2) Al fallar un archivo: no mostrar ventana de error, reintentar 3 veces y si falla -> omitir.
# 3) Mostrar botón Cancelar bajo la barra de progreso para cortar todo el proceso.
# 4) Al final, listar los archivos no traducidos en una ventana.
################################################################################

# ======================
# CONFIGURACIÓN / GLOBAL
# ======================
MAX_RETRIES = 3                 # Máximo de intentos por archivo
end_process = False             # Se pondrá True si se pulsa "Cancelar"
untranslated_files = []         # Archivos que fallaron tras 3 intentos
fallback_lang = None            # Idioma fallback si no se detecta
fallback_enabled = False        # True si el usuario decidió usar fallback para todos
current_ui_lang = "ES"          # Idioma actual de la interfaz
base_folder = None              # Se definirá según la ruta de entrada

ui_translations = {
    "ES": {
        "app_title": "Traductor de Archivos (Googletrans)",
        "lbl_input_folder": "Carpeta de entrada:",
        "lbl_output_folder": "Carpeta de salida:",
        "lbl_source_lang": "Idioma de origen (opcional):",
        "lbl_dest_lang": "Idioma de destino:",
        "lbl_select": "Seleccionar",
        "btn_start": "Iniciar Traducción",
        "btn_cancel": "Cancelar Traducción",
        "progress_title": "Progreso de traducción",
        "progress_label": "Traduciendo archivos...",
        "info_no_files": "Sin archivos",
        "msg_no_files_found": "No se encontraron archivos .txt, .pdf o .docx",
        "err_title": "Error",
        "err_input_folder": "La carpeta de entrada no es válida",
        "err_output_folder": "Seleccione una carpeta de salida",
        "err_dest_lang": "Seleccione un idioma de destino",
        "err_invalid_input": "Ruta de entrada no válida",
        "notify_file_translated": "Archivo traducido correctamente.",
        "notify_all_translated": "Todos los archivos han sido traducidos correctamente.",
        "notify_title_done": "Traducción Completada",
        "dlg_no_detect_title": "Idioma no detectado",
        "dlg_no_detect_msg": "No se pudo detectar el idioma. Selecciona manualmente:",
        "dlg_no_detect_chk": "Usar este idioma para todos los archivos sin detectar",
        "btn_ok": "Aceptar",
        "btn_cancel_dialog": "Cancelar",
        "final_report_title": "Archivos no traducidos",
        "final_report_msg": "Los siguientes archivos no se tradujeron:"
    },
    "EN": {
        "app_title": "File Translator (Googletrans)",
        "lbl_input_folder": "Input folder:",
        "lbl_output_folder": "Output folder:",
        "lbl_source_lang": "Source language (optional):",
        "lbl_dest_lang": "Target language:",
        "lbl_select": "Select",
        "btn_start": "Start Translation",
        "btn_cancel": "Cancel Translation",
        "progress_title": "Translation Progress",
        "progress_label": "Translating files...",
        "info_no_files": "No files",
        "msg_no_files_found": "No .txt, .pdf or .docx found.",
        "err_title": "Error",
        "err_input_folder": "Input folder is invalid.",
        "err_output_folder": "Please select an output folder.",
        "err_dest_lang": "Please select a target language.",
        "err_invalid_input": "Invalid input path.",
        "notify_file_translated": "File translated successfully.",
        "notify_all_translated": "All files have been translated successfully.",
        "notify_title_done": "Translation Completed",
        "dlg_no_detect_title": "Language not detected",
        "dlg_no_detect_msg": "Could not detect language. Select manually:",
        "dlg_no_detect_chk": "Use this language for all non-detectable files.",
        "btn_ok": "OK",
        "btn_cancel_dialog": "Cancel",
        "final_report_title": "Untranslated files",
        "final_report_msg": "These files could not be translated:"
    }
    # Agrega más idiomas de interfaz si necesitas
}

ui_langs = ["ES", "EN"]  # Idiomas de la interfaz
languages = ["auto", "EN", "ES", "FR", "DE", "IT", "RU", "ZH", "ar"]


# ======================
# FUNCIONES DE INTERFAZ
# ======================
def get_ui_text(key):
    return ui_translations.get(current_ui_lang, {}).get(key, key)

def set_app_language(lang_code):
    global current_ui_lang
    current_ui_lang = lang_code
    root.title(get_ui_text("app_title"))
    lbl_input_folder.config(text=get_ui_text("lbl_input_folder"))
    btn_select_input.config(text=get_ui_text("lbl_select"))
    lbl_output_folder.config(text=get_ui_text("lbl_output_folder"))
    btn_select_output.config(text=get_ui_text("lbl_select"))
    lbl_src_lang.config(text=get_ui_text("lbl_source_lang"))
    lbl_dest_lang.config(text=get_ui_text("lbl_dest_lang"))
    btn_start_translation.config(text=get_ui_text("btn_start"))
    ui_lang_label.config(text=get_ui_text("app_title"))

def detect_langdetect(text):
    """Intenta detectar el idioma con langdetect, si falla retorna None."""
    try:
        return detect(text)
    except:
        return None

def ask_fallback_lang_dialog():
    """Si no se detecta idioma y no hay fallback, pregunta qué usar."""
    dialog = tk.Toplevel()
    dialog.title(get_ui_text("dlg_no_detect_title"))

    tk.Label(dialog, text=get_ui_text("dlg_no_detect_msg")).pack(pady=5)

    choice_var = tk.StringVar(value="EN")
    use_for_all_var = tk.BooleanVar(value=False)

    combo = ttk.Combobox(dialog, textvariable=choice_var, values=languages, state="readonly")
    combo.set("EN")
    combo.pack(pady=5)

    chk = tk.Checkbutton(dialog, text=get_ui_text("dlg_no_detect_chk"), variable=use_for_all_var)
    chk.pack(pady=5)

    result = {"lang": None, "use_for_all": False}

    def on_ok():
        result["lang"] = choice_var.get()
        result["use_for_all"] = use_for_all_var.get()
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    frame_btn = tk.Frame(dialog)
    frame_btn.pack()

    tk.Button(frame_btn, text=get_ui_text("btn_ok"), command=on_ok, width=10).pack(side="left", padx=5, pady=10)
    tk.Button(frame_btn, text=get_ui_text("btn_cancel_dialog"), command=on_cancel, width=10).pack(side="left", padx=5, pady=10)

    dialog.grab_set()
    dialog.wait_window()
    return result["lang"], result["use_for_all"]

def get_real_source_lang(text, user_src):
    """Determina el idioma real de origen (si user_src es auto, intentamos)."""
    global fallback_lang, fallback_enabled

    if user_src.lower() != "auto":
        return user_src

    detected = detect_langdetect(text)
    if detected:
        return detected
    else:
        if fallback_enabled and fallback_lang:
            return fallback_lang
        chosen, use_for_all = ask_fallback_lang_dialog()
        if chosen:
            if use_for_all:
                fallback_lang = chosen
                fallback_enabled = True
            return chosen
        else:
            return None


# ===============
# TRADUCCIÓN
# ===============
def attempt_translation(text, src_lang, dest_lang):
    """1 intento de traducción con googletrans (sin mostrar ventana de error).  
       Retorna el texto traducido o None si falla."""
    translator = Translator()
    real_src = get_real_source_lang(text, src_lang)
    if not real_src:
        # No se pudo determinar (o usuario canceló fallback)
        return None
    try:
        result = translator.translate(text, src=real_src.lower(), dest=dest_lang.lower())
        return result.text
    except Exception as e:
        # Manejo silencioso: no mostramos pop-up, solo se registra en consola
        print(f"ERROR: No se pudo traducir (intento fallido): {e}")
        return None

def read_text_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_pdf_file(path):
    return extract_text(path)

def save_text_file(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def save_docx_file(path, doc, dest_lang):
    for para in doc.paragraphs:
        if para.text.strip():
            new_text = attempt_translation(para.text, "auto", dest_lang)
            if new_text:
                para.text = new_text
    doc.save(path)

def process_file(file_path, out_path, src_lang, dest_lang):
    """Procesa un archivo en hasta MAX_RETRIES intentos silenciosos.
       Retorna True si se tradujo, False si no se logró."""
    ext = file_path.suffix.lower()
    # Salida manteniendo estructura
    rel = file_path.relative_to(base_folder)
    final_path = out_path / rel
    final_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if ext == ".txt":
                text = read_text_file(file_path)
                if not text.strip():
                    return True  # archivo vacío, se considera éxito
                translated = attempt_translation(text, src_lang, dest_lang)
                if translated:
                    save_text_file(final_path, translated)
                    return True
            elif ext == ".pdf":
                text = read_pdf_file(file_path)
                if not text.strip():
                    return True
                translated = attempt_translation(text, src_lang, dest_lang)
                if translated:
                    save_text_file(final_path.with_suffix(".txt"), translated)
                    return True
            elif ext == ".docx":
                doc = Document(file_path)
                save_docx_file(final_path, doc, dest_lang)
                return True  # Si no hubo error, consideramos éxito
            else:
                # Si es otro tipo, lo consideramos éxito sin traducir
                return True
        except Exception as e:
            print(f"ERROR: (intento {attempt}/{MAX_RETRIES}) para {file_path} -> {e}")

    # Si llega aquí, fallaron los 3 intentos
    return False

def cancel_translation():
    global end_process
    end_process = True
    if progress_window and progress_window.winfo_exists():
        progress_window.destroy()

def show_untranslated_report():
    if not untranslated_files:
        return
    dlg = tk.Toplevel()
    dlg.title(get_ui_text("final_report_title"))

    tk.Label(dlg, text=get_ui_text("final_report_msg")).pack(pady=5)

    lb = tk.Listbox(dlg, width=80, height=8)
    lb.pack(padx=10, pady=5)
    for f in untranslated_files:
        lb.insert(tk.END, f)

    tk.Button(dlg, text=get_ui_text("btn_ok"), command=dlg.destroy).pack(pady=10)
    dlg.grab_set()

def run_translation_process(all_files, out_path, src_lang, dest_lang):
    """Corre la traducción de forma asíncrona, con barra de progreso y botón Cancelar."""
    global end_process
    end_process = False
    untranslated_files.clear()

    total = len(all_files)
    progress_var.set(0)
    count = 0

    for file_path in all_files:
        if end_process:
            break
        success = process_file(file_path, out_path, src_lang, dest_lang)
        count += 1
        if not success:
            # No se pudo traducir tras 3 intentos
            untranslated_files.append(str(file_path))

        # Actualizar progreso
        perc = (count / total) * 100
        progress_var.set(perc)
        progress_window.update_idletasks()

    # Cerrar la ventana de progreso si sigue abierta
    if progress_window.winfo_exists():
        progress_window.destroy()

    if not end_process:
        # Notificar
        notification.notify(
            title=get_ui_text("notify_title_done"),
            message=get_ui_text("notify_all_translated"),
            timeout=5
        )
        # Mostrar reporte de no traducidos
        show_untranslated_report()

def process_folder(in_path, out_path, src_lang, dest_lang):
    # Recolectar archivos relevantes
    files_to_translate = []
    for root_, _, fs in os.walk(in_path):
        for f in fs:
            fp = Path(root_) / f
            if fp.suffix.lower() in [".txt", ".pdf", ".docx"]:
                files_to_translate.append(fp)

    if not files_to_translate:
        messagebox.showinfo(get_ui_text("info_no_files"), get_ui_text("msg_no_files_found"))
        return

    # Crear ventana de progreso (global)
    global progress_window
    progress_window = tk.Toplevel()
    progress_window.title(get_ui_text("progress_title"))

    tk.Label(progress_window, text=get_ui_text("progress_label")).pack(padx=10, pady=10)
    bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    bar.pack(padx=10, pady=10)

    btn_cancel = tk.Button(progress_window, text=get_ui_text("btn_cancel"), command=cancel_translation)
    btn_cancel.pack(pady=5)

    # Iniciar traducción asíncrona
    root.after(100, lambda: run_translation_process(files_to_translate, out_path, src_lang, dest_lang))
    progress_window.transient(root)
    progress_window.grab_set()

def process_single_file(in_path, out_path, src_lang, dest_lang):
    global end_process
    end_process = False
    untranslated_files.clear()

    # Crear ventana de progreso
    global progress_window
    progress_window = tk.Toplevel()
    progress_window.title(get_ui_text("progress_title"))

    tk.Label(progress_window, text=get_ui_text("progress_label")).pack(padx=10, pady=10)
    bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", variable=progress_var)
    bar.pack(padx=10, pady=10)

    btn_cancel = tk.Button(progress_window, text=get_ui_text("btn_cancel"), command=cancel_translation)
    btn_cancel.pack(pady=5)

    def run_single():
        success = process_file(in_path, out_path, src_lang, dest_lang)
        progress_var.set(100)
        progress_window.update_idletasks()
        if progress_window.winfo_exists():
            progress_window.destroy()

        if not success:
            untranslated_files.append(str(in_path))

        if not end_process:
            notification.notify(
                title=get_ui_text("notify_title_done"),
                message=get_ui_text("notify_file_translated"),
                timeout=5
            )
            show_untranslated_report()

    root.after(100, run_single)
    progress_window.transient(root)
    progress_window.grab_set()

def start_translation():
    in_path = Path(input_var.get())
    out_path = Path(output_var.get())
    s_lang = source_lang_var.get()
    d_lang = dest_lang_var.get()

    if not in_path.exists():
        messagebox.showerror(get_ui_text("err_title"), get_ui_text("err_input_folder"))
        return
    if not out_path:
        messagebox.showerror(get_ui_text("err_title"), get_ui_text("err_output_folder"))
        return
    if not d_lang:
        messagebox.showerror(get_ui_text("err_title"), get_ui_text("err_dest_lang"))
        return

    out_path.mkdir(parents=True, exist_ok=True)

    global base_folder
    base_folder = in_path if in_path.is_dir() else in_path.parent

    if in_path.is_file():
        process_single_file(in_path, out_path, s_lang, d_lang)
    elif in_path.is_dir():
        process_folder(in_path, out_path, s_lang, d_lang)
    else:
        messagebox.showerror(get_ui_text("err_title"), get_ui_text("err_invalid_input"))

# ======================
# VENTANA PRINCIPAL
# ======================
root = tk.Tk()
root.title(get_ui_text("app_title"))

ui_lang_label = tk.Label(root, text=get_ui_text("app_title"))
ui_lang_label.grid(row=0, column=0)

ui_lang_var = tk.StringVar()
ui_lang_combo = ttk.Combobox(root, textvariable=ui_lang_var, values=ui_langs, state="readonly")
ui_lang_combo.grid(row=0, column=1)

def on_ui_lang_change(*_):
    new_lang = ui_lang_var.get()
    set_app_language(new_lang)

ui_lang_combo.bind("<<ComboboxSelected>>", on_ui_lang_change)
ui_lang_combo.set("ES")

input_var = tk.StringVar()
output_var = tk.StringVar()
source_lang_var = tk.StringVar()
dest_lang_var = tk.StringVar()

lbl_input_folder = tk.Label(root, text=get_ui_text("lbl_input_folder"))
lbl_input_folder.grid(row=1, column=0)

entry_input = tk.Entry(root, textvariable=input_var, width=50)
entry_input.grid(row=1, column=1)
btn_select_input = tk.Button(root, text=get_ui_text("lbl_select"), command=lambda: input_var.set(filedialog.askdirectory()))
btn_select_input.grid(row=1, column=2)

lbl_output_folder = tk.Label(root, text=get_ui_text("lbl_output_folder"))
lbl_output_folder.grid(row=2, column=0)

entry_output = tk.Entry(root, textvariable=output_var, width=50)
entry_output.grid(row=2, column=1)
btn_select_output = tk.Button(root, text=get_ui_text("lbl_select"), command=lambda: output_var.set(filedialog.askdirectory()))
btn_select_output.grid(row=2, column=2)

lbl_src_lang = tk.Label(root, text=get_ui_text("lbl_source_lang"))
lbl_src_lang.grid(row=3, column=0)

cmb_src_lang = ttk.Combobox(root, textvariable=source_lang_var, values=languages, state="readonly")
cmb_src_lang.grid(row=3, column=1)
cmb_src_lang.set("auto")

lbl_dest_lang = tk.Label(root, text=get_ui_text("lbl_dest_lang"))
lbl_dest_lang.grid(row=4, column=0)

cmb_dest_lang = ttk.Combobox(root, textvariable=dest_lang_var, values=languages, state="readonly")
cmb_dest_lang.grid(row=4, column=1)
cmb_dest_lang.set("ES")

btn_start_translation = tk.Button(root, text=get_ui_text("btn_start"), command=start_translation)
btn_start_translation.grid(row=5, column=1)

# Variable de progreso
progress_var = tk.DoubleVar(value=0)
progress_window = None  # Será asignado cuando abramos la ventana de progreso

root.mainloop()
