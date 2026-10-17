import os
import io
import json
import logging
import asyncio
import re
import time
from typing import Optional

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    FSInputFile
)

from database import Database
from checker import BannedChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tg_bot")

db = Database()
checker = BannedChecker()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "bot_config.json")

def load_bot_token() -> str:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("telegram_bot_token", "")
        except Exception:
            pass
    return os.environ.get("TELEGRAM_BOT_TOKEN", "")

def load_webapp_url() -> str:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("webapp_url", "http://localhost:8000")
        except Exception:
            pass
    return "http://localhost:8000"

dp = Dispatcher()

# Multilingual Texts
BOT_TEXTS = {
    "uz": {
        "welcome": (
            "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
            "🛡 <b>InstaSafe UZ</b> — O‘zbekiston Respublikasi Oliy sudi tomonidan taqiqlangan "
            "ekstremistik manbalar (<b>Telegram, YouTube, Instagram, Facebook</b>) bo‘yicha avtomatik tekshiruv tizimi (1560+ ta manba).\n\n"
            "🎁 <b>Siz uchun bonus:</b> 1 ta to‘liq bepul tekshiruv berildi!\n\n"
            "🔍 <b>Qanday tekshirish mumkin (Eng qulay usullar):</b>\n\n"
            "📸 <b>1️⃣ Eng oson usul — Skrinshot yuborish:</b>\n"
            "• Telegram kanallar ro'yxati yoki Instagram/YouTube obunalaringizni <b>skrinshot qilib to'g'ridan-to'g'ri rasm yuboring!</b>\n"
            "• AI 2 soniyada barcha kanallarni avtomatik o'qib tekshiradi.\n\n"
            "✈️ <b>2️⃣ Telegram kanalni tekshirish:</b>\n"
            "• Shubhali kanaldan <b>istalgan xabarni shu botga uzating (forward qiling)</b>!\n"
            "• Yoki kanal nomini/havolasini yuboring (masalan: <code>@kanal_nomi</code> yoki <code>t.me/kanal</code>).\n\n"
            "▶️ <b>3️⃣ YouTube yoki Facebook:</b>\n"
            "• Kanal yoki sahifa nomini/havolasini yuboring (masalan: <code>youtube.com/@kanal</code>).\n\n"
            "📁 <b>4️⃣ Fayl orqali ommaviy tekshirish:</b>\n"
            "• Telegram Desktop'dan <code>result.json</code> yoki Instagram'dan <code>following.json</code> yuboring.\n\n"
            "⚡ <i>Tekshiruv 0.1 soniyada rasmiy Oliy sud reyestri bilan solishtiriladi.</i>"
        ),
        "app_btn": "🛡 InstaSafe ilovasini ochish",
        "buy_btn": "💎 Tekshiruv sotib olish (10 000 so‘m)",
        "balance_btn": "📊 Mening balansim",
        "lang_btn": "🌐 Tilni o'zgartirish (Русский)",
        "guide_btn": "📖 Qo'llanma",
        "balance_text": (
            "📊 <b>Sizning holatingiz:</b>\n\n"
            "• Bepul urinishlar: <b>{free}</b> ta\n"
            "• To‘langan tekshiruvlar: <b>{paid}</b> ta\n"
            "• Jami mavjud: <b>{total}</b> ta"
        ),
        "pay_required": "🔒 <b>Siz bepul tekshiruv imkoniyatidan foydalandingiz.</b>\n\n1 ta tekshiruv narxi: <b>10 000 so‘m</b>.\nDavom etish uchun hisobingizni to‘ldiring.",
        "lang_switched": "🇺🇿 Til o'zbek tiliga o'zgartirildi!"
    },
    "ru": {
        "welcome": (
            "👋 Ассалому алейкум, <b>{name}</b>!\n\n"
            "🛡 <b>InstaSafe UZ</b> — автоматическая система проверки каналов и подписок "
            "(<b>Telegram, YouTube, Instagram, Facebook</b>) по официальному реестру экстремистских материалов Верховного суда РУз (1560+ источников).\n\n"
            "🎁 <b>Ваш бонус:</b> 1 бесплатная проверка доступна прямо сейчас!\n\n"
            "🔍 <b>Как проверить канал или подписки (Самые удобные способы):</b>\n\n"
            "📸 <b>1️⃣ Самый быстрый способ — Отправьте скриншот:</b>\n"
            "• Сделайте <b>скриншот списка ваших Telegram-каналов, подписок Instagram или YouTube</b> и отправьте фото в этот чат!\n"
            "• ИИ за 2 секунды распознает все названия на фото и сверит с черным списком.\n\n"
            "✈️ <b>2️⃣ Проверка Telegram-канала:</b>\n"
            "• Просто <b>перешлите (forward) любое сообщение из канала</b> прямо в этот чат!\n"
            "• Или отправьте ссылку/юзернейм (например: <code>@channel_name</code> или <code>t.me/channel</code>).\n\n"
            "▶️ <b>3️⃣ Проверка YouTube или Facebook:</b>\n"
            "• Отправьте ссылку на канал или его название (например: <code>youtube.com/@channel</code>).\n\n"
            "📁 <b>4️⃣ Массовая проверка файлом:</b>\n"
            "• <code>result.json</code> из Telegram Desktop или <code>following.json</code> из Instagram.\n\n"
            "⚡ <i>Проверка занимает 0.1 секунды по официальной судебной базе.</i>"
        ),
        "app_btn": "🛡 Открыть приложение InstaSafe",
        "buy_btn": "💎 Пополнить проверки (10 000 сум)",
        "balance_btn": "📊 Мой баланс",
        "lang_btn": "🌐 Tilni o'zgartirish (O'zbekcha)",
        "guide_btn": "📖 Инструкция",
        "balance_text": (
            "📊 <b>Ваш статус:</b>\n\n"
            "• Бесплатных попыток: <b>{free}</b>\n"
            "• Оплаченных проверок: <b>{paid}</b>\n"
            "• Всего доступно: <b>{total}</b>"
        ),
        "pay_required": "🔒 <b>Вы использовали бесплатную попытку проверки.</b>\n\nСтоимость разовой проверки: <b>10 000 сум</b>.\nПожалуйста, пополните баланс для продолжения.",
        "lang_switched": "🇷🇺 Язык переключен на русский!"
    }
}

