import asyncio
from telethon import TelegramClient
client = TelegramClient("/opt/humanlike-agent/humanlike_agent", 2040, "b18441a1ff607e10a989891a5462e627")
async def main():
    await client.start(phone="+79933490618")
    me = await client.get_me()
    print(f"Authorized as {me.first_name} (ID: {me.id})")
    await client.disconnect()
asyncio.run(main())
