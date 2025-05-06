import yt_dlp
import os
import random
import time

def get_random_user_agent():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
    ]
    return random.choice(user_agents)

def download_video(url, output_path=None):
    try:
        # Menentukan path output
        if output_path is None:
            output_path = os.path.join(os.getcwd(), "downloads")
        
        # Membuat folder jika belum ada
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Konfigurasi yt-dlp tanpa cookiesfrombrowser
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
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
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
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
            'merge_output_format': 'mp4',
        }
        
        # Mengunduh video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\nMengambil informasi video...")
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Tidak dapat mendapatkan informasi video")
                
                print("\nInformasi Video:")
                print(f"Judul: {info.get('title', 'Tidak tersedia')}")
                print(f"Durasi: {info.get('duration', 'Tidak tersedia')} detik")
                print(f"Views: {info.get('view_count', 'Tidak tersedia'):,}")
                
                print("\nMengunduh video...")
                time.sleep(2)
                try:
                    ydl.download([url])
                except Exception as e:
                    print(f"\nError saat mengunduh dengan format pertama: {str(e)}")
                    print("\nMencoba format alternatif...")
                    ydl_opts['format'] = 'best'
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                        ydl2.download([url])
                print(f"\nVideo berhasil diunduh ke: {output_path}")
            except Exception as e:
                print(f"\nError saat mengunduh: {str(e)}")
                print("\nMencoba metode alternatif...")
                ydl_opts['format'] = 'best'
                ydl_opts['merge_output_format'] = None
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    ydl2.download([url])
                print(f"\nVideo berhasil diunduh ke: {output_path}")
    except Exception as e:
        print(f"\nTerjadi kesalahan: {str(e)}")
        print("\nTips troubleshooting:")
        print("1. Periksa koneksi internet Anda")
        print("2. Pastikan URL video valid dan dapat diakses")
        print("3. Coba gunakan URL video yang berbeda")
        print("4. Pastikan video tidak memiliki pembatasan usia")
        print("5. Coba gunakan VPN jika video dibatasi di wilayah Anda")
        print("6. Tunggu beberapa saat dan coba lagi")
        print("7. Pastikan Anda tidak mengunduh terlalu banyak video dalam waktu singkat")
        print("8. Coba buka video di browser terlebih dahulu untuk memastikan tidak ada pembatasan")
        print("9. Pastikan Anda menggunakan versi terbaru dari yt-dlp")
        print("10. Coba hapus folder 'downloads' dan buat ulang")

def print_progress(d):
    if d['status'] == 'downloading':
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
        elif 'total_bytes_estimate' in d:
            percent = d['downloaded_bytes'] / d['total_bytes_estimate'] * 100
        else:
            percent = 0
        print(f"\rMengunduh: {percent:.1f}%", end='', flush=True)
    elif d['status'] == 'finished':
        print("\nUnduhan selesai!")

if __name__ == "__main__":
    print("=== YouTube Video Downloader ===")
    print("Program ini akan mengunduh video YouTube ke folder 'downloads'")
    while True:
        try:
            video_url = input("\nMasukkan URL video YouTube (ketik 'q' untuk keluar): ")
            if video_url.lower() == 'q':
                print("Program selesai.")
                break
            download_video(video_url)
        except KeyboardInterrupt:
            print("\nProgram dihentikan oleh pengguna.")
            break
        except Exception as e:
            print(f"\nTerjadi kesalahan tak terduga: {str(e)}")
            continue 