def get_user_lang(user_id: int) -> str:
    status = db.get_user_status(user_id)
    if status and status.get("language"):
        return status["language"]
    return "uz"

def get_main_keyboard(webapp_url: str, lang: str = "uz") -> InlineKeyboardMarkup:
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])
    buttons = [
        [
            InlineKeyboardButton(text=t["app_btn"], web_app=WebAppInfo(url=webapp_url))
        ],
        [
            InlineKeyboardButton(text=t["buy_btn"], callback_data="buy_checks"),
            InlineKeyboardButton(text=t["balance_btn"], callback_data="my_balance")
        ],
        [
            InlineKeyboardButton(text=t["guide_btn"], callback_data="show_guide"),
            InlineKeyboardButton(text=t["lang_btn"], callback_data="toggle_lang")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user
    db.get_or_create_user(
        telegram_id=user.id,
        username=user.username or "",
        first_name=user.first_name or ""
    )
    lang = get_user_lang(user.id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])
    webapp_url = load_webapp_url()

    text = t["welcome"].format(name=user.first_name or "")
    await message.answer(text, reply_markup=get_main_keyboard(webapp_url, lang), parse_mode="HTML")

@dp.callback_query(F.data == "toggle_lang")
async def cb_toggle_lang(callback: types.CallbackQuery):
    curr = get_user_lang(callback.from_user.id)
    new_lang = "ru" if curr == "uz" else "uz"
    db.set_user_language(callback.from_user.id, new_lang)
    t = BOT_TEXTS[new_lang]
    webapp_url = load_webapp_url()
    await callback.message.edit_reply_markup(reply_markup=get_main_keyboard(webapp_url, new_lang))
    await callback.answer(t["lang_switched"], show_alert=False)

@dp.callback_query(F.data == "my_balance")
async def cb_balance(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    status = db.get_user_status(user_id)
    if not status:
        await callback.answer("Error", show_alert=True)
        return
    lang = get_user_lang(user_id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])
    free = status.get("free_checks_left", 0)
    paid = status.get("paid_checks_left", 0)
    total = free + paid
    msg = t["balance_text"].format(free=free, paid=paid, total=total)
    await callback.message.answer(msg, parse_mode="HTML")
    await callback.answer()

@dp.message(Command("guide"))
@dp.callback_query(F.data == "show_guide")
async def show_guide_handler(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    lang = get_user_lang(user_id)
    
    if lang == "uz":
        guide_text = (
            "📖 <b>InstaSafe UZ'dan foydalanish bo'yicha to'liq qo'llanma:</b>\n\n"
            "📸 <b>1. Skrinshot orqali bir zumda tekshirish (Eng qulay):</b>\n"
            "• Telefoningizda Telegram kanallar ro'yxatini, Instagram obunalaringizni yoki YouTube obunalar sahifasini oching.\n"
            "• Ekran skrinshotini (skrin) oling va shu botga <b>rasm sifatida yuboring</b>!\n"
            "• AI sun'iy intellekti 2 soniyada barcha kanallarni aniqlab, Oliy sud bazasidan tekshirib beradi.\n\n"
            "✈️ <b>2. Telegram bitta kanalni tekshirish:</b>\n"
            "• Shubhali kanaldan xabarni botga <b>forward qiling</b>.\n"
            "• Yoki kanal silkasini yuboring (<code>@kanal</code> yoki <code>t.me/...</code>).\n\n"
            "▶️ <b>3. YouTube yoki Facebook:</b>\n"
            "• Kanal yoki sahifa havolasini yuboring (<code>youtube.com/@kanal</code>).\n\n"
            "💻 <b>4. Telegram barcha obunalarini fayl orqali tekshirish:</b>\n"
            "• Kompyuterda Telegram Desktop: <b>Sozlamalar</b> → <b>Qo'shimcha</b> → <b>Export Telegram data</b>.\n"
            "• Faqat <b>«Channels list»</b>ni belgilab, <b>JSON</b> formatida olingan <code>result.json</code> faylini botga yuboring!\n\n"
            "📸 <b>5. Instagram obunalarini fayl orqali tekshirish:</b>\n"
            "• Instagram ilovasi: <b>Hisoblar markazi</b> → <b>Ma'lumotlarni yuklab olish</b> → Faqat «Obunalar» (JSON).\n"
            "• Tayyor bo'lgan <code>following.json</code> faylini botga yuboring."
        )
    else:
        guide_text = (
            "📖 <b>Полная инструкция по использованию InstaSafe UZ:</b>\n\n"
            "📸 <b>1. Проверка по скриншоту (Самый удобный способ):</b>\n"
            "• Откройте на телефоне список каналов Telegram, подписки Instagram или YouTube.\n"
            "• Сделайте скриншот экрана и <b>отправьте фото в этот чат</b>!\n"
            "• ИИ за 2 секунды распознает каналы на фото и сверит их с официальным черным списком.\n\n"
            "✈️ <b>2. Проверка любого Telegram-канала:</b>\n"
            "• Перешлите (forward) сообщение из канала в этот чат.\n"
            "• Или отправьте ссылку на канал (<code>@kanal</code> или <code>t.me/...</code>).\n\n"
            "▶️ <b>3. Проверка YouTube или Facebook:</b>\n"
            "• Отправьте ссылку на канал (<code>youtube.com/@channel</code>).\n\n"
            "💻 <b>4. Проверка всех Telegram-подписок файлом:</b>\n"
            "• В Telegram Desktop: <b>Настройки</b> → <b>Продвинутые настройки</b> → <b>Экспорт данных Telegram</b>.\n"
            "• Отметьте только <b>«Список каналов»</b>, формат <b>JSON</b>.\n"
            "• Отправьте полученный файл <code>result.json</code> в этот чат!\n\n"
            "📸 <b>5. Проверка Instagram файлом:</b>\n"
            "• Выгрузите файл <code>following.json</code> из настроек Instagram и отправьте сюда."
        )

    if isinstance(event, types.CallbackQuery):
        await event.message.answer(guide_text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(guide_text, parse_mode="HTML")

@dp.callback_query(F.data == "buy_checks")
async def cb_buy(callback: types.CallbackQuery):
    lang = get_user_lang(callback.from_user.id)
    if lang == "uz":
        title = "💳 <b>Xavfsizlik tekshiruvlari uchun tarifni tanlang:</b>"
        p1, p2, p3 = "1 ta tekshiruv — 10 000 so‘m", "3 ta tekshiruv — 25 000 so‘m (Foydali)", "Oylik cheksiz — 49 000 so‘m"
    else:
        title = "💳 <b>Выберите тариф для проверки каналов и аккаунтов:</b>"
        p1, p2, p3 = "1 проверка — 10 000 сум", "3 проверки — 25 000 сум (Выгода)", "Месячный безлимит — 49 000 сум"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=p1, callback_data="order_single")],
        [InlineKeyboardButton(text=p2, callback_data="order_pack3")],
        [InlineKeyboardButton(text=p3, callback_data="order_unlimited")]
    ])
    await callback.message.answer(title, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("order_"))
