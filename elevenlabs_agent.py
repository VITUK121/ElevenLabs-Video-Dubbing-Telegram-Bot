from elevenlabs.core.api_error import ApiError
from elevenlabs.client import AsyncElevenLabs
from time import time
from asyncio import sleep
import aiofiles
from os import path

class Dubbing:
    def __init__(self, api_keys: list, save_folder: str):
        self.api_keys = api_keys
        self.save_folder = save_folder
        self.api_key_index = 0

        self.client = AsyncElevenLabs(api_key=self.api_keys[self.api_key_index])

    def _switch_client(self):
        self.api_key_index += 1
        if self.api_key_index >= len(self.api_keys):
            return False
        
        new_key = self.api_keys[self.api_key_index]
        print(f"🔄 Перемикаємось на наступний API ключ (індекс {self.api_key_index})...")
        self.client = AsyncElevenLabs(api_key=new_key)
        return True

    async def start_dubbing(self, file_path):
        dubbing_id = None
        
        # Trying to make a dub
        while True:
            try:
                with open(file_path, "rb") as f:
                    print(f"🚀 Спроба створити даббінг з ключем №{self.api_key_index}...")
                    response = await self.client.dubbing.create(
                        file=f,
                        name=f"Dub_{int(time())}",
                        source_lang="ja",
                        target_lang="uk",
                        watermark=True
                    )
                    dubbing_id = response.dubbing_id
                    print(f"✅ Завдання створено! ID: {dubbing_id}")
                    break

            except ApiError as e:
                print(f"⚠️ API Error Code: {e.status_code}")
                print(f"⚠️ Error Body: {e.body}")

                if e.status_code in [400, 401, 429, 402]: 
                    print("📉 Недостатньо кредитів або ліміт запитів. Міняємо ключ...")
                    
                    if not self._switch_client():
                        print("❌ Всі ключі перебрано. Фініш.")
                        return None
                else:
                    print(f"❌ Критична помилка, зміна ключа не допоможе: {e}")
                    return None
                    
            except Exception as e:
                print(f"❌ Невідома помилка системи: {e}")
                return None

        # Polling
        if not dubbing_id:
            return None
        
        waited_seconds = 0
        timeout = 600 # 10 min. max

        while waited_seconds < timeout:
            try:
                project = await self.client.dubbing.get(dubbing_id)
                
                if project.status == "dubbed":
                    print(f"🎉 Готово! Статус: {project.status}")
                    break
                elif project.status == "failed":
                    error_msg = getattr(project, 'error_message', 'Unknown error')
                    print(f"💀 Помилка ElevenLabs: {error_msg}")
                    return None
                
                print(f"⏳ {dubbing_id} обробляється... ({waited_seconds}s)")
                await sleep(5)
                waited_seconds += 5
                
            except Exception as e:
                print(f"⚠️ Помилка перевірки статусу: {e}")
                await sleep(5)
                waited_seconds += 5

        # Downloading result
        try:
            audio_stream = self.client.dubbing.audio.get(
                dubbing_id, 
                language_code="uk"
            )
            
            file_name = f"{dubbing_id}.mp4"
            full_path = path.join(self.save_folder, file_name)
            
            await self.save_file_async(audio_stream, full_path)
            print(f"💾 Файл збережено: {full_path}")
            return full_path
            
        except Exception as e:
            print(f"❌ Помилка завантаження файлу: {e}")
            return None


    async def save_file_async(self, stream, path):
        async with aiofiles.open(path, "wb") as f:
            async for chunk in stream:
                if chunk:
                    await f.write(chunk)