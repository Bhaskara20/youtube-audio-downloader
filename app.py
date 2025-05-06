from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import yt_dlp
import os
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
        if output_path is None:
            output_path = os.path.join(os.getcwd(), "audio_downloads")
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
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
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("Tidak dapat mendapatkan informasi audio")
            
            ydl.download([url])
            return True, "Audio berhasil diunduh"
            
    except Exception as e:
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
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port) 