async def cb_order(callback: types.CallbackQuery):
    plan = callback.data.replace("order_", "")
    PACKAGES = {
        "single": (10000, 1, "1 tekshiruv / 1 проверка"),
        "pack3": (25000, 3, "3 tekshiruv / 3 проверки"),
        "unlimited": (49000, 100, "Cheksiz / Безлимит")
    }
    amount, count, name = PACKAGES.get(plan, (10000, 1, "1 tekshiruv"))
    order_id = db.create_order(callback.from_user.id, amount, count, "telegram")

    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass

    click_service_id = cfg.get("click_service_id", "32014")
    click_merchant_id = cfg.get("click_merchant_id", "24018")
    payme_merchant_id = cfg.get("payme_merchant_id", "64b182e01fa2")

    click_url = (
        f"https://my.click.uz/services/pay?service_id={click_service_id}"
        f"&merchant_id={click_merchant_id}"
        f"&amount={amount}"
        f"&transaction_param={order_id}"
    )

    import base64
    payme_params = f"m={payme_merchant_id};ac.order_id={order_id};a={amount * 100}"
    payme_b64 = base64.b64encode(payme_params.encode()).decode()
    payme_url = f"https://checkout.paycom.uz/{payme_b64}"

    lang = get_user_lang(callback.from_user.id)
    if lang == "uz":
        text = (
            f"🧾 <b>To‘lov hisobi №{order_id}</b>\n\n"
            f"• Tarif: <b>{name}</b>\n"
            f"• To‘lov miqdori: <b>{amount:,} so‘m</b>\n"
            f"• Beriladigan tekshiruvlar: <b>{count} ta</b>\n\n"
            f"Quyidagi to‘lov tizimlaridan birini tanlang va to‘lovni amalga oshiring:"
        )
        pay_click_txt = "📲 Click orqali to‘lash"
        pay_payme_txt = "📲 Payme orqali to‘lash"
        check_txt = "🔄 To‘lovni tekshirish"
        demo_txt = "✅ Test to‘lovi (Demo)"
    else:
        text = (
            f"🧾 <b>Счет на оплату №{order_id}</b>\n\n"
            f"• Тариф: <b>{name}</b>\n"
            f"• Сумма к оплате: <b>{amount:,} сум</b>\n"
            f"• Количество проверок: <b>{count}</b>\n\n"
            f"Выберите платежную систему для перехода к оплате:"
        )
        pay_click_txt = "📲 Оплатить через CLICK"
        pay_payme_txt = "📲 Оплатить через PAYME"
        check_txt = "🔄 Проверить оплату"
        demo_txt = "✅ Тестовая оплата (Демо)"

    pay_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=pay_click_txt, url=click_url)],
        [InlineKeyboardButton(text=pay_payme_txt, url=payme_url)],
        [InlineKeyboardButton(text=check_txt, callback_data=f"check_order_{order_id}")],
        [InlineKeyboardButton(text=demo_txt, callback_data=f"pay_demo_{order_id}")]
    ])

    await callback.message.answer(text, reply_markup=pay_kb, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("check_order_"))
