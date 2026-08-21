import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================
# تنظیمات
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 6303851350

CARD_NUMBER = "6219861853906500"
CARD_NAME = "تکین درویشی"


# =========================
# لاگ
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# ذخیره درخواست‌های کاربران
# =========================

# user_id -> نوع درخواست
# buy_36
# buy_78
# buy_128
# test
# support

user_requests = {}


# =========================
# منوی اصلی
# =========================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🛒 خرید کانفیگ",
                callback_data="buy"
            )
        ],
        [
            InlineKeyboardButton(
                "🧪 تست کانفیگ",
                callback_data="test"
            )
        ],
        [
            InlineKeyboardButton(
                "💬 پشتیبانی",
                callback_data="support"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# دکمه‌های خرید
# =========================

def buy_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "36 گیگ | 1 ماهه | 200 تومان",
                callback_data="buy_36"
            )
        ],
        [
            InlineKeyboardButton(
                "78 گیگ | 1 ماهه | 300 تومان",
                callback_data="buy_78"
            )
        ],
        [
            InlineKeyboardButton(
                "128 گیگ | 3 ماهه | 550 تومان",
                callback_data="buy_128"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 برگشت",
                callback_data="back"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    user_requests.pop(user.id, None)

    text = (
        "🤖 به ربات فروش کانفیگ خوش آمدید.\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# دکمه‌ها
# =========================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user = query.from_user
    user_id = user.id

    # -------------------------
    # خرید
    # -------------------------

    if query.data == "buy":

        user_requests.pop(user_id, None)

        await query.edit_message_text(
            "🛒 یکی از کانفیگ‌های زیر را انتخاب کنید:",
            reply_markup=buy_menu()
        )

        return

    # -------------------------
    # 36 گیگ
    # -------------------------

    if query.data == "buy_36":

        user_requests[user_id] = "buy_36"

        text = (
            "📦 کانفیگ 36 گیگ\n"
            "⏱ مدت: 1 ماهه\n"
            "💰 قیمت: 200 تومان\n\n"
            f"💳 شماره کارت:\n"
            f"{CARD_NUMBER}\n\n"
            f"👤 به نام:\n"
            f"{CARD_NAME}\n\n"
            "💵 مبلغ 200 تومان بزنید.\n\n"
            "📸 بعد از پرداخت، عکس شات/رسید پرداخت "
            "را همینجا ارسال کنید تا مالک بررسی کند.\n\n"
            "⚡ بعد از ارسال رسید، درخواست شما سریع‌تر بررسی می‌شود."
        )

        await query.edit_message_text(text)

        return

    # -------------------------
    # 78 گیگ
    # -------------------------

    if query.data == "buy_78":

        user_requests[user_id] = "buy_78"

        text = (
            "📦 کانفیگ 78 گیگ\n"
            "⏱ مدت: 1 ماهه\n"
            "💰 قیمت: 300 تومان\n\n"
            f"💳 شماره کارت:\n"
            f"{CARD_NUMBER}\n\n"
            f"👤 به نام:\n"
            f"{CARD_NAME}\n\n"
            "💵 مبلغ 300 تومان بزنید.\n\n"
            "📸 بعد از پرداخت، عکس شات/رسید پرداخت "
            "را همینجا ارسال کنید تا مالک بررسی کند.\n\n"
            "⚡ بعد از ارسال رسید، درخواست شما سریع‌تر بررسی می‌شود."
        )

        await query.edit_message_text(text)

        return

    # -------------------------
    # 128 گیگ
    # -------------------------

    if query.data == "buy_128":

        user_requests[user_id] = "buy_128"

        text = (
            "📦 کانفیگ 128 گیگ\n"
            "⏱ مدت: 3 ماهه\n"
            "💰 قیمت: 550 تومان\n\n"
            f"💳 شماره کارت:\n"
            f"{CARD_NUMBER}\n\n"
            f"👤 به نام:\n"
            f"{CARD_NAME}\n\n"
            "💵 مبلغ 550 تومان بزنید.\n\n"
            "📸 بعد از پرداخت، عکس شات/رسید پرداخت "
            "را همینجا ارسال کنید تا مالک بررسی کند.\n\n"
            "⚡ بعد از ارسال رسید، درخواست شما سریع‌تر بررسی می‌شود."
        )

        await query.edit_message_text(text)

        return

    # -------------------------
    # تست کانفیگ
    # -------------------------

    if query.data == "test":

        user_requests[user_id] = "test"

        text = (
            "🧪 با موفقیت درخواست تست به مالک ارسال شد.\n\n"
            "⚡ هرچه سریع‌تر کانفیگ تست برای شما ارسال می‌شود."
        )

        await query.edit_message_text(text)

        # اطلاع به مالک
        await send_test_request_to_owner(
            context,
            user
        )

        return

    # -------------------------
    # پشتیبانی
    # -------------------------

    if query.data == "support":

        user_requests[user_id] = "support"

        text = (
            "💬 درخواستی داشتید توی پیوی بگید.\n\n"
            "چون پیوی شلوغه، پیام خود را همینجا ارسال کنید "
            "تا برای پشتیبانی ارسال شود."
        )

        await query.edit_message_text(text)

        return

    # -------------------------
    # برگشت
    # -------------------------

    if query.data == "back":

        user_requests.pop(user_id, None)

        await query.edit_message_text(
            "🤖 منوی اصلی:",
            reply_markup=main_menu()
        )

        return


# =========================
# ارسال درخواست تست برای مالک
# =========================

async def send_test_request_to_owner(
    context: ContextTypes.DEFAULT_TYPE,
    user
):

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    text = (
        "🧪 درخواست تست کانفیگ\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"🔗 یوزرنیم: {username}\n\n"
        "برای ارسال کانفیگ تست، روی همین پیام Reply کنید "
        "و متن کانفیگ را بفرستید."
    )

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=text
    )


# =========================
# پیام‌های متنی کاربران
# =========================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not update.message:
        return

    user_id = user.id

    # --------------------------------
    # اگر مالک است و Reply می‌کند
    # --------------------------------

    if user_id == OWNER_ID:

        await handle_owner_reply(
            update,
            context
        )

        return

    # --------------------------------
    # کاربر
    # --------------------------------

    request_type = user_requests.get(user_id)

    if request_type == "support":

        await send_support_to_owner(
            update,
            context
        )

        user_requests.pop(user_id, None)

        await update.message.reply_text(
            "✅ پیام شما برای پشتیبانی ارسال شد.\n"
            "به‌محض پاسخ، پاسخ برای شما ارسال می‌شود."
        )

        return

    await update.message.reply_text(
        "لطفاً یکی از گزینه‌های منوی اصلی را انتخاب کنید.",
        reply_markup=main_menu()
    )


# =========================
# رسید پرداخت
# =========================

async def receipt_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if user.id == OWNER_ID:
        return

    request_type = user_requests.get(user.id)

    if request_type not in (
        "buy_36",
        "buy_78",
        "buy_128",
    ):
        await update.message.reply_text(
            "⚠️ ابتدا از منوی «خرید کانفیگ» یکی از کانفیگ‌ها را انتخاب کنید."
        )
        return

    if request_type == "buy_36":

        product = "36 گیگ - 1 ماهه"
        price = "200 تومان"

    elif request_type == "buy_78":

        product = "78 گیگ - 1 ماهه"
        price = "300 تومان"

    else:

        product = "128 گیگ - 3 ماهه"
        price = "550 تومان"

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    caption = (
        "💰 رسید پرداخت جدید\n\n"
        f"📦 محصول: {product}\n"
        f"💵 مبلغ: {price}\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"🔗 یوزرنیم: {username}\n\n"
        "⬇️ برای ارسال کانفیگ، روی همین پیام Reply کنید "
        "و متن کانفیگ را ارسال کنید."
    )

    await context.bot.send_photo(
        chat_id=OWNER_ID,
        photo=update.message.photo[-1].file_id,
        caption=caption
    )

    await update.message.reply_text(
        "✅ رسید شما با موفقیت برای مالک ارسال شد.\n\n"
        "⚡ رسید شما در سریع‌ترین زمان بررسی می‌شود و "
        "پس از تأیید، کانفیگ برای شما ارسال خواهد شد."
    )


# =========================
# ارسال پشتیبانی برای مالک
# =========================

async def send_support_to_owner(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    text = (
        "💬 پیام جدید پشتیبانی\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🆔 آیدی عددی: {user.id}\n"
        f"🔗 یوزرنیم: {username}\n\n"
        "📝 پیام کاربر:\n"
        f"{update.message.text}\n\n"
        "⬇️ برای پاسخ، روی همین پیام Reply کنید."
    )

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=text
    )


# =========================
# Reply مالک
# =========================

async def handle_owner_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message

    # باید Reply باشد
    if not message.reply_to_message:

        await message.reply_text(
            "⚠️ برای ارسال پاسخ به کاربر، "
            "باید روی پیام درخواست همان کاربر Reply کنید."
        )

        return

    replied_message = message.reply_to_message

    # --------------------------------
    # پیدا کردن آیدی کاربر
    # --------------------------------

    target_user_id = extract_user_id(
        replied_message.text
        or replied_message.caption
        or ""
    )

    if not target_user_id:

        await message.reply_text(
            "❌ آیدی کاربر از پیام Reply پیدا نشد."
        )

        return

    # --------------------------------
    # فقط متن کانفیگ / پاسخ
    # --------------------------------

    if not message.text:

        await message.reply_text(
            "⚠️ پاسخ باید به صورت متن ارسال شود."
        )

        return

    config_text = message.text

    try:

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "✅ پاسخ شما آماده است.\n\n"
                f"{config_text}"
            )
        )

        await message.reply_text(
            "✅ پیام با موفقیت برای کاربر ارسال شد."
        )

    except Exception as e:

        logger.exception(e)

        await message.reply_text(
            "❌ ارسال پیام به کاربر ناموفق بود.\n"
            "ممکن است کاربر ربات را بلاک کرده باشد."
        )


# =========================
# پیدا کردن آیدی کاربر
# =========================

def extract_user_id(text):

    if not text:
        return None

    marker = "آیدی عددی:"

    if marker not in text:
        return None

    try:

        part = text.split(marker, 1)[1]

        line = part.split("\n", 1)[0].strip()

        return int(line)

    except Exception:

        return None


# =========================
# پیام عکس / رسید
# =========================

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await receipt_handler(
        update,
        context
    )


# =========================
# دستور ping
# =========================

async def ping(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🏓 ربات فعال است."
    )


# =========================
# اجرای ربات
# =========================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN پیدا نشد! "
            "مطمئن شوید Secret با نام BOT_TOKEN ساخته شده است."
        )

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # دستورات
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        CommandHandler(
            "ping",
            ping
        )
    )

    # دکمه‌ها
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # عکس
    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )

    # متن
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )

    print("🤖 Bot started successfully...")

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
