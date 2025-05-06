import yt_dlp
import os
import random
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    ]
    return random.choice(user_agents)

def download_audio(url, output_path=None):
    try:
        # Menentukan path output
        if output_path is None:
            output_path = os.path.join(os.getcwd(), "audio_downloads")
        
        # Membuat folder jika belum ada
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Konfigurasi yt-dlp untuk audio
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: print_progress(d)],
            'quiet': False,
            'no_warnings': False,
            'http_headers': {
                'User-Agent': get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'socket_timeout': 30,
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 10,
            'ignoreerrors': False,
            'no_check_certificate': True,
            'geo_bypass': True,
            'geo_verification_proxy': None,
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'verbose': True,
        }
        
        # Mengunduh audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nMengambil informasi audio...")
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Tidak dapat mendapatkan informasi audio")
                
                print("\nInformasi Audio:")
                print(f"Judul: {info.get('title', 'Tidak tersedia')}")
                print(f"Durasi: {info.get('duration', 'Tidak tersedia')} detik")
                print(f"Views: {info.get('view_count', 'Tidak tersedia'):,}")
                
                print("\nMengunduh audio...")
                time.sleep(2)
                ydl.download([url])
                print(f"\nAudio berhasil diunduh ke: {output_path}")
                return True, "Audio berhasil diunduh"
            except Exception as e:
                print(f"\nError saat mengunduh: {str(e)}")
                print("\nTips troubleshooting:")
                print("1. Periksa koneksi internet Anda")
                print("2. Pastikan URL video valid dan dapat diakses")
                print("3. Coba gunakan URL video yang berbeda")
                print("4. Pastikan video tidak memiliki pembatasan usia")
                print("5. Coba gunakan VPN jika video dibatasi di wilayah Anda")
                print("6. Tunggu beberapa saat dan coba lagi")
                print("7. Pastikan Anda tidak mengunduh terlalu banyak audio dalam waktu singkat")
                print("8. Coba buka video di browser terlebih dahulu untuk memastikan tidak ada pembatasan")
                print("9. Pastikan Anda menggunakan versi terbaru dari yt-dlp")
                print("10. Coba hapus folder 'audio_downloads' dan buat ulang")
                return False, str(e)
    except Exception as e:
        print(f"\nTerjadi kesalahan: {str(e)}")
        return False, str(e)

def print_progress(d):
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif 'total_bytes_estimate' in d:
            percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
        else:
            percent = 0
        socketio.emit('progress', {'percent': percent})
    elif d['status'] == 'finished':
        print("\nUnduhan selesai!")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL tidak ditemukan'})
    
    success, message = download_audio(url)
    return jsonify({'success': success, 'error': message if not success else None})

if __name__ == "__main__":
    print("=== YouTube Audio Downloader Web ===")
    print("Server berjalan di http://localhost:5000")
    socketio.run(app, debug=True) 