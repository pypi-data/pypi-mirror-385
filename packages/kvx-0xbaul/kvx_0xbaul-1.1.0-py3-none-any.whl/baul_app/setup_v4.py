#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import base64
import hashlib
from typing import Dict, Optional, Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import customtkinter as ctk
from tkinter import messagebox

# Apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Constantes
HARDCODED_HASHES = {
    "7d99c95b72d2c17d06d01a44aafe636c4b9dc8ea542c38f13d3b265e6002fdbc",
    "dcd019294f04d39a2cb867b54849986b449b5d55e828bafac38e87c027cbceb6"
}

BAUL_DIR = os.path.join(os.path.dirname(__file__), "baul")
KEY_SIZE, IV_SIZE, AES_BLOCK = 32, 16, 16

# ---- Utilidades criptográficas y de FS ----
def cred_hash(u: str, p: str) -> str:
    return hashlib.sha256(f"{u}:{p}".encode()).hexdigest()

def decode_key_iv_from_b64(b64str: str) -> Tuple[bytes, bytes]:
    import base64 as _b64
    raw = _b64.urlsafe_b64decode(b64str)
    if len(raw) != KEY_SIZE + IV_SIZE:
        raise ValueError("Longitud inválida: se esperaban 48 bytes")
    return raw[:KEY_SIZE], raw[KEY_SIZE:]

def decrypt_bytes_to_text(ciphertext: bytes, key: bytes, iv: bytes) -> str:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ciphertext), AES_BLOCK)
    try:
        return pt.decode("utf-8", errors="replace")
    except Exception:
        return pt.hex()

def decrypt_bytes_raw(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ciphertext), AES_BLOCK)
    return pt

def list_dir_recursive(base_dir: str, rel_path: str = "") -> Tuple[list[str], list[str]]:
    abs_path = os.path.join(base_dir, rel_path)
    dirs, files = [], []
    for entry in os.listdir(abs_path):
        full = os.path.join(abs_path, entry)
        if os.path.isdir(full):
            dirs.append(entry)
        else:
            files.append(entry)
    dirs.sort(), files.sort()
    return dirs, files

# ---- Aplicación ----
class BaulApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("0xbaul -")
        self.geometry("600x400")
        self.minsize(600, 400)
        self.configure(fg_color="#1a1a1a")

        # Estado global
        self.key: Optional[bytes] = None
        self.iv: Optional[bytes] = None
        self.cache: Dict[str, str] = {}

        # Login inicial
        self.login_frame = LoginFrame(self, self.on_login)
        self.login_frame.pack(fill="both", expand=True)

    def on_login(self, user: str):
        self.geometry("1250x720")
        self.minsize(1250, 720)
        self.login_frame.pack_forget()
        self.main_frame = MainFrame(self, user)
        self.main_frame.pack(fill="both", expand=True)

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent: 'BaulApp', on_ok):
        super().__init__(parent, fg_color="#1a1a1a")
        self.parent = parent
        self.on_ok = on_ok

        frame = ctk.CTkFrame(self, fg_color="#202020", corner_radius=12)
        frame.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(frame, text="0xBAUL LOGIN", font=("Consolas", 18, "bold"), text_color="white").pack(pady=(15, 20))

        self.user = ctk.CTkEntry(frame, placeholder_text="Usuario", width=250, height=30, font=("Consolas", 12))
        self.user.pack(pady=5)
        self.pwd = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=250, height=30, font=("Consolas", 12))
        self.pwd.pack(pady=5)

        ctk.CTkButton(
            frame, text="Iniciar sesión", width=140, height=32, font=("Consolas", 12, "bold"),
            fg_color="#303030", hover_color="#444", text_color="white",
            corner_radius=8, command=self.try_login
        ).pack(pady=(18, 15))

    def try_login(self):
        u, p = self.user.get().strip(), self.pwd.get()
        h = cred_hash(u, p)
        if h in HARDCODED_HASHES:
            self.on_ok(u)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o no autorizadas")

