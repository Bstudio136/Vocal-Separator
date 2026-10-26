import sys
import subprocess
import shutil
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import threading
import math
import colorsys

# --- AUTO INSTALL DEPENDENCIES ---
def install_if_missing(package, import_name=None):
    try:
        __import__(import_name or package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_missing("customtkinter")
install_if_missing("demucs")

# --- CORRECTIF FORCE SCALING (Windows) ---
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# --- CHECK FFMPEG ---
if not shutil.which("ffmpeg"):
    raise RuntimeError("FFmpeg manquant (obligatoire pour Demucs)")

ctk.set_appearance_mode("Dark")

class DemucsQuantumApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VOCAL SEPARATOR QUANTUM AUDIO CORE // OPERATING SYSTEM v3.4.7")
        self.geometry("720x650")
        self.resizable(False, False)
        
        self.PINK = "#ff007f"
        self.PINK_GLOW = "#ff3399"
        self.DARK_BG = "#020407"
        self.CARD_BG = "#060a12"
        self.GREEN = "#00ff66"
        
        self.configure(fg_color=self.DARK_BG)
        self.file_path = ""
        
        self.author_url = "https://bstudio136.github.io/mylink/"
        
        self.rainbow_hue = 0.0  
        self.pulse_time = 0.0
        
        # ✅ NOUVEAU : Texte avec une icône de lien pour montrer que c'est cliquable
        self.sig_text = "🔗 by Bstudio136 🔗" 
        self.sig_idx = 0
        
        self.blink_state = True
        self.inject_pulse_speed = 0.0
        self.boot_queue = []
        
        # ✅ NOUVEAU : Variable pour savoir si la souris est sur la signature
        self.is_hovering_sig = False 
        
        self.creer_widgets()
        self.sequences_initialisation()

    def creer_widgets(self):
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(25, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, text="⧔ VOCAL SEPARATOR ⧔⧕ NEURAL QUANTUM CORE ⧕", 
            font=ctk.CTkFont(family="Courier", size=26, weight="bold"),
            text_color="#00f0ff"
        )
        self.title_label.pack()

        # ✅ MODIFIÉ : Ajout de underline=True et taille légèrement plus grande
        self.signature_label = ctk.CTkLabel(
            self.header_frame, text="",
            font=ctk.CTkFont(family="Courier", size=14, weight="bold", slant="italic", underline=True),
            text_color="#00f0ff",
            cursor="hand2"  # Curseur main dès le départ
        )
        self.signature_label.pack(pady=(2, 0))

        # ✅ NOUVEAU : Les événements sont liés tout de suite
        self.signature_label.bind("<Button-1>", self.ouvrir_lien_author)
        self.signature_label.bind("<Enter>", self.on_sig_enter)
        self.signature_label.bind("<Leave>", self.on_sig_leave)

        self.file_frame = ctk.CTkFrame(self, fg_color=self.CARD_BG, border_color="#003a3d", border_width=2)
        self.file_frame.pack(pady=10, padx=40, fill="x")
        self.boot_queue.append(self.file_frame)

        self.btn_browse = ctk.CTkButton(
            self.file_frame, text="⚡ INJECT AUDIO", 
            font=ctk.CTkFont(family="Courier", weight="bold", size=14),
            fg_color="transparent", text_color="#00f0ff",
            border_color="#00f0ff", border_width=2,
            hover_color="#002630", command=self.parcourir_fichier
        )
        self.btn_browse.pack(side="left", padx=20, pady=18)

        self.lbl_file = ctk.CTkLabel(
            self.file_frame, text="STATUS :: COLD STANDBY // AWAITING WAVEFORM", 
            font=ctk.CTkFont(family="Courier", size=11, weight="bold"),
            text_color="#4f687a", anchor="w"
        )
        self.lbl_file.pack(side="left", padx=10, pady=18, fill="x", expand=True)

        self.options_frame = ctk.CTkFrame(self, fg_color=self.CARD_BG, border_color="#003a3d", border_width=2)
        self.options_frame.pack(pady=10, padx=40, fill="x")
        self.boot_queue.append(self.options_frame)

        self.lbl_opt_title = ctk.CTkLabel(
            self.options_frame, text="SYNAPSE FORMAT :", 
            font=ctk.CTkFont(family="Courier", size=11, weight="bold"), text_color="white"
        )
        self.lbl_opt_title.pack(side="left", padx=(20, 10), pady=15)

        self.format_var = tk.StringVar(value="MP3")
        for fmt_text, fmt_val in [("COMPRESSED MP3 (320K)", "MP3"), ("RAW QUANTUM WAV", "WAV")]:
            rb = ctk.CTkRadioButton(
                self.options_frame, text=fmt_text, variable=self.format_var, value=fmt_val,
                font=ctk.CTkFont(family="Courier", size=11, weight="bold"), text_color="white", 
                fg_color="#00f0ff", border_color="#00f0ff"
            )
            rb.pack(side="left", padx=20, pady=15)

        self.terminal_wrapper = ctk.CTkFrame(self, fg_color="#010204", border_color="#101824", border_width=1)
        self.terminal_wrapper.pack(pady=10, padx=40, fill="both", expand=True)
        self.boot_queue.append(self.terminal_wrapper)

        self.laser_canvas = tk.Canvas(self.terminal_wrapper, bg="#010204", bd=0, highlightthickness=0, height=6)
        self.laser_canvas.pack(fill="x", padx=2, pady=0)

        self.txt_console = ctk.CTkTextbox(
            self.terminal_wrapper, font=ctk.CTkFont(family="Courier", size=12), 
            fg_color="transparent", text_color=self.GREEN
        )
        self.txt_console.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=20, fill="x", padx=40)
        self.boot_queue.append(self.action_frame)

        self.btn_open = ctk.CTkButton(
            self.action_frame, text="📂 ACCESS SEPARATED CORES", 
            font=ctk.CTkFont(family="Courier", size=11, weight="bold"),
            fg_color="#0e131f", text_color="#536475",
            border_color="#1a2336", border_width=1,
            state="disabled", command=self.ouvrir_dossier_sortie
        )
        self.btn_open.pack(side="left", padx=5, fill="y")

        self.btn_start = ctk.CTkButton(
            self.action_frame, text="⚡ INITIALIZE COGNITIVE EXTRACTION", 
            font=ctk.CTkFont(family="Courier", size=12, weight="bold"),
            fg_color="#14070e", text_color="#4d3340",
            border_color="#24141c", border_width=1,
            state="disabled", command=self.demarrer_traitement_thread
        )
        self.btn_start.pack(side="right", padx=5, fill="y", expand=True)

        for w in self.boot_queue:
            w.pack_forget()

    def sequences_initialisation(self):
        self.log_message_quantum("INITIALIZING CORE OS IN SEAMLESS RGB SPECTRUM...")
        self.after(300, lambda: self.boot_sequentiel(0))
        self.pulse_engine()
        self.laser_scanner_engine()
        self.blink_action_engine()
        self.inject_glow_engine()

    def boot_sequentiel(self, idx):
        if idx < len(self.boot_queue):
            if idx == 2:
                self.boot_queue[idx].pack(pady=10, padx=40, fill="both", expand=True)
            elif idx == 3:
                self.boot_queue[idx].pack(pady=20, fill="x", padx=40)
            else:
                self.boot_queue[idx].pack(pady=10, padx=40, fill="x")
            self.after(120, lambda: self.boot_sequentiel(idx + 1))
        else:
            self.after(100, self.typewriter_signature)

    def pulse_engine(self):
        self.rainbow_hue += 0.005
        if self.rainbow_hue > 1.0:
            self.rainbow_hue = 0.0

        rgb = colorsys.hsv_to_rgb(self.rainbow_hue, 1.0, 1.0)
        hex_rainbow = f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"
        
        rgb_dim = colorsys.hsv_to_rgb(self.rainbow_hue, 1.0, 0.4)
        hex_rainbow_dim = f"#{int(rgb_dim[0]*255):02x}{int(rgb_dim[1]*255):02x}{int(rgb_dim[2]*255):02x}"

        try:
            self.title_label.configure(text_color=hex_rainbow)
            
            # ✅ MODIFIÉ : L'animation arc-en-ciel s'arrête si la souris est sur la signature
            if not self.is_hovering_sig:
                self.signature_label.configure(text_color=hex_rainbow)
                
            self.file_frame.configure(border_color=hex_rainbow_dim)
            self.options_frame.configure(border_color=hex_rainbow_dim)
            
            if not self.file_path:
                self.lbl_opt_title.configure(text_color=hex_rainbow)
        except: 
            pass
            
        self.after(30, self.pulse_engine)

    # ✅ NOUVEAU : Effet visuel quand la souris passe sur la signature
    def on_sig_enter(self, event=None):
        self.is_hovering_sig = True
        self.signature_label.configure(text_color="#ffffff") # Blanc pur

    # ✅ NOUVEAU : Reprise de l'animation quand la souris s'en va
    def on_sig_leave(self, event=None):
        self.is_hovering_sig = False

    def inject_glow_engine(self):
        try:
            if not self.file_path:
                self.inject_pulse_speed += 0.25
                glow_factor = (math.sin(self.inject_pulse_speed) + 1) / 2
                bright_cyan = int(100 + (155 * glow_factor))
                
                hex_glow_cyan = f"#00{bright_cyan:02x}{bright_cyan:02x}"
                hex_bg_glow = f"#00{int(40 * glow_factor):02x}{int(50 * glow_factor):02x}"
                
                self.btn_browse.configure(
                    text_color=hex_glow_cyan,
                    border_color=hex_glow_cyan,
                    fg_color=hex_bg_glow,
                    border_width=2
                )
        except:
            pass
        
        self.after(60, self.inject_glow_engine)

    def blink_action_engine(self):
        try:
            if self.file_path and self.btn_start.cget("state") != "disabled":
                self.blink_state = not self.blink_state
                if self.blink_state:
                    self.btn_start.configure(
                        fg_color=self.PINK,
                        text_color="white",
                        border_color=self.PINK_GLOW,
                        border_width=2
                    )
                else:
                    self.btn_start.configure(
                        fg_color="#4d0026", 
                        text_color="#ff80bf",
                        border_color="#33001a",
                        border_width=1
                    )
            elif self.file_path and self.btn_start.cget("text") == "PROCESSING SYNAPSES...":
                self.btn_start.configure(
                    fg_color="#99004d",
                    text_color="white",
                    border_width=0
                )
            else:
                self.btn_start.configure(
                    fg_color="#14070e",
                    text_color="#4d3340",
                    border_color="#24141c",
                    border_width=1,
                    state="disabled"
                )
        except:
            pass
            
        self.after(400, self.blink_action_engine)

    def laser_scanner_engine(self):
        self.laser_canvas.delete("all")
        self.pulse_time += 0.02
        
        laser_glow = int(190 + 65 * ((math.sin(self.pulse_time * 2.5) + 1) / 2))
        laser_color = f"#ff00{laser_glow:02x}"
        
        width = self.laser_canvas.winfo_width()
        self.laser_canvas.create_line(0, 3, width, 3, fill=laser_color, width=3)
        
        self.after(25, self.laser_scanner_engine)

    def ouvrir_lien_author(self, event=None):
        if self.author_url:
            webbrowser.open_new(self.author_url)

    def typewriter_signature(self):
        if self.sig_idx < len(self.sig_text):
            self.signature_label.configure(text=self.sig_text[:self.sig_idx+1])
            self.sig_idx += 1
            self.after(90, self.typewriter_signature)
        else:
            self.log_message_quantum("SECURITY SIGNATURE VERIFIED // AUTHOR: BSTUDIO136")
            self.log_message_quantum("AWAITING WAVEFORM INJECTION. LOOK AT THE FLASHING INJECTOR.")

    def log_message_quantum(self, msg, type_log="INFO"):
        prefix = "⚡ " if type_log == "INFO" else "🚨 "
        if type_log == "SUCCESS": prefix = "✔ "
        
        self.txt_console.configure(state="normal")
        self.txt_console.insert("end", f"{prefix}{msg}\n")
        self.txt_console.see("end")
        self.txt_console.configure(state="disabled")

    def verifier_dependances(self):
        manquant = []
        if not shutil.which("ffmpeg"): manquant.append("FFmpeg Neural Encoder")
        try:
            import demucs
        except ImportError:
            manquant.append("Cognitive Core (Demucs package)")

        if manquant:
            for item in manquant:
                self.log_message_quantum(f"CRITICAL FAULT: {item} IS ABSENT", type_log="ERROR")
            messagebox.showerror("CRITICAL CORE FAULT", "Composants IA introuvables.")
            return False
        return True

    def parcourir_fichier(self):
        if not self.verifier_dependances(): return
        path = filedialog.askopenfilename(filetypes=[("Quantum Audio", "*.mp3 *.wav *.flac *.ogg")])
        if path:
            self.file_path = path
            filename = os.path.basename(path).upper()
            if len(filename) > 35: filename = filename[:32] + "..."
                
            self.lbl_file.configure(text=f"CONNECTED // TARGET CORE: {filename}", text_color="#00f0ff")
            
            self.btn_browse.configure(
                text_color=self.GREEN, 
                border_color=self.GREEN, 
                fg_color="transparent"
            )
            
            self.log_message_quantum(f"AUDIO SOURCE INJECTED. QUANTUM STROBE GENERATED ON PROCESSOR.", type_log="SUCCESS")
            self.btn_start.configure(state="normal")

    def demarrer_traitement_thread(self):
        threading.Thread(target=self.executer_demucs_quantum, daemon=True).start()

    def executer_demucs_quantum(self):
        self.btn_start.configure(state="disabled", text="PROCESSING SYNAPSES...")
        self.btn_browse.configure(state="disabled")
        self.log_message_quantum("ENGAGING AI PIPELINE CORE...", type_log="INFO")
        
        cmd = [sys.executable, "-m", "demucs"]
        if self.format_var.get() == "MP3":
            cmd.extend(["--mp3", "--mp3-bitrate", "320"])
        cmd.append(self.file_path)

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                l = line.strip()
                if any(x in l for x in ["Selected", "Separating", "Writing"]):
                    self.log_message_quantum(f"[AI PIPELINE] {l}")
            
            proc.wait()
            if proc.returncode == 0:
                self.log_message_quantum("▲ MATRIX COMPLETED. EXTRACTED CORES GENERATED.", type_log="SUCCESS")
                self.btn_open.configure(state="normal", text_color="white")
                messagebox.showinfo("QUANTUM EXTRACTED", "La séparation cognitive est achevée.")
                self.file_path = ""
                self.lbl_file.configure(text="STATUS :: COLD STANDBY // AWAITING WAVEFORM", text_color="#4f687a")
            else:
                self.log_message_quantum("▲ CRITICAL FAULT ENCOUNTERED BY COGNITIVE ENGINE.", type_log="ERROR")
        except Exception as e:
            self.log_message_quantum(f"UNHANDLED SYSTEM EXCEPTION: {e}", type_log="ERROR")
        finally:
            self.btn_browse.configure(state="normal")
            self.btn_start.configure(text="⚡ INITIALIZE COGNITIVE EXTRACTION")
            if self.file_path:
                self.btn_start.configure(state="normal")
            else:
                self.btn_start.configure(state="disabled")

    def ouvrir_dossier_sortie(self):
        d = os.path.join(os.getcwd(), "separated")
        if os.path.exists(d):
            os.startfile(d) if sys.platform == "win32" else subprocess.run(["open", d])
        else:
            self.log_message_quantum("DIRECTORY ERROR: OUTPUT CORES ROOT NOT FOUND", type_log="ERROR")

if __name__ == "__main__":
    app = DemucsQuantumApp()
    app.mainloop()