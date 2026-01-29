from video_downloader import SocialDownloader
from bot import Ai_Bot
from elevenlabs_agent import Dubbing

from os import getenv, makedirs, path
from dotenv import load_dotenv
from asyncio import run

load_dotenv()

BOT_API_KEY: str= getenv("BOT_API_KEY")
ELEVENLABS_API_KEYS: list= getenv("ELEVENLABS_API_KEYS").split(',')
INPUT_DIR: str = getenv("MAIN_DIR") + "\\Input"
OUTPUT_DIR: str = INPUT_DIR.replace("Input","Output")

if not path.exists(INPUT_DIR):
    makedirs(INPUT_DIR)

if not path.exists(OUTPUT_DIR):
    makedirs(OUTPUT_DIR)

if __name__ == '__main__':
    try:
        dub_agent = Dubbing(ELEVENLABS_API_KEYS, OUTPUT_DIR)
        bot = Ai_Bot(BOT_API_KEY, INPUT_DIR, dub_agent)
        
        run(bot.main())

    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")