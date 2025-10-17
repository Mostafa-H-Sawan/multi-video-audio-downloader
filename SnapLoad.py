import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess

try:
    import yt_dlp
except ImportError:
    print("❌ Required library not installed!")
    print("🔧 Running automatic installation...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print("✅ yt-dlp installed successfully!")
        import yt_dlp
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        print("📝 Please install the library manually:")
        print("   pip install yt-dlp")
        sys.exit(1)

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional YouTube Downloader")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")
        
        self.url_var = tk.StringVar()
        self.download_path = tk.StringVar(value=os.getcwd())
        self.download_type = tk.StringVar(value="video")
        self.video_quality = tk.StringVar(value="best")
        self.audio_quality = tk.StringVar(value="0")
        self.is_downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎬 Professional YouTube Downloader", 
                              font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame, text="Download videos and audio in high quality", 
                                 font=("Arial", 12), fg="#ecf0f1", bg="#2c3e50")
        subtitle_label.pack(expand=True)
        
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        url_frame = tk.LabelFrame(main_frame, text="🔗 Video URL", font=("Arial", 12, "bold"), 
                                 bg="#f0f0f0", padx=10, pady=10)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(url_frame, text="Enter YouTube URL:", font=("Arial", 10), 
                bg="#f0f0f0").pack(anchor=tk.W)
        
        url_entry = tk.Entry(url_frame, textvariable=self.url_var, font=("Arial", 11), 
                            width=70, relief=tk.SOLID, bd=1)
        url_entry.pack(fill=tk.X, pady=(5, 0))
        
        info_button = tk.Button(url_frame, text="📋 Get Video Info", 
                               command=self.get_video_info, font=("Arial", 10),
                               bg="#3498db", fg="white", relief=tk.FLAT, padx=15, pady=5)
        info_button.pack(pady=(10, 5))
        
        self.info_text = scrolledtext.ScrolledText(main_frame, height=8, font=("Consolas", 9),
                                                  relief=tk.SOLID, bd=1, wrap=tk.WORD)
        self.info_text.pack(fill=tk.X, pady=(0, 10))
        self.info_text.config(state=tk.DISABLED)
        
        settings_frame = tk.LabelFrame(main_frame, text="⚙️ Download Settings", 
                                      font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        type_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        type_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(type_frame, text="Download Type:", font=("Arial", 10), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        
        video_radio = tk.Radiobutton(type_frame, text="🎥 Video", variable=self.download_type, 
                                    value="video", command=self.on_type_change, bg="#f0f0f0")
        video_radio.pack(side=tk.LEFT, padx=(20, 10))
        
        audio_radio = tk.Radiobutton(type_frame, text="🎵 Audio (MP3)", variable=self.download_type, 
                                    value="audio", command=self.on_type_change, bg="#f0f0f0")
        audio_radio.pack(side=tk.LEFT)
        
        quality_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        quality_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(quality_frame, text="Quality:", font=("Arial", 10), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        
        self.video_quality_combo = ttk.Combobox(quality_frame, textvariable=self.video_quality, 
                                               values=["best", "1080p", "720p", "480p", "360p", "240p", "144p", "worst"],
                                               state="readonly", width=15)
        self.video_quality_combo.pack(side=tk.LEFT, padx=(20, 0))
        
        self.audio_quality_combo = ttk.Combobox(quality_frame, textvariable=self.audio_quality,
                                               values=["0 (Best)", "256", "192", "128", "96"],
                                               state="readonly", width=15)
        self.audio_quality_combo.pack(side=tk.LEFT, padx=(20, 0))
        self.audio_quality_combo.pack_forget() 
        
        path_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        path_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(path_frame, text="Download Folder:", font=("Arial", 10), 
                bg="#f0f0f0").pack(side=tk.LEFT)
        
        path_entry = tk.Entry(path_frame, textvariable=self.download_path, font=("Arial", 10), 
                             width=50, relief=tk.SOLID, bd=1)
        path_entry.pack(side=tk.LEFT, padx=(20, 10), fill=tk.X, expand=True)
        
        browse_button = tk.Button(path_frame, text="📁 Browse", command=self.browse_folder,
                                 font=("Arial", 9), bg="#95a5a6", fg="white", relief=tk.FLAT)
        browse_button.pack(side=tk.RIGHT)
        
        progress_frame = tk.LabelFrame(main_frame, text="📊 Download Progress", 
                                      font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(progress_frame, text="Ready to download", 
                                    font=("Arial", 10), bg="#f0f0f0", fg="#7f8c8d")
        self.status_label.pack(anchor=tk.W)
        
        self.details_label = tk.Label(progress_frame, text="", font=("Arial", 9), 
                                     bg="#f0f0f0", fg="#95a5a6")
        self.details_label.pack(anchor=tk.W)
        
        self.download_button = tk.Button(main_frame, text="🚀 Start Download", 
                                        command=self.start_download, font=("Arial", 12, "bold"),
                                        bg="#27ae60", fg="white", relief=tk.FLAT, padx=30, pady=10)
        self.download_button.pack(pady=10)
        
        self.on_type_change()
        
    def on_type_change(self):
        if self.download_type.get() == "video":
            self.video_quality_combo.pack(side=tk.LEFT, padx=(20, 0))
            self.audio_quality_combo.pack_forget()
        else:
            self.video_quality_combo.pack_forget()
            self.audio_quality_combo.pack(side=tk.LEFT, padx=(20, 0))
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)
    
    def get_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
            return
        
        threading.Thread(target=self._get_video_info_thread, args=(url,), daemon=True).start()
    
    def _get_video_info_thread(self, url):
        self.update_status("Fetching video information...", "#f39c12")
        
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                
                info_text = f"{'='*50}\n"
                info_text += f"📹 Title: {info.get('title', 'Unknown')}\n"
                info_text += f"📺 Channel: {info.get('uploader', 'Unknown')}\n"
                info_text += f"⏱️  Duration: {self.format_duration(info.get('duration', 0))}\n"
                
                view_count = info.get('view_count')
                if view_count:
                    info_text += f"👁️  Views: {view_count:,}\n"
                else:
                    info_text += "👁️  Views: Unknown\n"
                    
                upload_date = info.get('upload_date', '')
                if upload_date:
                    formatted_date = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}"
                    info_text += f"📅 Upload Date: {formatted_date}\n"
                
                formats = info.get('formats', [])
                available_qualities = set()
                for fmt in formats:
                    if fmt.get('height'):
                        available_qualities.add(f"{fmt.get('height')}p")
                
                if available_qualities:
                    sorted_qualities = sorted(list(available_qualities), key=lambda x: int(x[:-1]), reverse=True)
                    info_text += f"🎥 Available Qualities: {', '.join(sorted_qualities)}\n"
                
                info_text += f"{'='*50}\n"
                
                self.root.after(0, self.display_video_info, info_text)
                self.root.after(0, lambda: self.update_status("Video information loaded successfully!", "#27ae60"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get video info: {str(e)}"))
            self.root.after(0, lambda: self.update_status("Failed to get video information", "#e74c3c"))
    
    def display_video_info(self, info_text):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state=tk.DISABLED)
    
    def format_duration(self, seconds):
        if not seconds:
            return "Unknown"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def start_download(self):
        if self.is_downloading:
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL!")
            return
        
        if not os.path.exists(self.download_path.get()):
            messagebox.showerror("Error", "Download folder does not exist!")
            return
        
        self.is_downloading = True
        self.download_button.config(state=tk.DISABLED, text="⏳ Downloading...", bg="#f39c12")
        self.progress_bar.start()
        
        threading.Thread(target=self._download_thread, args=(url,), daemon=True).start()
    
    def _download_thread(self, url):
        try:
            if self.download_type.get() == "video":
                quality_format = self.get_video_format()
                success = self.download_video(url, quality_format, self.download_path.get())
            else:
                quality = self.audio_quality.get().split()[0]  
                success = self.download_audio(url, quality, self.download_path.get())
            
            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success", "Download completed successfully!"))
                self.root.after(0, lambda: self.update_status("Download completed successfully!", "#27ae60"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Download failed!"))
                self.root.after(0, lambda: self.update_status("Download failed", "#e74c3c"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
            self.root.after(0, lambda: self.update_status(f"Download failed: {str(e)}", "#e74c3c"))
        
        finally:
            self.root.after(0, self.download_completed)
    
    def get_video_format(self):
        quality_map = {
            "best": "best",
            "1080p": "best[height<=1080]",
            "720p": "best[height<=720]",
            "480p": "best[height<=480]",
            "360p": "best[height<=360]",
            "240p": "best[height<=240]",
            "144p": "best[height<=144]",
            "worst": "worst"
        }
        return quality_map.get(self.video_quality.get(), "best")
    
    def download_video(self, url, quality_format, download_path):
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', 'N/A').strip()
                speed = d.get('_speed_str', 'N/A').strip()
                eta = d.get('_eta_str', 'N/A').strip()
                self.root.after(0, self.update_progress, percent, speed, eta)
            elif d['status'] == 'finished':
                self.root.after(0, lambda: self.update_details(f"Download finished: {os.path.basename(d['filename'])}"))
        
        try:
            ydl_opts = {
                'format': quality_format,
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [progress_hook],
            }
            
            self.root.after(0, lambda: self.update_status("Starting video download...", "#3498db"))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                return True
                
        except Exception as e:
            self.root.after(0, lambda: self.update_details(f"Error: {str(e)}"))
            return False
    
    def download_audio(self, url, quality, download_path):
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', 'N/A').strip()
                speed = d.get('_speed_str', 'N/A').strip()
                eta = d.get('_eta_str', 'N/A').strip()
                self.root.after(0, self.update_progress, percent, speed, eta)
            elif d['status'] == 'finished':
                self.root.after(0, lambda: self.update_details("Download finished, converting to MP3..."))
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                'progress_hooks': [progress_hook],
            }
            
            self.root.after(0, lambda: self.update_status("Starting audio download and conversion...", "#3498db"))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                return True
                
        except Exception as e:
            self.root.after(0, lambda: self.update_details(f"Error: {str(e)}"))
            if "ffmpeg" in str(e).lower():
                self.root.after(0, lambda: self.update_details("Note: Audio conversion requires FFmpeg to be installed."))
            return False
    
    def update_status(self, message, color="#7f8c8d"):
        self.status_label.config(text=message, fg=color)
    
    def update_details(self, message):
        self.details_label.config(text=message)
    
    def update_progress(self, percent, speed, eta):
        self.update_status(f"Downloading... {percent}", "#3498db")
        self.update_details(f"Speed: {speed} | ETA: {eta}")
    
    def download_completed(self):
        self.is_downloading = False
        self.download_button.config(state=tk.NORMAL, text="🚀 Start Download", bg="#27ae60")
        self.progress_bar.stop()
        self.update_details("")

def main():
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()