from os import path
from aiogram import Bot, Router, Dispatcher, types, F
from aiogram.types import File, FSInputFile
from os import remove

class Ai_Bot:
    def __init__(self, api_key, downloads_folder, dub_agent):
        self.bot = Bot(token=api_key)
        self.dp = Dispatcher()
        self.router = Router()
        self.downloads_folder = downloads_folder
        # Dubbuing() from elevenlabs_agent.py
        self.dub_agent = dub_agent
        
        self.router.message.register(self.download_video_handler, F.video)

        self.dp.include_router(self.router)

    async def download_video_handler(self, message: types.Message):
        if message.video:
            file_id = message.video.file_id
            await message.reply("Downloading your video...")
            
            try:
                file: File = await self.bot.get_file(file_id)
                file_path = file.file_path
                destination = path.join(self.downloads_folder, message.video.file_name or f"{file_id}.mp4")
                
                await self.bot.download_file(file_path, destination)
                await message.reply(f"Video downloaded. Starting processing...")
                
                # --- ВИПРАВЛЕННЯ ТУТ ---
                video_file_path = await self.dub_agent.start_dubbing(destination)
                
                if video_file_path:
                    # Якщо файл успішно створено
                    await self.send_result_to_user(message.from_user.id, video_file_path, destination)
                else:
                    # Якщо повернувся None (ключі закінчились або помилка)
                    await message.reply("❌ Не вдалося створити даббінг. Закінчилися кредити на всіх акаунтах або сталася помилка.")
                    # Видаляємо вхідний файл, щоб не засмічувати сервер
                    if path.exists(destination):
                        remove(destination)

            except Exception as e:
                await message.reply(f"An error occurred: {e}")
                # Для відладки виводимо повний трейсбек у консоль
                print(f"CRITICAL BOT ERROR: {e}")
        else:
            await message.reply("This is not a video message.")
            
    async def send_result_to_user(self, chat_id, file_path, file_input_path):
        try:
            # Preparing video
            video_file = FSInputFile(file_path)
            
            # Sending
            print(f"📤 Відправляю відео користувачеві {chat_id}...")
            await self.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption="✅ Ваше відео готове! (Переклад з ElevenLabs)",
                supports_streaming=True
            )
            
            # Removing files from server
            remove(file_path)
            remove(file_input_path)
            
        except Exception as e:
            print(f"❌ Помилка відправки в Telegram: {e}")

    async def main(self):
        await self.dp.start_polling(self.bot)