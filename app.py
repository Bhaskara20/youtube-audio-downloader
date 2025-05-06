from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import yt_dlp
import os
import random
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
AUDIO_FOLDER = os.path.join(os.getcwd(), 'audio_downloads')

# Membuat folder jika belum ada
for folder in [DOWNLOAD_FOLDER, AUDIO_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    ]
    return random.choice(user_agents)

def download_video(url, sid):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: yt_progress_hook(d, sid)],
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': get_random_user_agent(),
        },
        'merge_output_format': 'mp4',
    }
    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        socketio.emit('download_complete', {'filename': os.path.basename(filename), 'type': 'video'}, room=sid)
    except Exception as e:
        socketio.emit('download_error', {'error': str(e)}, room=sid)

def download_audio(url, sid):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': os.path.join(AUDIO_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [lambda d: yt_progress_hook(d, sid)],
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': get_random_user_agent(),
        },
    }
    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        socketio.emit('download_complete', {'filename': os.path.basename(filename), 'type': 'audio'}, room=sid)
    except Exception as e:
        socketio.emit('download_error', {'error': str(e)}, room=sid)

def yt_progress_hook(d, sid):
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif 'total_bytes_estimate' in d:
            percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
        else:
            percent = 0
        socketio.emit('progress', {'percent': percent}, room=sid)
    elif d['status'] == 'finished':
        socketio.emit('progress', {'percent': 100}, room=sid)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    sid = request.form.get('sid')
    download_type = request.form.get('type', 'video')
    
    if not url or not sid:
        return jsonify({'error': 'URL atau SID tidak ditemukan'}), 400
    
    if download_type == 'audio':
        threading.Thread(target=download_audio, args=(url, sid), daemon=True).start()
    else:
        threading.Thread(target=download_video, args=(url, sid), daemon=True).start()
    
    return jsonify({'status': 'started'})

@app.route('/downloads/<filename>')
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False) 