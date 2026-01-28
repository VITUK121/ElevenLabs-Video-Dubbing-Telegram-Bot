from elevenlabs.client import AsyncElevenLabs
from time import time
from asyncio import sleep
import aiofiles
from os import path

class Dubbing:
    def __init__(self, api_key, save_folder):
        self.client = AsyncElevenLabs(api_key=api_key)
        self.save_folder = save_folder

    async def start_dubbing(self, file_path):
        with open(file_path, "rb") as f:
            response = await self.client.dubbing.create(file=f, 
                                        name=f"Dub_{int(time())}",
                                        source_lang="ja",
                                        target_lang="uk", 
                                        watermark=True)
        dubbing_id = response.dubbing_id

        while True:
                # Getting status of dub
                project = await self.client.dubbing.get(dubbing_id)
                
                if project.status == "dubbed":
                    print(f"{dubbing_id=} ✅ Статус: DUBBED")
                    break
                elif project.status == "failed":
                    print(f"{dubbing_id=} ❌ Статус: FAILED")
                    return None

                await sleep(5)
        # Getting the filestream
        audio_stream = self.client.dubbing.audio.get(
            dubbing_id, 
            language_code="uk"
        )
        
        file_name = f"{dubbing_id}.mp4"
        full_path = path.join(self.save_folder, file_name)
        # Saving file to server
        await self.save_file_async(audio_stream, full_path)
            
        print(f"💾 Готово! Файл збережено: {self.save_folder}")

        return full_path


    async def save_file_async(self, stream, path):
        async with aiofiles.open(path, "wb") as f:
            async for chunk in stream:
                if chunk:
                    await f.write(chunk)