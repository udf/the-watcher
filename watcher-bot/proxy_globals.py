from logging import Logger
from telethon import TelegramClient
from telethon.tl.types import User

client: TelegramClient
me: User
logger: Logger