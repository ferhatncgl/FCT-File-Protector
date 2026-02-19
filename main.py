import os
import secrets
import zipfile
import tempfile
import threading
import shutil
import webbrowser
import customtkinter as ctk
from tkinter import messagebox, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES

from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# UI Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TkinterDnD_CTk(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class FCTToolPro(TkinterDnD_CTk):
    def __init__(self):
        super().__init__()
        self.title("FCT File Protector")
        self.geometry("550x550") # Biraz daha büyüttüm (uyarılar sığsın diye)
        self.resizable(False, False)
        
        self.keyfile_path = None
        self.setup_ui()

    def setup_ui(self):
        # Header
        self.header_label = ctk.CTkLabel(self, text="FCT File Protector", font=("Roboto", 28, "bold"))
        self.header_label.pack(pady=(20, 10))

        # Password Input
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Enter Master Password...", show="*", width=400, height=40)
        self.pass_entry.pack(pady=10)

        # Options Frame
        self.opt_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.opt_frame.pack(pady=5, fill="x", padx=70)

        # Keyfile Option
        self.use_keyfile_var = ctk.BooleanVar(value=False)
        self.keyfile_cb = ctk.CTkCheckBox(self.opt_frame, text="Use Keyfile (Optional)", variable=self.use_keyfile_var, command=self.toggle_keyfile)
        self.keyfile_cb.pack(anchor="w", pady=5)

        self.keyfile_btn = ctk.CTkButton(self.opt_frame, text="Select Keyfile", state="disabled", fg_color="gray", command=self.select_keyfile)
        self.keyfile_btn.pack(anchor="w", pady=5)

        # Shredding Option & Serious Warning
        self.shred_var = ctk.BooleanVar(value=False)
        self.shred_cb = ctk.CTkCheckBox(self.opt_frame, text="Secure Shred Originals", variable=self.shred_var, text_color="#e74c3c", font=("Roboto", 12, "bold"))
        self.shred_cb.pack(anchor="w", pady=(15, 0))
        
        self.warning_label = ctk.CTkLabel(self.opt_frame, text="WARNING: This action is 100% IRREVERSIBLE!\nDeleted files CANNOT be recovered.", text_color="#c0392b", font=("Roboto", 10, "bold"), justify="left")
        self.warning_label.pack(anchor="w", padx=25, pady=(0, 5))

        # Drag & Drop Zone
        self.dnd_frame = ctk.CTkFrame(self, width=400, height=90, corner_radius=10)
        self.dnd_frame.pack(pady=10)
        self.dnd_frame.pack_propagate(False)
        
        self.dnd_label = ctk.CTkLabel(self.dnd_frame, text="Drag & Drop Folder or .fct File Here", text_color="gray")
        self.dnd_label.place(relx=0.5, rely=0.5, anchor="center")

        self.dnd_frame.drop_target_register(DND_FILES)
        self.dnd_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=5)

        self.enc_btn = ctk.CTkButton(self.btn_frame, text="ENCRYPT FOLDER", fg_color="#27ae60", hover_color="#2ecc71", command=self.manual_encrypt)
        self.enc_btn.grid(row=0, column=0, padx=10)

        self.dec_btn = ctk.CTkButton(self.btn_frame, text="DECRYPT .FCT", fg_color="#2980b9", hover_color="#3498db", command=self.manual_decrypt)
        self.dec_btn.grid(row=0, column=1, padx=10)

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(15, 5))

        self.status_label = ctk.CTkLabel(self, text="Ready.", font=("Roboto", 12))
        self.status_label.pack()

        # GitHub Footer Link
        self.github_link = ctk.CTkLabel(self, text="Developed by @ferhatncgl | GitHub", font=("Roboto", 11, "underline"), text_color="#3498db", cursor="hand2")
        self.github_link.pack(side="bottom", pady=10)
        self.github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/ferhatncgl"))

    def toggle_keyfile(self):
        if self.use_keyfile_var.get():
            self.keyfile_btn.configure(state="normal", fg_color="#8e44ad")
        else:
            self.keyfile_btn.configure(state="disabled", fg_color="gray")
            self.keyfile_path = None
            self.keyfile_btn.configure(text="Select Keyfile")

    def select_keyfile(self):
        path = filedialog.askopenfilename(title="Select Keyfile")
        if path:
            self.keyfile_path = path
            self.keyfile_btn.configure(text=f"...{path[-15:]}")

    def handle_drop(self, event):
        path = event.data.strip('{}')
        if os.path.isdir(path):
            self.start_process("encrypt", path)
        elif path.endswith(".fct"):
            self.start_process("decrypt", path)
        else:
            messagebox.showwarning("Invalid Input", "Please drop a folder to encrypt or a .fct file to decrypt.")

    def manual_encrypt(self):
        folder = filedialog.askdirectory(title="Select Folder to Encrypt")
        if folder: self.start_process("encrypt", folder)

    def manual_decrypt(self):
        file = filedialog.askopenfilename(title="Select .fct File", filetypes=[("FCT Archive", "*.fct")])
        if file: self.start_process("decrypt", file)

    def update_ui(self, text, progress):
        self.after(0, self._update_ui_sync, text, progress)

    def _update_ui_sync(self, text, progress):
        self.status_label.configure(text=text)
        self.progress_bar.set(progress)

    def set_states(self, state):
        mode = "normal" if state else "disabled"
        self.pass_entry.configure(state=mode)
        self.enc_btn.configure(state=mode)
        self.dec_btn.configure(state=mode)

    def secure_shred(self, folder_path):
        self.update_ui("Securely shredding original files...", 0.95)
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                size = os.path.getsize(file_path)
                try:
                    with open(file_path, "ba+", buffering=0) as f:
                        for _ in range(3):
                            f.seek(0)
                            f.write(os.urandom(size))
                    os.remove(file_path)
                except Exception:
                    pass
            for name in dirs:
                try: os.rmdir(os.path.join(root, name))
                except: pass
        try: shutil.rmtree(folder_path)
        except: pass

    def derive_key(self, password: str, salt: bytes) -> bytes:
        keyfile_data = b""
        if self.use_keyfile_var.get() and self.keyfile_path:
            with open(self.keyfile_path, 'rb') as f:
                keyfile_data = f.read(1024 * 1024)
        
        combined_material = password.encode() + keyfile_data
        kdf = Argon2id(salt=salt, length=32, iterations=3, lanes=4, memory_cost=65536)
        return kdf.derive(combined_material)

    def start_process(self, mode, target_path):
        password = self.pass_entry.get()
        if not password:
            messagebox.showerror("Error", "Master Password is required!")
            return
        
        if self.use_keyfile_var.get() and not self.keyfile_path:
            messagebox.showerror("Error", "You checked 'Use Keyfile' but didn't select one!")
            return

        self.set_states(False)
        if mode == "encrypt":
            output = filedialog.asksaveasfilename(defaultextension=".fct", initialfile=os.path.basename(target_path)+".fct")
            if output:
                threading.Thread(target=self._encrypt_routine, args=(target_path, output, password), daemon=True).start()
            else:
                self.set_states(True)
        else:
            output = filedialog.askdirectory(title="Select Extraction Folder")
            if output:
                threading.Thread(target=self._decrypt_routine, args=(target_path, output, password), daemon=True).start()
            else:
                self.set_states(True)

    def _encrypt_routine(self, folder_path, output_file, password):
        temp_zip = None
        try:
            fd, temp_zip = tempfile.mkstemp(suffix=".zip")
            os.close(fd)
            
            all_files = [os.path.join(r, f) for r, d, files in os.walk(folder_path) for f in files]
            total = len(all_files)
            
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for idx, f_path in enumerate(all_files):
                    arc_path = os.path.relpath(f_path, folder_path)
                    self.update_ui(f"Archiving: {arc_path[:30]}...", (idx/total)*0.4)
                    zf.write(f_path, arc_path)

            salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
            key = self.derive_key(password, salt)
            encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()

            file_size = os.path.getsize(temp_zip)
            processed = 0
            
            with open(temp_zip, 'rb') as f_in, open(output_file, 'wb') as f_out:
                f_out.write(salt)
                f_out.write(nonce)
                while chunk := f_in.read(64 * 1024):
                    f_out.write(encryptor.update(chunk))
                    processed += len(chunk)
                    self.update_ui("Encrypting blocks...", 0.4 + ((processed/file_size)*0.5))

                f_out.write(encryptor.finalize())
                f_out.write(encryptor.tag)

            if self.shred_var.get():
                self.secure_shred(folder_path)

            self.update_ui("Encryption Complete!", 1.0)
            messagebox.showinfo("Success", "Folder secured successfully.")

        except Exception as e:
            self.update_ui("Encryption Failed", 0)
            messagebox.showerror("Error", str(e))
        finally:
            if temp_zip and os.path.exists(temp_zip): os.remove(temp_zip)
            self.after(0, lambda: self.set_states(True))

    def _decrypt_routine(self, fct_file, target_dir, password):
        temp_zip = None
        try:
            file_size = os.path.getsize(fct_file)
            fd, temp_zip = tempfile.mkstemp(suffix=".zip")
            os.close(fd)

            with open(fct_file, 'rb') as f_in:
                salt, nonce = f_in.read(16), f_in.read(12)
                f_in.seek(-16, os.SEEK_END)
                tag = f_in.read(16)
                f_in.seek(28)

                key = self.derive_key(password, salt)
                decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()

                enc_size = file_size - 44
                processed = 0

                with open(temp_zip, 'wb') as f_out:
                    while processed < enc_size:
                        chunk = f_in.read(min(64 * 1024, enc_size - processed))
                        f_out.write(decryptor.update(chunk))
                        processed += len(chunk)
                        self.update_ui("Decrypting...", (processed/enc_size)*0.7)
                    decryptor.finalize()

            self.update_ui("Extracting files...", 0.85)
            with zipfile.ZipFile(temp_zip, 'r') as zf:
                zf.extractall(target_dir)

            self.update_ui("Decryption Complete!", 1.0)
            messagebox.showinfo("Success", "Files fully restored.")

        except Exception:
            self.update_ui("Failed! Wrong password or keyfile?", 0)
            messagebox.showerror("Error", "Authentication failed or file is corrupted.")
        finally:
            if temp_zip and os.path.exists(temp_zip): os.remove(temp_zip)
            self.after(0, lambda: self.set_states(True))

if __name__ == "__main__":
    app = FCTToolPro()
    app.mainloop()