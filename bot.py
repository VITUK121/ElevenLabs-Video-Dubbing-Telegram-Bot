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
        """
        Handles incoming video messages and downloads the video file.
        """
        if message.video:
            # Get the file_id of the video
            file_id = message.video.file_id
            
            # Inform the user that the download is starting
            await message.reply("Downloading your video...")
            
            try:
                # Get file details including file_path
                file: File = await self.bot.get_file(file_id)
                file_path = file.file_path
                # Define the destination path with a desired filename
                # Using the original filename is often best
                destination = path.join(self.downloads_folder, message.video.file_name or f"{file_id}.mp4")
                
                # Download the file to the specified destination
                await self.bot.download_file(file_path, destination)
                
                await message.reply(f"Video downloaded successfully to: {destination}")
                # Get the end file path
                video_file_path = await self.dub_agent.start_dubbing(destination)
                # Sending video to user
                await self.send_result_to_user(message.from_user.id, video_file_path, destination)


            except Exception as e:
                await message.reply(f"An error occurred during download: {e}")
                # Note: Bots have a 20MB limit for files downloaded via the standard API.
                # For larger files, you might need a different approach (e.g., using a local Bot API server).

        else:
            await message.reply("This is not a video message or something went wrong.")
            
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