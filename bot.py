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


# =========================
# تنظیمات
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 6303851350

CHANNEL_ID = "@etlaeeeeeee"
CHANNEL_LINK = "https://t.me/etlaeeeeeee"

CARD_NUMBER = "6219861853906500"
CARD_NAME = "تکین درویشی"

DATA_FILE = "data.json"


# =========================
# لاگ
# =========================

logging.basicConfig(
    level=logging.INFO
)


# =========================
# دیتابیس
# =========================

def load_data():

    if not os.path.exists(DATA_FILE):

        data = {
            "owner": OWNER_ID,
            "enabled": True,
            "users": {},
            "reply": {}
        }

        save_data(data)

        return data


    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



def save_data(data):

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


db = load_data()



# =========================
# کاربر
# =========================

def create_user(user_id):

    user_id = str(user_id)

    if user_id not in db["users"]:

        db["users"][user_id] = {

            "referrals": [],

            "claimed": 0,

            "gift": False,

            "request": None
        }

        save_data(db)



# =========================
# عضویت کانال
# =========================

async def check_join(
    user_id,
    context
):

    try:

        member = await context.bot.get_chat_member(
            CHANNEL_ID,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:

        return False



# =========================
# منوی اصلی
# =========================

def main_menu(user_id):

    keyboard = [

        [
            InlineKeyboardButton(
                "🛒 خرید کانفیگ",
                callback_data="buy"
            )
        ],

        [
            InlineKeyboardButton(
                "👥 زیرمجموعه",
                callback_data="ref"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 کانال ما",
                url=CHANNEL_LINK
            )
        ]
    ]


    user = db["users"].get(
        str(user_id),
        {}
    )


    if user.get("gift"):

        keyboard.append(
            [
                InlineKeyboardButton(
                    "🎁 دریافت کانفیگ زیرمجموعه",
                    callback_data="gift"
                )
            ]
        )


    return InlineKeyboardMarkup(
        keyboard
    )



# =========================
# منوی خرید
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
        ]

    ]

    return InlineKeyboardMarkup(
        keyboard
    )



# =========================
# شروع
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    joined = await check_join(
        user.id,
        context
    )


    if not joined:

        keyboard = [

            [
                InlineKeyboardButton(
                    "📢 عضویت در کانال",
                    url=CHANNEL_LINK
                )
            ],

            [
                InlineKeyboardButton(
                    "🔄 بررسی عضویت",
                    callback_data="check_join"
                )
            ]

        ]


        await update.message.reply_text(
            "⚠️ ابتدا عضو کانال شوید.",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    create_user(
        user.id
    )


    await update.message.reply_text(
        "🤖 خوش آمدید\n\n"
        "یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=main_menu(
            user.id
        )
    )
    # =========================
# ثبت زیرمجموعه
# =========================

def add_referral(inviter, user_id):

    inviter = str(inviter)
    user_id = str(user_id)

    if inviter == user_id:
        return

    if inviter not in db["users"]:
        return

    refs = db["users"][inviter]["referrals"]

    if user_id in refs:
        return

    refs.append(user_id)

    # هر 3 نفر یک گیگ
    if len(refs) - db["users"][inviter]["claimed"] >= 3:

        db["users"][inviter]["gift"] = True

    save_data(db)



# =========================
# ساخت لینک دعوت
# =========================