async def cb_check_order(callback: types.CallbackQuery):
    order_id = callback.data.replace("check_order_", "")
    status = db.get_user_status(callback.from_user.id)
    lang = get_user_lang(callback.from_user.id)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        order_status = row["status"] if row else "NOT_FOUND"

    if order_status == "PAID":
        msg = "✅ To‘lov tasdiqlandi! Tekshiruvlar balansingizga qo‘shildi." if lang == "uz" else "✅ Оплата подтверждена! Проверки начислены на ваш баланс."
        await callback.answer(msg, show_alert=True)
    else:
        msg = "⏳ To‘lov hali tizimga tushmadi. Iltimos, to‘lovni bajargach qayta bosing." if lang == "uz" else "⏳ Оплата еще не поступила. Попробуйте нажать еще раз после оплаты."
        await callback.answer(msg, show_alert=True)

@dp.callback_query(F.data.startswith("pay_demo_"))
async def cb_demo_payment(callback: types.CallbackQuery):
    order_id = callback.data.replace("pay_demo_", "")
    lang = get_user_lang(callback.from_user.id)
    db.complete_order(order_id)
    msg = "✅ Demo to‘lov muvaffaqiyatli! Balans to‘ldirildi." if lang == "uz" else "✅ Демо-оплата прошла успешно! Баланс пополнен."
    await callback.answer(msg, show_alert=True)
    status = db.get_user_status(callback.from_user.id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])
    free = status.get("free_checks_left", 0)
    paid = status.get("paid_checks_left", 0)
    await callback.message.answer(t["balance_text"].format(free=free, paid=paid, total=free+paid), parse_mode="HTML")

