import os
import json
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)


# =====================
# تنظیمات
# =====================

BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 6303851350

CHANNEL = "@etlaeeeeeee"
CHANNEL_LINK = "https://t.me/etlaeeeeeee"

CARD_NUMBER = "6219861853906500"
CARD_NAME = "تکین درویشی"

DATA_FILE = "data.json"


logging.basicConfig(
    level=logging.INFO
)


# =====================
# دیتابیس
# =====================

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


    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {
            "owner": OWNER_ID,
            "enabled": True,
            "users": {},
            "reply": {}
        }



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



# =====================
# ساخت کاربر
# =====================

def create_user(user_id):

    user_id = str(user_id)

    if user_id not in db["users"]:

        db["users"][user_id] = {
            "refs": [],
            "claimed": 0,
            "gift": False,
            "buy": None
        }

        save_data(db)



# =====================
# چک عضویت کانال
# =====================

async def check_channel(
    user_id,
    context
):

    try:

        member = await context.bot.get_chat_member(
            CHANNEL,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:

        return False



# =====================
# منوی اصلی
# =====================

def main_menu(user_id):

    buttons = [

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
                "📢 کانال",
                url=CHANNEL_LINK
            )
        ]

    ]


    user = db["users"].get(
        str(user_id),
        {}
    )


    if user.get("gift"):

        buttons.append(
            [
                InlineKeyboardButton(
                    "🎁 دریافت کانفیگ زیرمجموعه",
                    callback_data="gift"
                )
            ]
        )


    return InlineKeyboardMarkup(
        buttons
    )



# =====================
# منوی خرید
# =====================

def buy_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "36 گیگ | 1 ماهه | 200 تومان",
                callback_data="buy36"
            )
        ],

        [
            InlineKeyboardButton(
                "78 گیگ | 1 ماهه | 300 تومان",
                callback_data="buy78"
            )
        ],

        [
            InlineKeyboardButton(
                "128 گیگ | 3 ماهه | 550 تومان",
                callback_data="buy128"
            )
        ],

        [
            InlineKeyboardButton(
                "🔙 برگشت",
                callback_data="back"
            )
        ]

    ])



# =====================
# استارت
# =====================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    if not await check_channel(
        user.id,
        context
    ):

        keyboard = [

            [
                InlineKeyboardButton(
                    "📢 عضویت کانال",
                    url=CHANNEL_LINK
                )
            ],

            [
                InlineKeyboardButton(
                    "🔄 بررسی عضویت",
                    callback_data="check"
                )
            ]

        ]


        await update.message.reply_text(

            "⚠️ اول عضو کانال شوید.",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )

        return


    create_user(
        user.id
    )


    await update.message.reply_text(

        "🤖 خوش آمدید",

        reply_markup=main_menu(
            user.id
        )

    )
# =====================
# اضافه کردن زیرمجموعه
# =====================

def add_ref(inviter, new_user):

    inviter = str(inviter)
    new_user = str(new_user)

    if inviter == new_user:
        return

    create_user(inviter)
    create_user(new_user)

    refs = db["users"][inviter]["refs"]

    if new_user in refs:
        return

    refs.append(new_user)

    if len(refs) - db["users"][inviter]["claimed"] >= 3:

        db["users"][inviter]["gift"] = True

    save_data(db)



# =====================
# لینک دعوت
# =====================

async def referral_link(
    context,
    user_id
):

    bot = await context.bot.get_me()

    return (
        f"https://t.me/{bot.username}?start={user_id}"
    )