async def get_ref_link(context, user_id):

    bot = await context.bot.get_me()

    return (
        f"https://t.me/{bot.username}"
        f"?start={user_id}"
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


    # بررسی عضویت

    if query.data == "check_join":

        if await check_join(user_id, context):

            create_user(user_id)

            await query.edit_message_text(
                "✅ عضویت تایید شد.",
                reply_markup=main_menu(user_id)
            )

        else:

            await query.answer(
                "❌ هنوز عضو کانال نیستید.",
                show_alert=True
            )

        return



    # خرید

    if query.data == "buy":

        await query.edit_message_text(
            "🛒 یکی از کانفیگ‌ها را انتخاب کنید:",
            reply_markup=buy_menu()
        )

        return



    # 36 گیگ

    if query.data == "buy_36":

        db["users"][str(user_id)]["request"] = "36"

        save_data(db)

        await query.edit_message_text(

            "📦 کانفیگ 36 گیگ\n"
            "⏱ مدت: 1 ماه\n"
            "💰 قیمت: 200 تومان\n\n"

            f"💳 کارت:\n{CARD_NUMBER}\n\n"

            f"👤 به نام:\n{CARD_NAME}\n\n"

            "بعد از پرداخت عکس رسید را ارسال کنید."

        )

        return



    # 78 گیگ

    if query.data == "buy_78":

        db["users"][str(user_id)]["request"] = "78"

        save_data(db)

        await query.edit_message_text(

            "📦 کانفیگ 78 گیگ\n"
            "⏱ مدت: 1 ماه\n"
            "💰 قیمت: 300 تومان\n\n"

            f"💳 کارت:\n{CARD_NUMBER}\n\n"

            f"👤 به نام:\n{CARD_NAME}\n\n"

            "بعد از پرداخت عکس رسید را ارسال کنید."

        )

        return



    # 128 گیگ

    if query.data == "buy_128":

        db["users"][str(user_id)]["request"] = "128"

        save_data(db)

        await query.edit_message_text(

            "📦 کانفیگ 128 گیگ\n"
            "⏱ مدت: 3 ماه\n"
            "💰 قیمت: 550 تومان\n\n"

            f"💳 کارت:\n{CARD_NUMBER}\n\n"

            f"👤 به نام:\n{CARD_NAME}\n\n"

            "بعد از پرداخت عکس رسید را ارسال کنید."

        )

        return



    # زیرمجموعه

    if query.data == "ref":

        link = await get_ref_link(
            context,
            user_id
        )

        count = len(
            db["users"][str(user_id)]["referrals"]
        )


        await query.edit_message_text(

            "👥 سیستم زیرمجموعه\n\n"

            f"تعداد دعوت: {count}\n\n"

            "هر 3 نفر = 1 گیگ هدیه 🎁\n\n"

            "لینک شما:\n"
            f"{link}",

            reply_markup=main_menu(user_id)

        )

        return



    # دریافت گیگ

    if query.data == "gift":

        user_data = db["users"].get(
            str(user_id)
        )


        if not user_data["gift"]:

            await query.answer(
                "هنوز شرایط کامل نشده.",
                show_alert=True
            )

            return


        text = (

            "🎁 درخواست کانفیگ زیرمجموعه\n\n"

            f"👤 نام: {user.full_name}\n"

            f"🆔 آیدی: {user.id}\n"

            f"🔗 یوزرنیم: @{user.username if user.username else 'ندارد'}\n\n"

            "کاربر 3 زیرمجموعه آورده است."

        )


        keyboard = [

            [
                InlineKeyboardButton(
                    "💬 پاسخ",
                    callback_data=f"reply_{user.id}"
                )
            ]

        ]


        await context.bot.send_message(

            chat_id=db["owner"],

            text=text,

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )


        user_data["gift"] = False
        user_data["claimed"] += 3

        save_data(db)


        await query.edit_message_text(

            "✅ درخواست شما ارسال شد.",

            reply_markup=main_menu(user_id)

        )

        return



    if query.data == "back":

        await query.edit_message_text(
            "🤖 منوی اصلی:",
            reply_markup=main_menu(user_id)
        )

        return
    # =========================
# دریافت رسید پرداخت
# =========================

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    data = db["users"].get(
        str(user.id)
    )


    if not data or not data.get("request"):

        await update.message.reply_text(
            "⚠️ اول یک کانفیگ انتخاب کنید."
        )

        return


    product = data["request"]


    text = (

        "💰 رسید پرداخت جدید\n\n"

        f"👤 نام: {user.full_name}\n"

        f"🆔 آیدی: {user.id}\n"

        f"🔗 یوزرنیم: @{user.username if user.username else 'ندارد'}\n\n"

        f"📦 کانفیگ: {product} گیگ\n\n"

        "برای پاسخ روی دکمه زیر بزنید."

    )


    keyboard = [

        [

            InlineKeyboardButton(

                "💬 پاسخ",

                callback_data=f"reply_{user.id}"

            )

        ]

    ]


    await context.bot.send_photo(

        chat_id=db["owner"],

        photo=update.message.photo[-1].file_id,

        caption=text,

        reply_markup=InlineKeyboardMarkup(keyboard)

    )


    await update.message.reply_text(

        "✅ رسید شما ارسال شد."

    )



# =========================
# پیام‌ها
# =========================

async def text_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    # مالک

    if user.id == db["owner"]:

        target = db["reply"].get(
            str(user.id)
        )


        if target:


            await context.bot.copy_message(

                chat_id=int(target),

                from_chat_id=update.message.chat_id,

                message_id=update.message.message_id

            )


            await update.message.reply_text(
                "✅ ارسال شد."
            )


            del db["reply"][str(user.id)]

            save_data(db)


            return



    await update.message.reply_text(
        "از منوی ربات استفاده کنید.",
        reply_markup=main_menu(user.id)
    )



# =========================
# پنل مالک
# =========================

def admin_menu():

    return InlineKeyboardMarkup([

        [

            InlineKeyboardButton(
                "🟢 روشن",
                callback_data="on"
            ),

            InlineKeyboardButton(
                "🔴 خاموش",
                callback_data="off"
            )

        ],

        [

            InlineKeyboardButton(
                "👑 انتقال مالکیت",
                callback_data="owner_change"
            )

        ]

    ])



async def panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != db["owner"]:

        return


    await update.message.reply_text(

        "⚙️ پنل مدیریت",

        reply_markup=admin_menu()

    )



# =========================
# مدیریت پنل
# =========================

async def admin_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    user = query.from_user


    if user.id != db["owner"]:

        await query.answer(
            "دسترسی ندارید",
            show_alert=True
        )

        return


    if query.data.startswith("reply_"):

        target = query.data.split("_")[1]

        db["reply"][str(user.id)] = target

        save_data(db)


        await query.message.reply_text(
            "پیام خود را ارسال کنید (متن، عکس، فایل و ...)"
        )

        return



    if query.data == "on":

        db["enabled"] = True

        save_data(db)

        await query.answer(
            "ربات روشن شد"
        )


    if query.data == "off":

        db["enabled"] = False

        save_data(db)

        await query.answer(
            "ربات خاموش شد"
        )



# =========================
# اجرا
# =========================

def main():

    app = (

        Application

        .builder()

        .token(BOT_TOKEN)

        .build()

    )


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        CommandHandler(
            "panel",
            panel
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )


    app.add_handler(
        CallbackQueryHandler(
            admin_handler
        )
    )


    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            photo_handler
        )
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT,
            text_handler
        )
    )


    print("🤖 BOT STARTED")


    app.run_polling()



if __name__ == "__main__":

    main()