# 1. FORWARDED MESSAGE HANDLER (Any Telegram Channel)
@dp.message(F.forward_origin | F.forward_from_chat)
async def handle_forwarded_channel(message: types.Message):
    user_id = message.from_user.id
    db.get_or_create_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(user_id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])

    can_check, left, _ = db.can_perform_check(user_id)
    if not can_check:
        buy_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["buy_btn"], callback_data="buy_checks")]
        ])
        await message.answer(t["pay_required"], reply_markup=buy_kb, parse_mode="HTML")
        return

    # Extract chat info from forward
    chat_title = ""
    chat_username = ""

    if message.forward_origin and hasattr(message.forward_origin, "chat"):
        chat = message.forward_origin.chat
        chat_title = getattr(chat, "title", "") or ""
        chat_username = getattr(chat, "username", "") or ""
    elif message.forward_from_chat:
        chat = message.forward_from_chat
        chat_title = getattr(chat, "title", "") or ""
        chat_username = getattr(chat, "username", "") or ""

    if not chat_title and not chat_username:
        # User forward, not channel
        await message.answer(
            "⚠️ Ushbu xabar kanaldan uzatilmagan. Iltimos, tekshirmoqchi bo'lgan <b>kanaldan</b> xabarni uzating." if lang == "uz"
            else "⚠️ Это сообщение не из канала. Пожалуйста, перешлите сообщение именно из <b>канала</b>.",
            parse_mode="HTML"
        )
        return

    wait_msg = await message.answer(
        f"🔍 <i>«{chat_title}» kanali Oliy sud ro'yxati bo'yicha tekshirilmoqda...</i>" if lang == "uz"
        else f"🔍 <i>Проверяю канал «{chat_title}» по судебному реестру...</i>",
        parse_mode="HTML"
    )

    # Check against database
    match = checker.check_single_account(chat_username or chat_title, title=chat_title, platform="telegram")
    db.deduct_check(user_id)
    status = db.get_user_status(user_id)

    if match:
        banned = match["banned_item"]
        if lang == "uz":
            rep = (
                f"🚨 <b>DIQQAT! TAQIQLANGAN TELEGRAM KANALI!</b>\n\n"
                f"• Kanal nomi: <b>{chat_title}</b>\n"
                f"• Username: <b>@{chat_username or 'yo\'q'}</b>\n"
                f"• Reyestrdagi yozuv (№{banned['id']}): <b>{banned['original']}</b>\n\n"
                f"⚠️ <b>Ogohlantirish:</b> Ushbu kanal Oliy sud tomonidan ekstremistik deb topilgan. "
                f"Qonuniy xavfsizligingiz uchun undan zudlik bilan chiqib ketish tavsiya etiladi (JK 244-1-moddasi).\n\n"
                f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
            )
        else:
            rep = (
                f"🚨 <b>ВНИМАНИЕ! ЗАПРЕЩЕННЫЙ TELEGRAM-КАНАЛ!</b>\n\n"
                f"• Название канала: <b>{chat_title}</b>\n"
                f"• Юзернейм: <b>@{chat_username or 'нет'}</b>\n"
                f"• Запись суда (№{banned['id']}): <b>{banned['original']}</b>\n\n"
                f"⚠️ <b>Предупреждение:</b> Этот канал включен в список запрещенных экстремистских материалов Верховного суда РУз. "
                f"Рекомендуется немедленно отписаться от него (ст. 244-1 УК РУз).\n\n"
                f"<i>Осталось проверок: {status['total_checks_left']}</i>"
            )
        await wait_msg.edit_text(rep, parse_mode="HTML")
    else:
        if lang == "uz":
            rep = (
                f"✅ <b>KANAL TOZA VA XAVFSIZ!</b>\n\n"
                f"• Kanal: <b>{chat_title}</b> (@{chat_username or 'yopiq'})\n"
                f"• Oliy sudning rasmiy taqiqlangan ro'yxatida mavjud emas.\n\n"
                f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
            )
        else:
            rep = (
                f"✅ <b>КАНАЛ БЕЗОПАСЕН!</b>\n\n"
                f"• Канал: <b>{chat_title}</b> (@{chat_username or 'закрытый'})\n"
                f"• Не числится в реестре запрещенных экстремистских материалов Верховного суда РУз.\n\n"
                f"<i>Осталось проверок: {status['total_checks_left']}</i>"
            )
        await wait_msg.edit_text(rep, parse_mode="HTML")