# =====================
# دکمه ها
# =====================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user = query.from_user

    uid = user.id



    # بررسی عضویت

    if query.data == "check":

        if await check_channel(uid, context):

            create_user(uid)

            await query.edit_message_text(

                "✅ تایید شد",

                reply_markup=main_menu(uid)

            )

        else:

            await query.answer(
                "هنوز عضو کانال نیستید",
                show_alert=True
            )

        return



    # خرید

    if query.data == "buy":

        await query.edit_message_text(

            "🛒 انتخاب کانفیگ:",

            reply_markup=buy_menu()

        )

        return



    # خرید 36

    if query.data == "buy36":

        db["users"][str(uid)]["buy"] = "36 گیگ"

        save_data(db)

        await query.edit_message_text(

            "📦 36 گیگ\n"
            "⏱ یک ماهه\n"
            "💰 200 تومان\n\n"
            f"💳 {CARD_NUMBER}\n"
            f"👤 {CARD_NAME}\n\n"
            "بعد از پرداخت عکس رسید را ارسال کنید."

        )

        return



    # خرید 78

    if query.data == "buy78":

        db["users"][str(uid)]["buy"] = "78 گیگ"

        save_data(db)

        await query.edit_message_text(

            "📦 78 گیگ\n"
            "⏱ یک ماهه\n"
            "💰 300 تومان\n\n"
            f"💳 {CARD_NUMBER}\n"
            f"👤 {CARD_NAME}\n\n"
            "بعد از پرداخت عکس رسید را ارسال کنید."

        )

        return



    # خرید 128

    if query.data == "buy128":

        db["users"][str(uid)]["buy"] = "128 گیگ"

        save_data(db)

        await query.edit_message_text(

            "📦 128 گیگ\n"
            "⏱ سه ماهه\n"
            "💰 550 تومان\n\n"
            f"💳 {CARD_NUMBER}\n"
            f"👤 {CARD_NAME}\n\n"
            "بعد از پرداخت عکس رسید را ارسال کنید."

        )

        return



    # زیرمجموعه

    if query.data == "ref":

        link = await referral_link(
            context,
            uid
        )

        count = len(
            db["users"][str(uid)]["refs"]
        )

        await query.edit_message_text(

            "👥 زیرمجموعه\n\n"
            f"تعداد دعوت: {count}\n\n"
            "هر 3 نفر = 1 گیگ 🎁\n\n"
            f"لینک شما:\n{link}",

            reply_markup=main_menu(uid)

        )

        return



    # دریافت گیگ

    if query.data == "gift":

        info = db["users"][str(uid)]


        if not info["gift"]:

            await query.answer(
                "شرایط کامل نیست",
                show_alert=True
            )

            return



        text = (

            "🎁 درخواست گیگ زیرمجموعه\n\n"
            f"👤 {user.full_name}\n"
            f"🆔 {uid}\n"
            f"🔗 @{user.username or 'ندارد'}\n\n"
            "3 زیرمجموعه آورده است."

        )


        await context.bot.send_message(

            chat_id=db["owner"],

            text=text

        )


        info["gift"] = False

        info["claimed"] += 3

        save_data(db)


        await query.edit_message_text(

            "✅ درخواست ارسال شد",

            reply_markup=main_menu(uid)

        )

        return



    if query.data == "back":

        await query.edit_message_text(

            "منوی اصلی",

            reply_markup=main_menu(uid)

        )

# =====================
# رسید پرداخت
# =====================

async def photo_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    info = db["users"].get(
        str(user.id)
    )


    if not info or not info.get("buy"):

        await update.message.reply_text(
            "⚠️ اول کانفیگ انتخاب کنید."
        )

        return



    text = (

        "💰 رسید پرداخت\n\n"

        f"👤 {user.full_name}\n"

        f"🆔 {user.id}\n"

        f"🔗 @{user.username or 'ندارد'}\n\n"

        f"📦 {info['buy']}\n\n"

        "برای پاسخ روی پیام ریپلای کنید."

    )


    await context.bot.send_photo(

        chat_id=db["owner"],

        photo=update.message.photo[-1].file_id,

        caption=text

    )


    await update.message.reply_text(
        "✅ رسید ارسال شد."
    )



# =====================
# پیام مالک
# =====================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    # فقط مالک

    if user.id == db["owner"]:

        if update.message.reply_to_message:

            replied = update.message.reply_to_message.text or ""

            target = None


            for uid in db["users"]:

                if uid in replied:

                    target = uid
                    break


            if target:

                await context.bot.copy_message(

                    chat_id=int(target),

                    from_chat_id=update.message.chat_id,

                    message_id=update.message.message_id

                )


                await update.message.reply_text(
                    "✅ ارسال شد"
                )


                return



    await update.message.reply_text(
        "از منو استفاده کنید.",
        reply_markup=main_menu(user.id)
    )



# =====================
# پنل مالک
# =====================

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
                callback_data="owner"
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



# =====================
# دکمه پنل
# =====================

async def admin_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if query.from_user.id != db["owner"]:

        return


    if query.data == "on":

        db["enabled"] = True
        save_data(db)

        await query.answer(
            "روشن شد"
        )


    elif query.data == "off":

        db["enabled"] = False
        save_data(db)

        await query.answer(
            "خاموش شد"
        )



# =====================
# اجرا
# =====================

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
            filters.ALL,
            message_handler
        )
    )


    print(
        "🤖 BOT STARTED"
    )


    app.run_polling()



if __name__ == "__main__":

    main()