class MainFrame(ctk.CTkFrame):
    def __init__(self, parent: 'BaulApp', user: str):
        super().__init__(parent, fg_color="#1a1a1a")
        self.parent = parent
        self.current_path = ""
        self.active_key_type = None
        self.selected_folder = None  # carpeta seleccionada para extraer

        # Mapa de botones por carpeta para resaltar sin redibujar
        self.folder_buttons: Dict[str, ctk.CTkButton] = {}

        # HEADER
        header = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=0)
        header.pack(fill="x", side="top")
        ctk.CTkLabel(header, text=f"0xBAUL - {user}",
                     font=("Consolas", 16, "bold"), text_color="white").pack(side="left", padx=15, pady=10)
        ctk.CTkButton(header, text="Cerrar sesión", width=120,
                      fg_color="#3a3a3a", hover_color="#555",
                      command=self.logout).pack(side="right", padx=10, pady=10)

        # BODY
        body = ctk.CTkFrame(self, fg_color="#1a1a1a")
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        # PANEL IZQUIERDO
        left = ctk.CTkScrollableFrame(body, fg_color="#2b2b2b", label_text="Explorador de archivos")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.left_panel = left

        self.path_label = ctk.CTkLabel(left, text="/", text_color="white", font=("Consolas", 12))
        self.path_label.pack(pady=4)
        self.refresh_button = ctk.CTkButton(left, text="Refrescar",
                                            fg_color="#3a3a3a", hover_color="#555",
                                            width=100, command=self.refresh_files)
        self.refresh_button.pack(pady=5)
        self.file_container = ctk.CTkFrame(left, fg_color="#2b2b2b")
        self.file_container.pack(fill="both", expand=True, pady=5)

        # PANEL DERECHO
        right = ctk.CTkFrame(body, fg_color="#2b2b2b")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(5, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # CAMPOS DE LLAVES
        ctk.CTkLabel(right, text="Llave:", text_color="white").grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        self.entry_key = ctk.CTkEntry(right, placeholder_text="Pega la llave maestra aquí", width=450)
        self.entry_key.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        ctk.CTkLabel(right, text="Llave ADM:", text_color="white").grid(row=2, column=0, sticky="w", padx=10, pady=(5, 0))
        self.entry_key_adm = ctk.CTkEntry(right, placeholder_text="Pega la llave ADM aquí", width=450)
        self.entry_key_adm.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="w")

        # BOTONES
        btns = ctk.CTkFrame(right, fg_color="#2b2b2b")
        btns.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkButton(btns, text="Validar", fg_color="#3a3a3a", hover_color="#555", width=100,
                      command=self.validate_key).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Descifrar TODO", fg_color="#3a3a3a", hover_color="#555", width=140,
                      command=self.decrypt_all_mem).pack(side="left", padx=5)
        ctk.CTkButton(btns, text="Extraer", fg_color="#3a3a3a", hover_color="#666", width=120,
                      command=self.extract_selected).pack(side="left", padx=5)

        # TEXTBOX LOG
        self.text_area = ctk.CTkTextbox(right, wrap="none", text_color="white", fg_color="#1f1f1f")
        self.text_area.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)

        self.refresh_files()

    # ---------------- VALIDAR LLAVES ----------------
    def validate_key(self):
        key_master = self.entry_key.get().strip()
        key_adm = self.entry_key_adm.get().strip()

        if key_master and key_adm:
            messagebox.showwarning("Error", "Solo puedes validar UNA llave a la vez (maestra o ADM).")
            return
        if not key_master and not key_adm:
            messagebox.showwarning("Falta llave", "Introduce una llave Base64 (normal o ADM).")
            return

        try:
            if key_master:
                key, iv = decode_key_iv_from_b64(key_master)
                self.parent.key, self.parent.iv = key, iv
                self.active_key_type = "MASTER"
                messagebox.showinfo("Llave OK", "Llave MAESTRA validada correctamente.")
            else:
                key, iv = decode_key_iv_from_b64(key_adm)
                self.parent.key, self.parent.iv = key, iv
                self.active_key_type = "ADM"
                messagebox.showinfo("Llave OK", "Llave ADM validada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Clave inválida: {e}")

    # ---------------- DESCIFRADO GLOBAL ----------------
    def decrypt_all_mem(self):
        import threading

        if not self.parent.key or not self.parent.iv:
            messagebox.showwarning("Llave requerida", "Valida primero una llave.")
            return
        if not self.active_key_type:
            messagebox.showwarning("Sin llave activa", "Debes validar una llave antes de descifrar.")
            return

        console = ctk.CTkToplevel(self)
        console.title("Descifrado en tiempo real")
        console.geometry("800x500")
        console.configure(fg_color="#101010")
        console.lift()
        console.focus_force()
        console.attributes('-topmost', True)

        txt = ctk.CTkTextbox(console, wrap="none", text_color="white", fg_color="#101010")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

        stop_flag = threading.Event()

        def log(msg: str):
            txt.insert("end", f"{msg}\n")
            txt.see("end")
            console.update_idletasks()

        def do_decrypt():
            count_ok = 0
            for root, _, files in os.walk(BAUL_DIR):
                if stop_flag.is_set():
                    log("\n[INTERRUPCION] Descifrado cancelado por el usuario.")
                    return

                root_upper = root.upper()
                if self.active_key_type == "MASTER" and "ADM" in root_upper:
                    continue
                if self.active_key_type == "ADM" and "ADM" not in root_upper:
                    continue

                for fname in files:
                    rel = os.path.relpath(os.path.join(root, fname), BAUL_DIR).replace("\\", "/")
                    if rel in self.parent.cache:
                        continue
                    try:
                        with open(os.path.join(root, fname), "rb") as f:
                            data = f.read()
                        plaintext = decrypt_bytes_to_text(data, self.parent.key, self.parent.iv)
                        self.parent.cache[rel] = plaintext
                        count_ok += 1
                        log(f"[OK] Descifrado: {rel}")
                    except Exception as e:
                        self.parent.cache[rel] = f"[ERROR DESCIFRANDO] {e}"
                        log(f"[FAIL] {rel} -> {e}")

            log(f"\n--- Descifrado completado ({count_ok} archivos) ---")
            self.refresh_files()
            console.after(1500, console.destroy)

        def stop_process():
            stop_flag.set()
            log("[INTENTO DE CANCELACION]")

        ctk.CTkButton(console, text="Cancelar", fg_color="#660000",
                      hover_color="#990000", command=stop_process).pack(side="bottom", pady=8)

        threading.Thread(target=do_decrypt, daemon=True).start()

    # ---------------- EXTRAER A ARCHIVOS ----------------
    def extract_selected(self):
        if not self.selected_folder:
            messagebox.showwarning("Sin selección", "Selecciona primero una carpeta con un clic.")
            return
        if not self.parent.key or not self.parent.iv:
            messagebox.showwarning("Llave requerida", "Valida una llave antes de extraer.")
            return

        src = os.path.join(BAUL_DIR, self.selected_folder)
        dst_root = os.path.join("decrypt-archivos", self.selected_folder)
        os.makedirs(dst_root, exist_ok=True)

        for root, _, files in os.walk(src):
            rel = os.path.relpath(root, src)
            dst_dir = os.path.join(dst_root, rel)
            os.makedirs(dst_dir, exist_ok=True)
            for fname in files:
                src_file = os.path.join(root, fname)

                # --- Quitar extensión .FSEC al exportar ---
                base_name, ext = os.path.splitext(fname)
                out_name = base_name if ext.lower() == ".fsec" else fname
                dst_file = os.path.join(dst_dir, out_name)

                try:
                    with open(src_file, "rb") as f:
                        data = f.read()
                    dec = decrypt_bytes_raw(data, self.parent.key, self.parent.iv)
                    with open(dst_file, "wb") as f:
                        f.write(dec)
                    self.log(f"[EXTRAÍDO] {dst_file}")
                except Exception as e:
                    self.log(f"[ERROR EXTRAER] {fname}: {e}")

        messagebox.showinfo("Extracción completada", f"Archivos guardados en: decrypt-archivos/{self.selected_folder}")

    # ---------------- INTERFAZ Y UTILIDADES ----------------
    def log(self, msg: str):
        self.text_area.insert("end", f"{msg}\n")
        self.text_area.see("end")

    def _apply_folder_styles(self, abs_folder: str, selected: bool):
        """Actualiza estilos del botón de carpeta sin redibujar toda la lista."""
        btn = self.folder_buttons.get(abs_folder)
        if not btn:
            return
        fg = "#4a4a4a" if selected else "#2f2f2f"
        tc = "#ffff99" if selected else "#5daeff"
        try:
            btn.configure(fg_color=fg, text_color=tc)
        except Exception:
            # fallback por si el botón fue destruido entre refresh
            pass

    def refresh_files(self):
        # Vaciar mapa y contenedor
        self.folder_buttons.clear()
        for w in self.file_container.winfo_children():
            w.destroy()

        self.path_label.configure(text=f"/{self.current_path or ''}")
        base = os.path.join(BAUL_DIR, self.current_path)
        os.makedirs(base, exist_ok=True)
        dirs, files = list_dir_recursive(BAUL_DIR, self.current_path)

        if self.current_path:
            ctk.CTkButton(self.file_container, text="Volver", fg_color="#3a3a3a",
                          hover_color="#555", command=self.go_up,
                          width=120).pack(pady=3)

        # --- Directorios ---
        for d in dirs:
            abs_folder = os.path.join(self.current_path, d)
            is_selected = (self.selected_folder == abs_folder)

            btn = ctk.CTkButton(self.file_container,
                                text=f"[{d}]",
                                fg_color="#4a4a4a" if is_selected else "#2f2f2f",
                                hover_color="#4a4a4a",
                                text_color="#ffff99" if is_selected else "#5daeff",
                                width=300,
                                anchor="w")
            btn.bind("<Button-1>", lambda e, x=abs_folder: self.select_folder_inplace(x))
            btn.bind("<Double-Button-1>", lambda e, x=d: self.open_folder(x))
            btn.pack(fill="x", pady=2, padx=(6, 0))

            self.folder_buttons[abs_folder] = btn

        # --- Archivos ---
        for f in files:
            rel = os.path.join(self.current_path, f).replace("\\", "/")
            base_color = "#FFD700" if "ADM" in self.current_path.upper() else "#ff5555"
            display_name = f
            if rel in self.parent.cache:
                base_color = "#8aff80"
                display_name = f + "  → descifrado"

            ctk.CTkButton(self.file_container, text=display_name,
                          fg_color="#2f2f2f", hover_color="#4a4a4a",
                          text_color=base_color, anchor="w",
                          command=lambda x=rel: self.show_file_content(x)
                          ).pack(fill="x", pady=2)

    def select_folder_inplace(self, abs_folder: str):
        """Marca visualmente la carpeta seleccionada sin redibujar (sin lag)."""
        # Quitar selección previa
        if self.selected_folder and self.selected_folder != abs_folder:
            self._apply_folder_styles(self.selected_folder, selected=False)
        # Marcar nueva
        self.selected_folder = abs_folder
        self._apply_folder_styles(abs_folder, selected=True)

    def open_folder(self, folder: str):
        self.current_path = os.path.join(self.current_path, folder)
        self.selected_folder = None
        self.refresh_files()

    def go_up(self):
        if self.current_path:
            self.current_path = os.path.dirname(self.current_path)
            self.selected_folder = None
            self.refresh_files()

    def show_file_content(self, rel_path: str):
        content = self.parent.cache.get(rel_path, "(No descifrado o error)")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)

    def logout(self):
        self.destroy()
        if hasattr(self.parent, "main_frame"):
            del self.parent.main_frame
        self.parent.key = None
        self.parent.iv = None
        self.parent.cache.clear()
        self.parent.geometry("600x400")
        self.parent.minsize(600, 400)
        self.parent.login_frame = LoginFrame(self.parent, self.parent.on_login)
        self.parent.login_frame.pack(fill="both", expand=True)


def main():
    try:
        os.makedirs(BAUL_DIR, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] No se pudo crear/asegurar el directorio '{BAUL_DIR}': {e}")
        sys.exit(1)

    app = BaulApp()
    try:
        app.mainloop()
    except Exception as e:
        print(f"[ERROR] Loop principal terminado por excepción: {e}")
        raise

if __name__ == "__main__":
    main()