# 1.5 SCREENSHOT / PHOTO OCR HANDLER (Telegram, Instagram, YouTube, Facebook)
@dp.message(F.photo)
async def handle_photo_upload(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    db.get_or_create_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(user_id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])

    can_check, left, _ = db.can_perform_check(user_id)
    if not can_check:
        buy_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["buy_btn"], callback_data="buy_checks")]
        ])
        await message.answer(t["pay_required"], reply_markup=buy_kb, parse_mode="HTML")
        return

    wait_msg = await message.answer(
        "📸 <i>Skrinshot qabul qilindi. AI tasvirdagi kanallarni o'qib, Oliy sudning 1560+ ta manbasi bilan solishtirmoqda...</i>" if lang == "uz"
        else "📸 <i>Скриншот принят. ИИ распознает каналы на фото и сверяет с базой 1560+ решений суда...</i>",
        parse_mode="HTML"
    )

    try:
        photo = message.photo[-1]
        file_bytes = io.BytesIO()
        await bot.download(photo, destination=file_bytes)
        img_data = file_bytes.getvalue()

        analysis = checker.analyze_screenshot(img_data)
        db.deduct_check(user_id)
        status = db.get_user_status(user_id)

        if analysis["is_safe"]:
            total = analysis["total_checked"]
            ocr_time = analysis.get("ocr_time_seconds", 1.5)
            detected_preview = ""
            if analysis.get("detected_channels"):
                channels_sample = ", ".join([f"«{c}»" for c in analysis["detected_channels"][:5]])
                detected_preview = f"\n• Tahlil qilingan kanallar: <i>{channels_sample}...</i>\n" if lang == "uz" else f"\n• Распознанные каналы: <i>{channels_sample}...</i>\n"

            if lang == "uz":
                rep = (
                    f"✅ <b>SKRINSHOT TEKSHIRUVI: BARCHA KANALLAR XAVFSIZ!</b>\n\n"
                    f"• Aniqlangan kanallar: <b>{total}</b> ta\n"
                    f"• Taqiqlangan manbalar: <b>0</b> ta\n"
                    f"• Tahlil tezligi: <b>{ocr_time} soniya</b>\n"
                    f"{detected_preview}\n"
                    f"Ushbu skrinshotdagi barcha kanallar Oliy sudning rasmiy taqiqlangan ro'yxatida mavjud emas.\n\n"
                    f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
                )
            else:
                rep = (
                    f"✅ <b>ПРОВЕРКА СКРИНШОТА: ВСЕ КАНАЛЫ БЕЗОПАСНЫ!</b>\n\n"
                    f"• Распознано каналов: <b>{total}</b>\n"
                    f"• Запрещенных: <b>0</b>\n"
                    f"• Время анализа: <b>{ocr_time} сек.</b>\n"
                    f"{detected_preview}\n"
                    f"На снимке не обнаружено экстремистских материалов Верховного суда РУз.\n\n"
                    f"<i>Осталось проверок: {status['total_checks_left']}</i>"
                )
            await wait_msg.edit_text(rep, parse_mode="HTML")
        else:
            items_str = "\n".join([
                f"• 🚨 <b>{item['detected_text']}</b> (№{item['details']['banned_item']['id']}: <i>{item['details']['banned_item']['original']}</i>)"
                for item in analysis["banned_found"][:15]
            ])
            ocr_time = analysis.get("ocr_time_seconds", 1.5)
            if lang == "uz":
                rep = (
                    f"🚨 <b>DIQQAT! SKRINSHOTDA TAQIQLANGAN KANALLAR TOPILDI: {analysis['banned_count']} ta!</b>\n\n"
                    f"• Jami aniqlangan: <b>{analysis['total_checked']}</b> ta kanal\n"
                    f"• Tahlil tezligi: <b>{ocr_time} soniya</b>\n\n"
                    f"<b>Taqiqlangan manbalar:</b>\n"
                    f"{items_str}\n\n"
                    f"⚠️ <b>Ogohlantirish:</b> Ushbu kanallar O'zbekiston Respublikasi Oliy sudi tomonidan taqiqlangan. "
                    f"Qonuniy xavfsizligingiz uchun ulardan zudlik bilan chiqib ketish tavsiya etiladi (JK 244-1-moddasi).\n\n"
                    f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
                )
            else:
                rep = (
                    f"🚨 <b>ВНИМАНИЕ! НА СКРИНШОТЕ НАЙДЕНЫ ЗАПРЕЩЕННЫЕ КАНАЛЫ: {analysis['banned_count']}!</b>\n\n"
                    f"• Всего распознано: <b>{analysis['total_checked']}</b> каналов\n"
                    f"• Время анализа: <b>{ocr_time} сек.</b>\n\n"
                    f"<b>Запрещенные ресурсы:</b>\n"
                    f"{items_str}\n\n"
                    f"⚠️ <b>Предупреждение:</b> Эти ресурсы включены в официальный список экстремистских материалов Верховного суда РУз. "
                    f"Срочно отпишитесь от них (ст. 244-1 УК РУз)!\n\n"
                    f"<i>Осталось проверок: {status['total_checks_left']}</i>"
                )
            await wait_msg.edit_text(rep, parse_mode="HTML")
    except Exception as e:
        logger.exception("Error processing screenshot")
        err_text = f"⚠️ Rasm tahlilida xatolik: {e}" if lang == "uz" else f"⚠️ Ошибка при обработке скриншота: {e}"
        await wait_msg.edit_text(err_text)

