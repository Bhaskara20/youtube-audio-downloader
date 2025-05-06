import tkinter as tk
from tkinter import ttk, messagebox
import threading
import yt_dlp
import os
import random

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    ]
    return random.choice(user_agents)

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("450x220")
        self.root.resizable(False, False)

        self.url_label = tk.Label(root, text="Masukkan URL YouTube:")
        self.url_label.pack(pady=(20, 5))
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        self.download_btn = tk.Button(root, text="Download", command=self.start_download)
        self.download_btn.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate")
        self.progress.pack(pady=5)

        self.status_label = tk.Label(root, text="Status: Menunggu input...", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(5, 0))

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Peringatan", "URL tidak boleh kosong!")
            return
        self.download_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Mengunduh...")
        self.progress['value'] = 0
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        output_path = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [self.yt_progress_hook],
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': get_random_user_agent(),
            },
            'merge_output_format': 'mp4',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.config(text=f"Status: Selesai! File ada di folder 'downloads'")
            messagebox.showinfo("Sukses", "Video berhasil diunduh!")
        except Exception as e:
            self.status_label.config(text=f"Status: Gagal mengunduh!")
            messagebox.showerror("Error", f"Terjadi kesalahan:\n{str(e)}")
        finally:
            self.download_btn.config(state=tk.NORMAL)
            self.progress['value'] = 0

    def yt_progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            elif 'total_bytes_estimate' in d:
                percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
            else:
                percent = 0
            self.progress['value'] = percent
            self.status_label.config(text=f"Status: Mengunduh... {percent:.1f}%")
        elif d['status'] == 'finished':
            self.progress['value'] = 100
            self.status_label.config(text="Status: Unduhan selesai!")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop() 