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


# =========================
# تنظیمات
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

OWNER_ID = 6303851350

CHANNEL_ID = "@etlaeeeeeee"
CHANNEL_LINK = "https://t.me/etlaeeeeeee"

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
            "users": {},
            "pending_reply": {}
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
# ساخت کاربر
# =========================

def create_user(user_id):

    user_id = str(user_id)

    if user_id not in db["users"]:

        db["users"][user_id] = {

            "referrals": [],

            "claimed": 0,

            "gift": False
        }

        save_data(db)



# =========================
# ثبت زیرمجموعه
# =========================

def add_referral(
    inviter,
    new_user
):

    inviter = str(inviter)
    new_user = str(new_user)


    if inviter == new_user:
        return


    create_user(inviter)
    create_user(new_user)


    refs = db["users"][inviter]["referrals"]


    # ضد ثبت دوباره

    if new_user in refs:
        return


    refs.append(new_user)



    # هر ۳ نفر یک گیگ

    if len(refs) - db["users"][inviter]["claimed"] >= 3:

        db["users"][inviter]["gift"] = True


    save_data(db)



# =========================
# چک عضویت کانال
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


        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:

            return True


        return False


    except Exception:

        return False



# =========================
# لینک دعوت
# =========================

def make_ref_link(
    username,
    user_id
):

    return (
        f"https://t.me/{username}"
        f"?start={user_id}"
    )



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
# استارت
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    # عضویت اجباری

    joined = await check_join(
        user.id,
        context
    )


    if not joined:

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
                    callback_data="check_join"
                )
            ]

        ]


        await update.message.reply_text(
            "⚠️ برای استفاده از ربات اول عضو کانال شوید.",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return



    create_user(
        user.id
    )


    # ثبت دعوت

    if context.args:

        inviter = context.args[0]

        if inviter.isdigit():

            add_referral(
                inviter,
                user.id
            )



    await update.message.reply_text(

        "🤖 خوش آمدید\n\n"
        "از منوی زیر استفاده کنید:",

        reply_markup=main_menu(
            user.id
        )
    )
    # =========================
# ارسال درخواست به مالک
# =========================

async def send_to_owner(
    context,
    user,
    text
):

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



# =========================
# مدیریت دکمه‌ها
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

        joined = await check_join(
            user_id,
            context
        )


        if joined:

            create_user(
                user_id
            )


            await query.edit_message_text(

                "✅ عضویت تایید شد.",

                reply_markup=main_menu(
                    user_id
                )

            )


        else:

            await query.answer(

                "❌ هنوز عضو کانال نیستید",

                show_alert=True

            )


        return



    # =====================
    # زیرمجموعه
    # =====================

    if query.data == "ref":


        me = await context.bot.get_me()


        link = make_ref_link(
            me.username,
            user_id
        )


        count = len(
            db["users"]
            .get(
                str(user_id),
                {}
            )
            .get(
                "referrals",
                []
            )
        )


        await query.edit_message_text(

            "👥 سیستم زیرمجموعه\n\n"

            f"تعداد دعوت موفق: {count}\n\n"

            "برای هر ۳ نفر زیرمجموعه "
            "۱ گیگ هدیه دریافت می‌کنید.\n\n"

            "لینک دعوت شما:\n"

            f"{link}",

            reply_markup=main_menu(
                user_id
            )

        )

        return



    # =====================
    # دریافت گیگ
    # =====================

    if query.data == "gift":


        data = db["users"].get(
            str(user_id)
        )


        if not data or not data["gift"]:

            await query.answer(

                "❌ هنوز شرایط دریافت کامل نشده",

                show_alert=True

            )

            return



        text = (

            "🎁 درخواست کانفیگ زیرمجموعه\n\n"

            f"👤 نام: {user.full_name}\n"

            f"🆔 آیدی: {user.id}\n"

            f"🔗 یوزرنیم: @{user.username if user.username else 'ندارد'}\n\n"

            "کاربر ۳ زیرمجموعه آورده و درخواست ۱ گیگ دارد."

        )


        await send_to_owner(

            context,

            user,

            text

        )


        # بعد از ارسال درخواست

        data["gift"] = False


        # سه نفر مصرف شد

        data["claimed"] += 3


        save_data(db)



        await query.edit_message_text(

            "✅ درخواست شما برای مالک ارسال شد.\n\n"

            "بعد از بررسی، کانفیگ ارسال می‌شود.",

            reply_markup=main_menu(
                user_id
            )

        )


        return



    # =====================
    # پاسخ مالک
    # =====================

    if query.data.startswith("reply_"):


        if user_id != db["owner"]:

            await query.answer(

                "⛔ فقط مالک",

                show_alert=True

            )

            return



        target = query.data.split("_")[1]


        db["pending_reply"][str(user_id)] = target


        save_data(db)


        await query.message.reply_text(

            "✍️ پیام، عکس، فایل یا هر چیزی که می‌خواهید برای کاربر ارسال شود را بفرستید."

        )


        return

# =========================
# پیام‌های مالک و کاربران
# =========================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user


    # =====================
    # پاسخ مالک به کاربر
    # =====================

    if user.id == db["owner"]:

        target = db["pending_reply"].get(
            str(user.id)
        )


        if target:

            try:

                await context.bot.copy_message(

                    chat_id=int(target),

                    from_chat_id=update.message.chat_id,

                    message_id=update.message.message_id

                )


                await update.message.reply_text(
                    "✅ پیام برای کاربر ارسال شد."
                )


                del db["pending_reply"][str(user.id)]

                save_data(db)


            except Exception as e:

                await update.message.reply_text(
                    "❌ ارسال نشد."
                )

            return



    # =====================
    # کاربر
    # =====================

    await update.message.reply_text(

        "لطفاً از منوی ربات استفاده کنید.",

        reply_markup=main_menu(
            user.id
        )

    )



# =========================
# پنل مدیریت
# =========================

def admin_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "🟢 روشن",
                callback_data="bot_on"
            ),

            InlineKeyboardButton(
                "🔴 خاموش",
                callback_data="bot_off"
            )
        ],

        [
            InlineKeyboardButton(
                "👑 انتقال مالکیت",
                callback_data="change_owner"
            )
        ]

    ]


    return InlineKeyboardMarkup(
        keyboard
    )