# 2. DOCUMENT / FILE HANDLER (Universal: Telegram result.json, Instagram following.json, YouTube CSV, TXT)
@dp.message(F.document)
async def handle_document_upload(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    db.get_or_create_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(user_id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])

    can_check, left, _ = db.can_perform_check(user_id)
    if not can_check:
        buy_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["buy_btn"], callback_data="buy_checks")]
        ])
        await message.answer(t["pay_required"], reply_markup=buy_kb, parse_mode="HTML")
        return

    doc = message.document
    fname = (doc.file_name or "").lower()
    
    wait_msg = await message.answer(
        "⏳ <i>Fayl qabul qilindi. 1560+ ta Oliy sud qarorlari bilan tekshirilmoqda...</i>" if lang == "uz"
        else "⏳ <i>Файл принят. Сверяю с базой из 1560+ решений Верховного суда...</i>",
        parse_mode="HTML"
    )

    file_bytes = io.BytesIO()
    await bot.download(doc, destination=file_bytes)
    content_str = file_bytes.getvalue().decode("utf-8", errors="ignore")

    # Universal parsing
    if "chats" in content_str or "public_channel" in content_str or "result" in fname:
        analysis = checker.analyze_telegram_export(content_str)
        platform_name = "Telegram"
    elif fname.endswith(".csv") or "Channel Id" in content_str:
        analysis = checker.analyze_youtube_export(content_str)
        platform_name = "YouTube"
    elif "relationships_following" in content_str or fname.startswith("following"):
        followings = []
        try:
            data = json.loads(content_str)
            rel_list = data.get("relationships_following") or []
            for item in rel_list:
                uname = item.get("title")
                if not uname:
                    for s in item.get("string_list_data", []):
                        if s.get("value"):
                            uname = s["value"]
                            break
                if uname:
                    followings.append({"username": uname.strip().replace("@", ""), "full_name": ""})
        except Exception:
            pass
        analysis = checker.analyze_following_list(followings, platform="instagram")
        platform_name = "Instagram"
    else:
        # Text line-by-line
        items = [line.strip() for line in content_str.splitlines() if line.strip()]
        followings = [{"username": u, "full_name": ""} for u in items]
        analysis = checker.analyze_following_list(followings, platform="all")
        platform_name = "Ro'yxat"

    db.deduct_check(user_id)
    status = db.get_user_status(user_id)

    if analysis["is_safe"]:
        if lang == "uz":
            rep = (
                f"✅ <b>BARCHA OBUNALAR XAVFSIZ!</b>\n\n"
                f"• Platforma: <b>{platform_name}</b>\n"
                f"• Tekshirildi: <b>{analysis['total_checked']}</b> ta kanal/obuna\n"
                f"• Taqiqlangan: <b>0</b> ta\n\n"
                f"Ro'yxatingizda Oliy sudning ekstremistik manbalari topilmadi.\n\n"
                f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
            )
        else:
            rep = (
                f"✅ <b>ВСЕ ПОДПИСКИ В БЕЗОПАСНОСТИ!</b>\n\n"
                f"• Платформа: <b>{platform_name}</b>\n"
                f"• Проверено: <b>{analysis['total_checked']}</b> каналов/подписок\n"
                f"• Запрещенных: <b>0</b>\n\n"
                f"В ваших подписках не обнаружено запрещенных материалов Верховного суда РУз.\n\n"
                f"<i>Осталось проверок: {status['total_checks_left']}</i>"
            )
        await wait_msg.edit_text(rep, parse_mode="HTML")
    else:
        items_str = "\n".join([
            f"• <b>@{item['username']}</b> (№{item['details']['banned_item']['id']}: <i>{item['details']['banned_item']['original']}</i>)"
            for item in analysis["banned_found"][:15]
        ])
        if lang == "uz":
            rep = (
                f"🚨 <b>DIQQAT! TAQIQLANGAN KANALLAR TOPILDI: {analysis['banned_count']} ta!</b>\n\n"
                f"• Platforma: <b>{platform_name}</b>\n"
                f"• Jami tekshirildi: <b>{analysis['total_checked']}</b> ta\n\n"
                f"{items_str}\n\n"
                f"⚠️ <b>Ogohlantirish:</b> Ushbu manbalardan zudlik bilan chiqish (unfollow) tavsiya etiladi (JK 244-1-moddasi).\n\n"
                f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
            )
        else:
            rep = (
                f"🚨 <b>ВНИМАНИЕ! НАЙДЕНЫ ЗАПРЕЩЕННЫЕ КАНАЛЫ: {analysis['banned_count']}!</b>\n\n"
                f"• Платформа: <b>{platform_name}</b>\n"
                f"• Всего проверено: <b>{analysis['total_checked']}</b>\n\n"
                f"{items_str}\n\n"
                f"⚠️ <b>Предупреждение:</b> Срочно отпишитесь от указанных ресурсов (ст. 244-1 УК РУз)!\n\n"
                f"<i>Осталось проверок: {status['total_checks_left']}</i>"
            )
        await wait_msg.edit_text(rep, parse_mode="HTML")

