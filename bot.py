# Copyright by X-Noid

import os, time, shutil, random, glob, asyncio, uuid, shlex
from typing import Tuple
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import BadRequest, FloodWait

# Configs
API_HASH = os.environ['API_HASH'] # Your API HASH
API_ID = int(os.environ['API_ID']) # Your API ID
BOT_TOKEN = os.environ['BOT_TOKEN'] # Your Bot Token
OWNER_ID = os.environ['OWNER_ID'] # Your Telegram ID

# Buttons
START_BUTTONS=[
    [
        InlineKeyboardButton("Source", url="https://github.com/X-Gorn/Spotify-Loader"),
        InlineKeyboardButton("Project Channel", url="https://t.me/xTeamBots"),
    ],
    [InlineKeyboardButton("Author", url="https://t.me/xgorn")],
]

CB_BUTTONS=[
    [
        InlineKeyboardButton("Send as ZIP", callback_data="zip"),
        InlineKeyboardButton("Send one by one", callback_data="1by1"),
    ]
]

# Helpers
# https://github.com/MysteryBots/UnzipBot/blob/0bc500639ceb18492ac89c8a9de1b8d87241c3cd/UnzipBot/functions.py#L17
async def absolute_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


# https://github.com/X-Gorn/FridayUB/blob/90814701558e986a68fdec2776c5aa004caa8ca5/main_startup/helper_func/basic_helpers.py#L378
async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """ run command in terminal """
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


# Running bot
xbot = Client('Spotify-Loader', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


if OWNER_ID:
    OWNER_FILTER = filters.incoming & filters.chat(int(OWNER_ID))
else:
    OWNER_FILTER = filters.incoming

# Start message
@xbot.on_message(filters.command('start') & OWNER_FILTER & filters.private)
async def start(bot, update):
    await update.reply(f'I\'m Spotify-Loader\nYou can download spotify playlist/artist/album/track music using this bot!', True, reply_markup=InlineKeyboardMarkup(START_BUTTONS))


@xbot.on_message(filters.regex('open(.)spotify(.)com|track|album|artist|playlist') & OWNER_FILTER & filters.private)
async def downloader(bot, update):
    await update.reply('Select Options Below!', True, reply_markup=InlineKeyboardMarkup(CB_BUTTONS))


@xbot.on_callback_query()
async def callbacks(bot: Client, updatex: CallbackQuery):
    cb_data = updatex.data
    update = updatex.message.reply_to_message
    url = updatex.message.reply_to_message.text
    await updatex.message.delete()
    rndm = uuid.uuid4().hex
    dirs = f'./{rndm}/'
    os.mkdir(dirs)
    await runcmd(f"spotdl {url} --path-template '{rndm}" + "/{artist}/{album}/{artist} - {title}.{ext}'")
    art_list = os.listdir(dirs)
    artist_names = ''
    for artist in art_list:
        artist_names += f' {artist},'
    names = artist_names[1:-1]
    if cb_data == 'zip':
        x = 'zipped music files'
        for artist in art_list:
            shutil.make_archive(dirs+'/'+artist, 'zip', dirs+'/'+artist)
            await update.reply_document(dirs+'/'+artist+'.zip')
    elif cb_data == '1by1':
        x = 'all musics'
        dldirs = [i async for i in absolute_paths(dirs)]
        for music in dldirs:
            try:
                await bot.send_audio(chat_id=update.from_user.id, audio=music)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await bot.send_audio(chat_id=update.from_user.id, audio=music)
    await update.reply(f'Successfully uploaded {x} from [{names}]({url})\'s Spotify', parse_mode='markdown')
    shutil.rmtree(dirs)


xbot.run()