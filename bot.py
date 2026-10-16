import asyncio
import os
from pathlib import Path
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv
from stories.story_data import STORIES
from render_chat import render_chapter

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", "10000"))
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

bot = Bot(TOKEN)
dp = Dispatcher()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Начать страшную переписку", callback_data="stories")],
        [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="about")]
    ])

def story_menu():
    rows = [[InlineKeyboardButton(text=f"{s['emoji']} {s['title']}", callback_data=f"open:{sid}:0")]
            for sid, s in STORIES.items()]
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def chapter_menu(story_id, index):
    story = STORIES[story_id]
    rows = []
    if index + 1 < len(story["chapters"]):
        rows.append([InlineKeyboardButton(text="➡️ Читать следующую часть", callback_data=f"open:{story_id}:{index+1}")])
    else:
        rows.append([InlineKeyboardButton(text="🔁 Прочитать заново", callback_data=f"open:{story_id}:0")])
    rows += [
        [InlineKeyboardButton(text="📚 Другие истории", callback_data="stories")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="home")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🌘 <b>ПОСЛЕ ПОЛУНОЧИ</b>\n\nСтрашные переписки, странные сообщения и тайны, которые лучше не открывать ночью.\n\nВыбирай историю 👁️",
        reply_markup=main_menu(), parse_mode="HTML"
    )

@dp.message(Command("stories"))
async def stories_command(message: Message):
    await message.answer("📚 Выбери историю:", reply_markup=story_menu())

@dp.callback_query(F.data == "home")
async def go_home(callback: CallbackQuery):
    await callback.message.answer("🌘 <b>ПОСЛЕ ПОЛУНОЧИ</b>\nЧто будем читать?", reply_markup=main_menu(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.answer(
        "📱 <b>Как читать истории</b>\n\n1. Выбери сюжет.\n2. Бот отправит картинку переписки с аватарами.\n3. Нажми «Следующая часть».\n\nИстории заранее написаны автором.",
        parse_mode="HTML", reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "stories")
async def choose_story(callback: CallbackQuery):
    await callback.message.answer("📚 Выбери историю:", reply_markup=story_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("open:"))
async def open_chapter(callback: CallbackQuery):
    try:
        _, story_id, index_text = callback.data.split(":")
        index = int(index_text)
        story = STORIES[story_id]
        chapter = story["chapters"][index]
    except (ValueError, KeyError, IndexError):
        await callback.answer("Не удалось открыть эту часть.", show_alert=True)
        return
    path = render_chapter(story, chapter, index + 1)
    caption = f"{story['emoji']} <b>{story['title']}</b>\nЧасть {index+1} из {len(story['chapters'])}\n\n{chapter['teaser']}"
    await callback.message.answer_photo(FSInputFile(path), caption=caption, parse_mode="HTML",
                                        reply_markup=chapter_menu(story_id, index))
    await callback.answer()

async def on_startup(bot: Bot):
    if not PUBLIC_URL:
        raise RuntimeError("Set PUBLIC_URL to your deployed HTTPS URL, e.g. https://your-service.onrender.com")
    await bot.set_webhook(f"{PUBLIC_URL}/telegram/webhook", drop_pending_updates=True)

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

async def health(request):
    return web.Response(text="Scary chat bot is running.")

async def main():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_post("/telegram/webhook", SimpleRequestHandler(dispatcher=dp, bot=bot))
    setup_application(app, dp, bot=bot)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Webhook server running on port {PORT}")
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
