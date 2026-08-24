import os
import json
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


# =========================================================
# تنظیمات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_OWNER_ID = 6303851350

CARD_NUMBER = "6219861853906500"
CARD_NAME = "تکین درویشی"

CHANNEL_USERNAME = "@etlaeeeeeee"
CHANNEL_URL = "https://t.me/etlaeeeeeee"

DATA_FILE = "bot_data.json"


# =========================================================
# لاگ
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# وضعیت کاربران
# =========================================================

user_requests = {}

# برای انتقال مالکیت
transfer_requests = set()


# =========================================================
# اطلاعات ربات
# =========================================================

def load_data():

    default_data = {
        "owner_id": DEFAULT_OWNER_ID,
        "bot_enabled": True
    }

    if not os.path.exists(DATA_FILE):
        save_data(default_data)
        return default_data

    try:

        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if "owner_id" not in data:
            data["owner_id"] = DEFAULT_OWNER_ID

        if "bot_enabled" not in data:
            data["bot_enabled"] = True

        return data

    except Exception as e:

        logger.exception(e)

        return default_data


def save_data(data):

    try:

        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        logger.exception(e)


bot_data = load_data()


# =========================================================
# گرفتن مالک فعلی
# =========================================================

def get_owner_id():

    return int(bot_data["owner_id"])


# =========================================================
# بررسی مالک
# =========================================================

def is_owner(user_id):

    return user_id == get_owner_id()


# =========================================================
# منوی اصلی
# =========================================================

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

        [
            InlineKeyboardButton(
                "📢 کانال ما",
                url=CHANNEL_URL
            )
        ],

    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# منوی خرید
# =========================================================

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


# =========================================================
# پنل مدیریت
# =========================================================

