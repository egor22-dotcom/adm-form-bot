import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# Твой новый токен
TOKEN = "8707207716:AAENiuo3o4PWuI0pg4LySxcW6KwEHhBZIk4"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text.startswith(("/ban ", "/permban ", "/bot ", "/warn ")))
async def handle_commands(message: Message):
    parts = message.text.split(maxsplit=2)
    command = parts[0].replace("/", "")
    
    if command == "bot":
        if len(parts) < 2:
            await message.answer("❌ <b>Неверный формат.</b>\nИспользуй: `/bot [Ник или ID]`", parse_mode="HTML")
            return
        target = parts[1]
        reason = parts[2] if len(parts) > 2 else "Бот"
    else:
        if len(parts) < 3:
            await message.answer(f"❌ <b>Неверный формат.</b>\nИспользуй: `/{command} [Ник или ID] [Причина]`", parse_mode="HTML")
            return
        target = parts[1]
        reason = parts[2]

    admin_mention = message.from_user.as_html()
    # Корректируем время под МСК (+3 часа от UTC сервера)
    current_time = (datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M:%S")
    copy_row = f"/{command} {target} {reason}"

    form_text = (
        f"<b><code>{copy_row}</code></b>\n\n"
        f"📝 Форму отправил:\n"
        f"{admin_mention}\n"
        f"({current_time})"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🟢 Принять", callback_data=f"act:ok:{command}:{target}"),
        InlineKeyboardButton(text="🔴 Отказать", callback_data=f"act:no:{command}:{target}")
    ]])

    try:
        await message.delete()
    except Exception:
        pass  # Если у бота нет прав на удаление в этом чате

    await message.answer(text=form_text, reply_markup=keyboard, parse_mode="HTML")

@dp.callback_query(F.data.startswith("act:"))
async def handle_buttons(callback: CallbackQuery):
    _, status, command, target = callback.data.split(":")
    who_pressed = callback.from_user.as_html()
    
    current_text = callback.message.text
    text_lines = current_text.split("\n")
    main_info = "\n".join(text_lines[1:]) if len(text_lines) > 1 else current_text
    reason_text = text_lines[0] if text_lines else f"/{command} {target}"
    
    if status == "ok":
        new_text = f"<b><code>{reason_text}</code></b>\n{main_info}\n\n🟢 <b>Форма принята</b> администратором {who_pressed}"
        await callback.answer("Форма одобрена!")
    else:
        new_text = f"<b><code>{reason_text}</code></b>\n{main_info}\n\n🔴 <b>Форма отклонена</b> администратором {who_pressed}"
        await callback.answer("Форма отклонена.")

    await callback.message.edit_text(text=new_text, parse_mode="HTML", reply_markup=None)

async def main():
    # На всякий случай сбрасываем вебхук от Cloudflare, чтобы Long Polling на Render завелся без конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