# 3. TEXT HANDLER (Channel Link, Username or Title)
@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text_check(message: types.Message):
    user_id = message.from_user.id
    db.get_or_create_user(user_id, message.from_user.username or "", message.from_user.first_name or "")
    lang = get_user_lang(user_id)
    t = BOT_TEXTS.get(lang, BOT_TEXTS["uz"])

    query = message.text.strip()
    if len(query) < 2:
        return

    can_check, left, _ = db.can_perform_check(user_id)
    if not can_check:
        buy_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t["buy_btn"], callback_data="buy_checks")]
        ])
        await message.answer(t["pay_required"], reply_markup=buy_kb, parse_mode="HTML")
        return

    wait_msg = await message.answer(
        f"🔍 <i>«{query}» Oliy sud bazasidan tekshirilmoqda...</i>" if lang == "uz"
        else f"🔍 <i>Сверяю «{query}» с реестром Верховного суда...</i>",
        parse_mode="HTML"
    )

    match = checker.check_single_account(query)
    db.deduct_check(user_id)
    status = db.get_user_status(user_id)

    if match:
        banned = match["banned_item"]
        plat = match.get("platform", "manba").upper()
        if lang == "uz":
            rep = (
                f"🚨 <b>DIQQAT! TAQIQLANGAN MANBA TOPILDI!</b>\n\n"
                f"• So'rov: <b>{query}</b>\n"
                f"• Platforma: <b>{plat}</b> (№{banned['id']})\n"
                f"• Reyestrdagi yozuv: <b>{banned['original']}</b>\n\n"
                f"⚠️ <b>Ogohlantirish:</b> Ushbu manba Oliy sud tomonidan taqiqlangan. "
                f"Undan zudlik bilan chiqish tavsiya etiladi (JK 244-1-moddasi).\n\n"
                f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
            )
        else:
            rep = (
                f"🚨 <b>ВНИМАНИЕ! ЗАПРЕЩЕННЫЙ РЕСУРС!</b>\n\n"
                f"• Запрос: <b>{query}</b>\n"
                f"• Платформа: <b>{plat}</b> (№{banned['id']})\n"
                f"• Запись суда: <b>{banned['original']}</b>\n\n"
                f"⚠️ <b>Предупреждение:</b> Этот ресурс числится в официальном списке экстремистских материалов Верховного суда РУз.\n\n"
                f"<i>Осталось проверок: {status['total_checks_left']}</i>"
            )
        await wait_msg.edit_text(rep, parse_mode="HTML")
    else:
        if lang == "uz":
            rep = (
                f"✅ <b>MANBA XAVFSIZ!</b>\n\n"
                f"• So'rov: <b>{query}</b>\n"
                f"• Oliy sudning rasmiy taqiqlangan ro'yxatida (1560+ ta) topilmadi.\n\n"
                f"<i>Qolgan tekshiruvlar: {status['total_checks_left']} ta</i>"
            )
        else:
            rep = (
                f"✅ <b>РЕСУРС БЕЗОПАСЕН!</b>\n\n"
                f"• Запрос: <b>{query}</b>\n"
                f"• Не числится в реестре запрещенных экстремистских материалов Верховного суда РУз (1560+ источников).\n\n"
                f"<i>Осталось проверок: {status['total_checks_left']}</i>"
            )
        await wait_msg.edit_text(rep, parse_mode="HTML")

async def main():
    token = load_bot_token()
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("Telegram Bot Token is not set in bot_config.json!")
        return

    bot = Bot(token=token)
    logger.info("Starting Multi-Platform Telegram Bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