def admin_panel():

    if bot_data["bot_enabled"]:

        status_text = "🟢 وضعیت: روشن"

    else:

        status_text = "🔴 وضعیت: خاموش"

    keyboard = [

        [
            InlineKeyboardButton(
                status_text,
                callback_data="admin_status"
            )
        ],

        [
            InlineKeyboardButton(
                "🟢 روشن کردن ربات",
                callback_data="admin_on"
            )
        ],

        [
            InlineKeyboardButton(
                "🔴 خاموش کردن ربات",
                callback_data="admin_off"
            )
        ],

        [
            InlineKeyboardButton(
                "👑 انتقال مالکیت",
                callback_data="admin_transfer"
            )
        ],

        [
            InlineKeyboardButton(
                "🔙 منوی اصلی",
                callback_data="admin_back"
            )
        ],

    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# /start
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    user_requests.pop(user.id, None)

    text = (
        "🤖 به ربات فروش کانفیگ خوش آمدید.\n\n"
        "📢 کانال ما:\n"
        f"{CHANNEL_USERNAME}\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# /panel
# =========================================================

async def panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not is_owner(user.id):

        await update.message.reply_text(
            "⛔ شما مالک ربات نیستید."
        )

        return

    await update.message.reply_text(
        "⚙️ پنل مدیریت ربات\n\n"
        f"👑 مالک فعلی: {get_owner_id()}",
        reply_markup=admin_panel()
    )


# =========================================================
# /ping
# =========================================================

async def ping(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🏓 ربات فعال است."
    )


# =========================================================
# دکمه‌ها
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user = query.from_user
    user_id = user.id
    data = query.data


    # =====================================================
    # پنل مدیریت
    # =====================================================

    if data.startswith("admin_"):

        if not is_owner(user_id):

            await query.answer(
                "⛔ فقط مالک می‌تواند از پنل استفاده کند.",
                show_alert=True
            )

            return


        # -------------------------------------------------
        # وضعیت
        # -------------------------------------------------

        if data == "admin_status":

            if bot_data["bot_enabled"]:

                status = "🟢 روشن"

            else:

                status = "🔴 خاموش"

            await query.answer(
                f"وضعیت ربات: {status}",
                show_alert=True
            )

            return


        # -------------------------------------------------
        # روشن کردن
        # -------------------------------------------------

        if data == "admin_on":

            bot_data["bot_enabled"] = True

            save_data(bot_data)

            await query.edit_message_text(
                "🟢 ربات روشن شد.\n\n"
                "کاربران می‌توانند دوباره از ربات استفاده کنند.",
                reply_markup=admin_panel()
            )

            return


        # -------------------------------------------------
        # خاموش کردن
        # -------------------------------------------------

        if data == "admin_off":

            bot_data["bot_enabled"] = False

            save_data(bot_data)

            await query.edit_message_text(
                "🔴 ربات خاموش شد.\n\n"
                "کاربران نمی‌توانند از امکانات ربات استفاده کنند.\n"
                "پنل مالک همچنان فعال است.",
                reply_markup=admin_panel()
            )

            return


        # -------------------------------------------------
        # انتقال مالکیت
        # -------------------------------------------------

        if data == "admin_transfer":

            transfer_requests.add(user_id)

            await query.edit_message_text(
                "👑 انتقال مالکیت\n\n"
                "آیدی عددی مالک جدید را ارسال کنید.\n\n"
                "مثال:\n"
                "123456789\n\n"
                "⚠️ بعد از انتقال، مالک فعلی دیگر به پنل مدیریت دسترسی نخواهد داشت."
            )

            return


    # =====================================================
    # برگشت پنل
    # =====================================================

    if data == "admin_back":

        if not is_owner(user_id):

            return

        await query.edit_message_text(
            "🤖 منوی اصلی:",
            reply_markup=main_menu()
        )

        return


    # =====================================================
    # خرید
    # =====================================================

    if data == "buy":

        if not bot_data["bot_enabled"] and not is_owner(user_id):

            await query.answer(
                "🔴 ربات موقتاً خاموش است.",
                show_alert=True
            )

            return

        user_requests.pop(user_id, None)

        await query.edit_message_text(
            "🛒 یکی از کانفیگ‌های زیر را انتخاب کنید:",
            reply_markup=buy_menu()
        )

        return


    # =====================================================
    # 36 گیگ
    # =====================================================

    if data == "buy_36":

        if not bot_data["bot_enabled"] and not is_owner(user_id):

            await query.answer(
                "🔴 ربات موقتاً خاموش است.",
                show_alert=True
            )

            return

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
            "را همینجا ارسال کنید."
        )

        await query.edit_message_text(text)

        return


    # =====================================================
    # 78 گیگ
    # =====================================================

    if data == "buy_78":

        if not bot_data["bot_enabled"] and not is_owner(user_id):

            await query.answer(
                "🔴 ربات موقتاً خاموش است.",
                show_alert=True
            )

            return

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
            "را همینجا ارسال کنید."
        )

        await query.edit_message_text(text)

        return


    # =====================================================
    # 128 گیگ
    # =====================================================

    if data == "buy_128":

        if not bot_data["bot_enabled"] and not is_owner(user_id):

            await query.answer(
                "🔴 ربات موقتاً خاموش است.",
                show_alert=True
            )

            return

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
            "را همینجا ارسال کنید."
        )

        await query.edit_message_text(text)

        return


    # =====================================================
    # تست
    # =====================================================

    if data == "test":

        if not bot_data["bot_enabled"] and not is_owner(user_id):

            await query.answer(
                "🔴 ربات موقتاً خاموش است.",
                show_alert=True
            )

            return

        user_requests[user_id] = "test"

        await query.edit_message_text(
            "🧪 درخواست تست شما ثبت شد.\n\n"
            "⚡ درخواست برای مالک ارسال شد."
        )

        await send_test_request_to_owner(
            context,
            user
        )

        return


    # =====================================================
    # پشتیبانی
    # =====================================================

    if data == "support":

        if not bot_data["bot_enabled"] and not is_owner(user_id):

            await query.answer(
                "🔴 ربات موقتاً خاموش است.",
                show_alert=True
            )

            return

        user_requests[user_id] = "support"

        await query.edit_message_text(
            "💬 پیام خود را همینجا ارسال کنید "
            "تا برای پشتیبانی ارسال شود."
        )

        return


    # =====================================================
    # برگشت خرید
    # =====================================================

    if data == "back":

        user_requests.pop(user_id, None)

        await query.edit_message_text(
            "🤖 منوی اصلی:",
            reply_markup=main_menu()
        )

        return


# =========================================================
# درخواست تست برای مالک
# =========================================================

async def send_test_request_to_owner(
    context: ContextTypes.DEFAULT_TYPE,
    user
):

    owner_id = get_owner_id()

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
        "برای ارسال کانفیگ تست، روی همین پیام Reply کنید."
    )

    await context.bot.send_message(
        chat_id=owner_id,
        text=text
    )


