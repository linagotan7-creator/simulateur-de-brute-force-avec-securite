import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os
import hashlib
import random

from security import SecuritySystem

# ================= CONFIG =================

DEV_SECRET_HASH = "e7d3685715939842749cc27b38d0ccb9706d4d14a5304ef9eee093780eab5df9"  # hacker
ROSALIE_SECRET = "rosalie"  # caché via normalisation

security = SecuritySystem(max_attempts=5, lock_time=5)
dev_mode = False
pin_set = False

# ================= GUI INIT =================

root = tk.Tk()
root.title("Secure System Simulator")
root.geometry("650x500")
root.resizable(False, False)

# ================= UTILS =================

def sha(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()

def normalize(value: str) -> str:
    return value.strip().lower()

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

# ================= 💖 ROSALIE FULLSCREEN =================

def rosalie_animation():
    overlay = tk.Canvas(root, bg="black", highlightthickness=0)
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    hearts = []
    for _ in range(40):
        hearts.append(
            overlay.create_text(
                random.randint(0, 650),
                random.randint(-400, 0),
                text="♥",
                fill="#ff69b4",
                font=("Arial", random.randint(16, 30), "bold")
            )
        )

    def animate():
        for h in hearts:
            overlay.move(h, 0, random.randint(2, 6))
        root.after(40, animate)

    animate()
    root.after(12000, overlay.destroy)

# ================= 💣 BOOM =================

def boom_animation():
    overlay = tk.Frame(root, bg="black")
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    bar = ttk.Progressbar(overlay, length=400, mode="determinate")
    bar.place(relx=0.5, rely=0.45, anchor="center")

    label = tk.Label(overlay, text="BOOM", fg="red", bg="black", font=("Arial Black", 10))

    def fill(v=0):
        if v <= 100:
            bar["value"] = v
            root.after(25, fill, v + 2)
        else:
            explode()

    def explode(size=10):
        label.place(relx=0.5, rely=0.5, anchor="center")
        if size < 80:
            label.config(font=("Arial Black", size))
            root.after(30, explode, size + 5)
        else:
            root.after(3000, overlay.destroy)

    fill()

# ================= ACTIONS =================

def save_code():
    global dev_mode, pin_set
    raw = entry.get()
    value = normalize(raw)

    # 💖 ROSALIE — INTERCEPTÉE AVANT TOUT
    if value == ROSALIE_SECRET:
        rosalie_animation()
        return

    # 💣 BOOM
    if value == "67":
        boom_animation()
        return

    # 🥚 DEV MODE
    if sha(value) == DEV_SECRET_HASH:
        dev_mode = True
        security.enable_test_mode()
        mode_label.config(text="👤 MODE TEST ACTIF", bg="#2ecc71", fg="white")
        quit_btn.pack(pady=5)
        log("🧪 Mode test activé")
        return

    # 🔐 PIN NORMAL
    if not value.isdigit() or len(value) != 3:
        messagebox.showerror("Erreur", "Code invalide (000–999)")
        return

    security.set_pin(value)
    pin_set = True
    log("🔐 Code PIN enregistré")
    messagebox.showinfo("Succès", "Code enregistré")

def quit_test():
    global dev_mode
    dev_mode = False
    mode_label.config(text="")
    quit_btn.pack_forget()
    log("🔒 Mode test désactivé")

def brute_force():
    if not pin_set:
        messagebox.showerror("Erreur", "Veuillez enregistrer un code d'abord")
        return

    log("🚀 Brute force lancé")

    while True:
        code = security.next_code(test_mode=dev_mode)
        result = security.try_code(code, test_mode=dev_mode)
        log(f"🔎 Tentative : {code}")
        time.sleep(0.3)

        if result == "SUCCESS":
            log("✅ Code correct")
            break
        if result in ("LOCK", "LOCKED"):
            log("⏳ Verrouillage temporaire")
            break

def start_bruteforce():
    threading.Thread(target=brute_force, daemon=True).start()

# ================= UI =================

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Code secret (000–999)", font=("Segoe UI", 12, "bold")).pack(anchor="w")
entry = ttk.Entry(frame, font=("Segoe UI", 12))
entry.pack(fill="x", pady=5)

btns = ttk.Frame(frame)
btns.pack(pady=10)

ttk.Button(btns, text="Enregistrer le code", command=save_code).pack(side="left", padx=5)
ttk.Button(btns, text="Lancer la simulation", command=start_bruteforce).pack(side="left", padx=5)

mode_label = tk.Label(frame, font=("Segoe UI", 11, "bold"))
mode_label.pack(fill="x", pady=5)

quit_btn = tk.Button(frame, text="Quitter le mode test", bg="#e74c3c", fg="white", command=quit_test)

ttk.Label(frame, text="Logs système", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(15, 5))
log_box = tk.Text(frame, height=10)
log_box.pack(fill="both", expand=True)

root.mainloop()
