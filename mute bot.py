import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# 🔑 Вставь токен своего бота
BOT_TOKEN = "8997598498:AAHN76V4rsA905JfmQpgf36bOUSQEpWAIiQ"

# 👤 Вставь СВОЙ личный Telegram ID (число без кавычек)
# Узнать свой ID можно у бота @userinfobot в Телеграме
MY_ADMIN_ID = 8524001499

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище:
# user_counters = { user_id: count }
# muted_users = set(user_id)
user_counters = {}
muted_users = set()

# 1. Ключевое слово для запуска отсчёта (например, человек написал "старт")
@dp.message(F.text.lower() == "старт")
async def start_tracking(message: types.Message):
    user_id = message.from_user.id
    
    # Запускаем отсчёт
    user_counters[user_id] = 0
    await message.answer("Счётчик запущен. Допущено 5 сообщений.")

# 2. Обработка всех сообщений в ЛС
@dp.message()
async def handle_private_messages(message: types.Message):
    user_id = message.from_user.id

    # Если это пишет админ (ТЫ) — бота не ограничиваем
    if user_id == MY_ADMIN_ID:
        return

    # ЕСЛИ ПОЛЬЗОВАТЕЛЬ В МУТЕ — мгновенно удаляем его сообщение!
    if user_id in muted_users:
        try:
            await message.delete()
        except Exception:
            pass # Если сообщение нельзя удалить
        return

    # Если для этого пользователя включён отсчёт
    if user_id in user_counters:
        user_counters[user_id] += 1

        # Если он достиг или превысил 5 сообщений -> отправляем в МУТ
        if user_counters[user_id] >= 5:
            muted_users.add(user_id)
            
            # Удаляем 5-е сообщение
            try:
                await message.delete()
            except Exception:
                pass

            # Кнопка снятия мута (привязана к ТВОЕМУ ID)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔊 Снять мут",
                            callback_data=f"unmute_{user_id}"
                        )
                    ]
                ]
            )

            # Бот уведомляет ТЕБЯ (админа), что пользователь замучен
            await bot.send_message(
                chat_id=MY_ADMIN_ID,
                text=f"🚫 Пользователь {message.from_user.full_name} (@{message.from_user.username}) превысил лимит в 5 сообщений и замучен!\n"
                     f"Его новые сообщения будут удаляться.",
                reply_markup=keyboard
            )

# 3. Обработка нажатия на кнопку "Снять мут"
@dp.callback_query(F.data.startswith("unmute_"))
async def process_unmute(callback: types.CallbackQuery):
    # ПРОВЕРКА: Нажал ли именно ТЫ?
    if callback.from_user.id != MY_ADMIN_ID:
        await callback.answer("❌ Только владелец бота может снять мут!", show_alert=True)
        return

    target_user_id = int(callback.data.split("_")[1])

    # Снимаем мут и сбрасываем счётчик
    if target_user_id in muted_users:
        muted_users.remove(target_user_id)
    if target_user_id in user_counters:
        del user_counters[target_user_id]

    await callback.message.edit_text("🔊 Мут успешно снят! Пользователь снова может писать.")
    
    # Опционально: сообщаем пользователю, что его размутили
    try:
        await bot.send_message(chat_id=target_user_id, text="Вам сняли мут! Вы снова можете отправлять сообщения.")
    except Exception:
        pass

    await callback.answer("Мут снят!")

# Запуск
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