# =========================================================
# پیام متنی
# =========================================================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    user = update.effective_user
    user_id = user.id


    # =====================================================
    # انتقال مالکیت
    # =====================================================

    if is_owner(user_id) and user_id in transfer_requests:

        text = update.message.text.strip()

        try:

            new_owner_id = int(text)

        except ValueError:

            await update.message.reply_text(
                "❌ آیدی معتبر نیست.\n\n"
                "لطفاً فقط آیدی عددی را ارسال کنید."
            )

            return


        if new_owner_id <= 0:

            await update.message.reply_text(
                "❌ آیدی واردشده معتبر نیست."
            )

            return


        # انتقال
        old_owner = get_owner_id()

        bot_data["owner_id"] = new_owner_id

        save_data(bot_data)

        transfer_requests.discard(user_id)

        await update.message.reply_text(
            "👑 انتقال مالکیت انجام شد.\n\n"
            f"مالک قبلی: {old_owner}\n"
            f"مالک جدید: {new_owner_id}\n\n"
            "⚠️ از این لحظه مالک جدید می‌تواند با /panel وارد پنل مدیریت شود."
        )

        return


    # =====================================================
    # مالک
    # =====================================================

    if is_owner(user_id):

        await handle_owner_reply(
            update,
            context
        )

        return


    # =====================================================
    # اگر ربات خاموش است
    # =====================================================

    if not bot_data["bot_enabled"]:

        await update.message.reply_text(
            "🔴 ربات در حال حاضر خاموش است.\n\n"
            "لطفاً بعداً دوباره تلاش کنید."
        )

        return


    # =====================================================
    # پشتیبانی
    # =====================================================

    request_type = user_requests.get(user_id)

    if request_type == "support":

        await send_support_to_owner(
            update,
            context
        )

        user_requests.pop(user_id, None)

        await update.message.reply_text(
            "✅ پیام شما برای پشتیبانی ارسال شد."
        )

        return


    await update.message.reply_text(
        "لطفاً یکی از گزینه‌های منوی اصلی را انتخاب کنید.",
        reply_markup=main_menu()
    )


# =========================================================
# رسید پرداخت
# =========================================================

async def receipt_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if is_owner(user.id):
        return

    if not bot_data["bot_enabled"]:

        await update.message.reply_text(
            "🔴 ربات در حال حاضر خاموش است."
        )

        return

    request_type = user_requests.get(user.id)

    if request_type not in (
        "buy_36",
        "buy_78",
        "buy_128",
    ):

        await update.message.reply_text(
            "⚠️ ابتدا از منوی خرید، یکی از کانفیگ‌ها را انتخاب کنید."
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
        "⬇️ برای ارسال کانفیگ، روی همین پیام Reply کنید."
    )


    await context.bot.send_photo(
        chat_id=get_owner_id(),
        photo=update.message.photo[-1].file_id,
        caption=caption
    )


    await update.message.reply_text(
        "✅ رسید شما با موفقیت برای مالک ارسال شد.\n\n"
        "⚡ پس از بررسی، کانفیگ برای شما ارسال خواهد شد."
    )


# =========================================================
# پشتیبانی
# =========================================================

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
        chat_id=get_owner_id(),
        text=text
    )


# =========================================================
# پاسخ مالک
# =========================================================

async def handle_owner_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.message

    if not message.reply_to_message:

        await message.reply_text(
            "⚠️ برای ارسال پاسخ به کاربر، "
            "روی پیام درخواست همان کاربر Reply کنید."
        )

        return


    replied_message = message.reply_to_message

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


    if not message.text:

        await message.reply_text(
            "⚠️ پاسخ باید به صورت متن ارسال شود."
        )

        return


    try:

        await context.bot.send_message(
            chat_id=target_user_id,
            text=(
                "✅ پاسخ شما آماده است.\n\n"
                f"{message.text}"
            )
        )


        await message.reply_text(
            "✅ پیام با موفقیت برای کاربر ارسال شد."
        )


    except Exception as e:

        logger.exception(e)

        await message.reply_text(
            "❌ ارسال پیام ناموفق بود.\n"
            "ممکن است کاربر ربات را بلاک کرده باشد."
        )


# =========================================================
# استخراج آیدی
# =========================================================

def extract_user_id(text):

    if not text:
        return None

    marker = "آیدی عددی:"

    if marker not in text:
        return None

    try:

        part = text.split(
            marker,
            1
        )[1]

        line = part.split(
            "\n",
            1
        )[0].strip()

        return int(line)

    except Exception:

        return None


# =========================================================
# عکس
# =========================================================

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await receipt_handler(
        update,
        context
    )


# =========================================================
# اجرای ربات
# =========================================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN پیدا نشد! "
            "در GitHub Secrets یک Secret با نام BOT_TOKEN بساز."
        )


    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    # =========================
    # دستورات
    # =========================

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

    app.add_handler(
        CommandHandler(
            "panel",
            panel
        )
    )


    # =========================
    # دکمه‌ها
    # =========================

    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )


    # =========================
    # عکس
    # =========================

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )


    # =========================
    # متن
    # =========================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            text_handler
        )
    )


    print("================================")
    print("🤖 BOT STARTED")
    print("👑 OWNER:", get_owner_id())
    print("🟢 ENABLED:", bot_data["bot_enabled"])
    print("📢 CHANNEL:", CHANNEL_USERNAME)
    print("================================")


    app.run_polling(
        drop_pending_updates=True
    )


# =========================================================
# شروع
# =========================================================

if __name__ == "__main__":
    main()