async def panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_user.id != db["owner"]:

        await update.message.reply_text(
            "⛔ دسترسی ندارید."
        )

        return



    await update.message.reply_text(

        "⚙️ پنل مدیریت",

        reply_markup=admin_menu()

    )



# =========================
# دکمه‌های مدیریت
# =========================

async def admin_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    user = query.from_user


    if user.id != db["owner"]:

        await query.answer(
            "⛔ فقط مالک",
            show_alert=True
        )

        return



    if query.data == "bot_on":

        db["enabled"] = True

        save_data(db)


        await query.answer(
            "🟢 روشن شد"
        )



    elif query.data == "bot_off":

        db["enabled"] = False

        save_data(db)


        await query.answer(
            "🔴 خاموش شد"
        )



    elif query.data == "change_owner":

        await query.message.reply_text(

            "آیدی عددی مالک جدید را ارسال کنید."

        )


        db["change_owner"] = True

        save_data(db)



# =========================
# انتقال مالکیت
# =========================

async def owner_change(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not db.get("change_owner"):

        return False


    if update.effective_user.id != db["owner"]:

        return False



    try:

        new_owner = int(
            update.message.text
        )


        db["owner"] = new_owner

        db["change_owner"] = False

        save_data(db)



        await update.message.reply_text(

            "👑 مالکیت منتقل شد."

        )


    except:

        await update.message.reply_text(

            "❌ آیدی اشتباه است."

        )


    return True



# =========================
# اجرای ربات
# =========================

def main():

    if not BOT_TOKEN:

        raise Exception(
            "BOT_TOKEN پیدا نشد"
        )



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
            admin_buttons,
            pattern="^(bot_|change_owner)"
        )

    )


    app.add_handler(

        MessageHandler(
            filters.ALL,
            owner_change
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
