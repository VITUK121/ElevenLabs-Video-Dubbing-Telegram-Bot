import instaloader
import yt_dlp
import os

class SocialDownloader:
    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Ініціалізація Instaloader
        self.L = instaloader.Instaloader(
            dirname_pattern=download_path,
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False
        )

    def download_instagram(self, url):
        """
        Завантажує пост (фото/відео/карусель) з Instagram.
        Працює для публічних акаунтів.
        """
        try:
            # Отримуємо shortcode з URL (наприклад, з https://www.instagram.com/p/CODE123/)
            shortcode = url.split("/p/")[1].split("/")[0]
            print(f"⏳ Завантаження Instagram поста: {shortcode}...")
            
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            self.L.download_post(post, target=shortcode)
            
            print(f"✅ Успішно завантажено в папку {self.download_path}/{shortcode}")
            return True
        except Exception as e:
            print(f"❌ Помилка Instagram: {e}")
            return False

    def download_tiktok(self, url):
        """
        Завантажує відео з TikTok (намагається без водяного знаку).
        """
        print(f"⏳ Завантаження TikTok відео...")
        
        ydl_opts = {
            'outtmpl': f'{self.download_path}/%(id)s.%(ext)s', # Формат імені файлу
            'format': 'bestvideo+bestaudio/best', # Найкраща якість
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                print(f"✅ Успішно завантажено: {filename}")
                return filename
        except Exception as e:
            print(f"❌ Помилка TikTok: {e}")
            return False

# --- Приклад використання ---
if __name__ == "__main__":
    downloader = SocialDownloader()

    # Приклад для Instagram (вставте реальний лінк на публічний пост)
    # downloader.download_instagram("https://www.instagram.com/p/C-example/")

    # Приклад для TikTok (вставте реальний лінк)
    # downloader.download_tiktok("https://www.tiktok.com/@user/video/1234567890")