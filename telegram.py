from pyrogram.file_id import FileId
from pyrogram.types import Gift
import aiofiles
import aiohttp
import asyncio
import logging
import io
import os

logger = logging.getLogger(__name__)
CACHE_FOLDER = "cache"
os.makedirs(CACHE_FOLDER, exist_ok=True)

class TGLogger:
  def __init__(self, token: str, chat_id: int):
    self.token = token
    self.chat_id = chat_id

  async def send_gift_sticker(self, gift: Gift, wait: bool = True) -> int:
    filepath = os.path.join(CACHE_FOLDER, f"{gift.id}.tgs")
    if not os.path.exists(filepath):
      async with aiofiles.open(filepath, "wb") as f:
          async for chunk in gift._client.get_file(FileId.decode(gift.sticker.file_id)):
              await f.write(chunk)

    COPY = open(filepath, "rb").read()
    b = io.BytesIO(COPY)
    b.name = f"{gift.id}.tgs"
    return await self.send_sticker(b, wait=wait)

  async def send_sticker(self, file_bytes: io.BytesIO, wait: bool = True) -> int:
    async with aiohttp.ClientSession() as session:
      data = aiohttp.FormData()
      data.add_field("chat_id", str(self.chat_id))
      data.add_field(
          "sticker",
          file_bytes,
          filename=file_bytes.name,
          content_type="application/x-tgsticker"
      )
      async with session.post(f"https://api.telegram.org/bot{self.token}/sendSticker", data=data) as response:
        response_json = await response.json()
        if response.status == 429 and wait:
          retry_after = response_json["parameters"]["retry_after"]

          logger.warning(f"FLOOD WAIT 429: {response_json}, waiting {retry_after} secs...")
          await asyncio.sleep(retry_after)
          return self.send_sticker(file_bytes, wait=False)
        
        response.raise_for_status()
        return response_json["result"]["message_id"]
      
  async def send_message(self, message: str, wait: bool = True, reply_to_message_id: int | None = None):
    async with aiohttp.ClientSession() as session:
      payload = {
        "text": message,
        "chat_id": self.chat_id,
        "parse_mode": "HTML"
      }
      if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id
      async with session.post(f"https://api.telegram.org/bot{self.token}/sendMessage", json=payload) as response:
        
        response_json = await response.json()
        if response.status == 429 and wait:
          retry_after = response_json["parameters"]["retry_after"]

          logger.warning(f"FLOOD WAIT 429: {response_json}, waiting {retry_after} secs...")
          await asyncio.sleep(retry_after)
          return self.send_message(message, wait=False)
        
        response.raise_for_status()