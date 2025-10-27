from colorama import init, Fore, Style
from config import api_hash, api_id, logger_chat_id, logger_token
from pyrogram.errors.exceptions import StargiftUsageLimited
from pyrogram.enums import ClientPlatform
from pyrogram.errors import RPCError, SessionExpired, AuthKeyInvalid, AuthKeyUnregistered
from pyrogram.types import Gift
from telegram import TGLogger
from pyrogram import Client
import traceback
import argparse
import asyncio
import logging
import math
import os

workdir = os.path.join(os.getcwd(), "sessions")
os.makedirs(workdir, exist_ok=True)
init(autoreset=True)

app = Client("session", device_model="Gift Snipper @touchmeh", client_platform=ClientPlatform.ANDROID, app_version="Android 11.14.1", api_id=api_id, api_hash=api_hash, workdir=workdir)
logger = logging.getLogger(__name__)
tg_logger = TGLogger(logger_token, logger_chat_id)
async def main():
  parser = argparse.ArgumentParser(
    description="Telegram autobuy-bot CLI: snipe gifts by criteria. TG: @touchmeh",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
  )
  parser.add_argument(
    "--id",
    type=int,
    help=(
      "Only target gift(s) with this unique ID "
      "(scans default/all gifts if omitted)"
    )
  )
  parser.add_argument(
    "--title",
    type=str,
    help=(
      "Only target gifts whose title matches exactly "
      "(case-sensitive string comparison)"
    )
  )
  parser.add_argument(
    "-n",
    dest="nullable_title",
    action="store_true",
    help=(
      "Allow gift entries with no title (skip title filter) "
      "if no title is present"
    )
  )
  parser.add_argument(
    "--min-price",
    type=int,
    help=(
      "Only target gifts with exactly this or greater price "
      "(in TGStars)"
    )
  )
  parser.add_argument(
    "--max-price",
    type=int,
    help=(
      "Only target gifts with exactly this or less price "
      "(in TGStars)"
    )
  )
  parser.add_argument(
    "--min-supply",
    type=int,
    help=(
      "Only target gifts with exactly this or greater total available amount/supply"
    )
  )
  parser.add_argument(
    "--max-supply",
    type=int,
    help=(
      "Only target gifts with exactly this or less available amount/supply"
    )
  )
  parser.add_argument(
    "--check-every",
    type=int,
    default=60,
    metavar="SECS",
    help=(
      "Poll for new gifts every N seconds "
      "(default: %(default)s)"
    )
  )
  parser.add_argument(
    "--star-amount",
    dest="star_amount",
    metavar="STARS",
    type=int,
    help=(
      "Amount of telegram stars you're willing to pay"
      "(alternative to --amount)"
    )
  )
  parser.add_argument(
    "--amount",
    type=int,
    default=1,
    metavar="QTY",
    help=(
      "Quantity of gifts to try to purchase on match "
      "(default: %(default)s)"
    )
  )
  args = parser.parse_args()
  
  filters = {
    "limited": True,
    "sold_out": False,
  }
  if args.id is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set ID={args.id}")
    filters["id"] = args.id

  if args.title is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set TITLE={args.title}")
    filters["title"] = args.title.strip()

  if args.min_price is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set MIN_PRICE={args.min_price}")
    filters["min_price"] = args.min_price

  if args.max_price is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set MAX_PRICE={args.max_price}")
    filters["max_price"] = args.max_price

  if args.min_supply is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set MIN_SUPPLY={args.min_supply}")
    filters["min_supply"] = args.min_supply

  if args.max_supply is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set MAX_SUPPLY={args.max_supply}")
    filters["max_supply"] = args.max_supply

  if args.star_amount is not None:
    logger.warning(Fore.GREEN + Style.DIM + f"* set STAR_AMOUNT={args.star_amount} (skipping AMOUNT)")

  try:
    is_authorized = await app.connect()
    if not is_authorized:
      me = await app.authorize()
    else:    
      me = await app.get_me()
  except AuthKeyUnregistered:
    logger.warning(Fore.RED + f"session expired")
    return
  except AuthKeyInvalid:
    logger.warning(Fore.RED + f"session expired")
    return
  except SessionExpired:
    logger.warning(Fore.RED + f"session expired")
    return
  except Exception as e:
    logger.warning(Fore.RED + f"failed to connect: {e}")
    return
  
  try:
    star_balance = await app.get_stars_balance()
    logger.warning(Fore.GREEN + "\n# DEV TG: @touchmeh")
    logger.warning(Fore.GREEN + Style.DIM + f"* Bot is connected to | {me.phone_number}:{me.username} |: {star_balance} ⭐...\n")

    if args.star_amount is not None and args.star_amount > star_balance:
      logger.error(Fore.YELLOW + Style.DIM + f"* Insufficient balance.")
    
    remaining_balance = args.star_amount
    while True:
      try:
        gifts = await app.get_available_gifts()
        gifts = list(sorted(gifts, key=lambda g: float("inf") if g.total_amount is None else g.total_amount))

        if filters.get("limited") is not None:
          gifts = filter(lambda g: g.is_limited == filters.get("limited"), gifts)
        
        if filters.get("title") is not None:
            gifts = filter(
                lambda g: (getattr(g.raw, "title", None) == filters["title"]) or 
                          (args.nullable_title and getattr(g.raw, "title", None) is None),
                gifts
            )

        if filters.get("sold_out") is not None:
          gifts = filter(lambda g: g.is_sold_out == filters.get("sold_out"), gifts)

        if filters.get("id") is not None:
          gifts = filter(lambda g: g.id == filters.get("id"), gifts)

        if filters.get("min_price") is not None:
          gifts = filter(lambda g: g.price >= filters.get("min_price"), gifts)

        if filters.get("max_price") is not None:
          gifts = filter(lambda g: g.price <= filters.get("max_price"), gifts)

        if filters.get("min_supply") is not None:
          gifts = filter(lambda g: g.total_amount >= filters.get("min_supply"), gifts)

        if filters.get("max_supply") is not None:
          gifts = filter(lambda g: g.total_amount <= filters.get("max_supply"), gifts)       

        gifts = list(gifts)
        entries = len(gifts)
        if entries <= 0:
          logger.warning(Fore.RED + Style.DIM + f"No new gifts, waiting {args.check_every} secs...")
          await asyncio.sleep(args.check_every)
          continue
        
        if args.star_amount is None:
          gift = gifts[0]
          amount_succeeded = await buy_gift(app, me.id, gift, args.amount)

          total_amount = gift.price * amount_succeeded
          t = f" \"{gift.raw.title}\"" if gift.raw.title is not None else ""
          message = (
            f"<b>Completed</b>: sent <b>{amount_succeeded}</b> of <b>{args.amount}</b>{t} gifts\n"
            f"<b>Actual cost</b>: <b>{total_amount}</b> ⭐\n\n"
            f"<span class=\"tg-spoiler\">"
            f"ID: {gift.id}\n"
            f"TITLE: {gift.raw.title or 'untitled'}\n"
            f"PRICE: {gift.price} stars\n"
            f"supply: {gift.total_amount or 'unlimited'}"
            f"</span>"
          )

          msg_id = await tg_logger.send_gift_sticker(gift)        
          await tg_logger.send_message(message, reply_to_message_id=msg_id)
          return

        tasks = []
        for gift in gifts:
          if gift.price > remaining_balance:
            continue
            
          a = math.floor(remaining_balance / gift.price)
          amount_succeeded = await buy_gift(app, me.id, gift, a)

          total_amount = gift.price * amount_succeeded
          remaining_balance -= total_amount
          t = f" \"{gift.raw.title}\"" if gift.raw.title is not None else ""
          message = (
            f"<b>Completed</b>: sent <b>{amount_succeeded}</b> of <b>{a}</b>{t} gifts\n"
            f"<b>Actual cost</b>: <b>{total_amount}</b> ⭐\n\n"
            f"<span class=\"tg-spoiler\">"
            f"ID: {gift.id}\n"
            f"TITLE: {gift.raw.title or 'untitled'}\n"
            f"PRICE: {gift.price} stars\n"
            f"supply: {gift.total_amount or 'unlimited'}"
            f"</span>"
          )

          async def send(gift_obj, msg):
            msg_id = await tg_logger.send_gift_sticker(gift_obj)        
            await tg_logger.send_message(msg, reply_to_message_id=msg_id)

          tasks.append(asyncio.create_task(send(gift, message)))

        try:
          await asyncio.gather(*tasks)
        except Exception as e:
          tb_str = traceback.format_exc()
          logger.error(Fore.RED + f"err: {e} / {tb_str}")
        return
      except (OSError, RPCError) as e:
        logger.warning(Fore.YELLOW + f"[WARN] Connection error: {e}, reconnecting...")
        await app.disconnect()
        await asyncio.sleep(2)
        await app.connect()
  except Exception as e:
    tb_str = traceback.format_exc()
    logger.error(f"unhandled error: {e} / {tb_str}")
    return
  finally:
    await app.disconnect()

async def buy_gift(app: Client, receiver_id: int, gift: Gift, amount: int) -> int:
  i = 0   
  while True:
    if i >= amount:
      return i
    
    try: 
      await app.send_gift(receiver_id, gift.id)
    except StargiftUsageLimited:
      logger.error(Fore.RED + f"Gift is sold out")
      return i
    except Exception as e:
      if "BALANCE_TOO_LOW" in str(e.value):
        logger.error(Fore.RED + "Insufficient balance")
        return i
      logger.error(Fore.RED + f"send_gift err: {e}")
      return i
    
    i += 1

if __name__ == "__main__":
  app.run(main())