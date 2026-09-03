import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot Token provided
TOKEN = "8939073259:AAH7PDuM16hoIFrpBo9laCZH2GduyyD2MDc"

# In-memory database for users: {user_id: {"phone": phone_str, "balance": float, "registered": bool}}
user_db = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user is registered
    if user_id not in user_db or not user_db[user_id].get("registered"):
        keyboard = [
            [InlineKeyboardButton("📱 ስልክ ቁጥር ሼር አድርግ / ምዝገባ", callback_data="register_prompt")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "ሰላም አቶ ቶቴ! እንኳን ወደ Beteseb Bingo & Keno በደህና መጡ።\n\n"
            "⚠️ ጨዋታዎችን ለመጀመር እና ለመጫወት መጀመሪያ በስልክ ቁጥርዎ መመዝገብ አለብዎት።\n"
            "🎁 ለአዲስ ተመዝጋቢዎች 10 ብር ነጻ ቦነስ ይሸለማሉ!",
            reply_markup=reply_markup
        )
        return

    # If already registered
    balance = user_db[user_id]["balance"]
    keyboard = [
        [InlineKeyboardButton("🎮 Play Keno / Bingo", callback_data="play_menu")],
        [InlineKeyboardButton("💰 ሒሳብ መሞላት", callback_data="deposit"), InlineKeyboardButton("📊 ሒሳብ ማየት", callback_data="balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"ሰላም አቶ ቶቴ! እንኳን ወደ Beteseb Bingo & Keno በደህና መጡ።\n\n"
        f"💳 ቀሪ ሒሳብዎ: {balance} ብር\n\n"
        f"ከዚህ በታች ያሉትን አማራጮች በመጠቀም ጨዋታውን መጀመር ይችላሉ!",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "register_prompt":
        # Ask user to send phone number
        await query.message.reply_text(
            "እባክዎ ለመመዝገብ ስልክ ቁጥርዎን ይጻፉ (ለምሳሌ: 0911223344) ወይም ከታች ያለውን ቁልፍ ይጠቀሙ።"
        )
        context.user_data['waiting_for_phone'] = True

    elif query.data == "play_menu":
        if user_id not in user_db or not user_db[user_id].get("registered"):
            await query.message.reply_text("❌ እባክዎ በመጀመሪያ ስልክ ቁጥርዎን ይመዝገቡ!")
            return
        
        keyboard = [
            [InlineKeyboardButton("Play 10 ETB", callback_data="stake_10"), InlineKeyboardButton("Play 20 ETB", callback_data="stake_20")],
            [InlineKeyboardButton("🔙 ወደ ዋናው ምናሌ", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🟡 የሚፈልጉትን የመውረጪ መጠን (Stake) ይምረጡ:", reply_markup=reply_markup)

    elif query.data == "balance":
        balance = user_db.get(user_id, {}).get("balance", 0.0)
        await query.message.reply_text(f"📊 የእርስዎ የሒሳብ መጠን: {balance} ብር")

    elif query.data == "deposit":
        await query.message.reply_text("💳 አካውንት ለመሞላት እባክዎ በሰጠነው ቁጥር (0993727789 - ዮሐንስ) በባንክ ወይም በቴሌብር ያስተላልፉ።")

    elif query.data.startswith("stake_"):
        stake = float(query.data.split("_")[1])
        if user_db[user_id]["balance"] < stake:
            await query.message.reply_text(
                f"❌ በቂ የሂሳብ ቀሪ የለዎትም! አሁን ያለዎት ሒሳብ: {user_db[user_id]['balance']} ብር ነው።\n"
                "እባክዎ በመጀመሪያ ➖ ሒሳብ መሞላት ይሙሉ።\n(0993727789 - ዮሐንስ)"
            )
        else:
            user_db[user_id]["balance"] -= stake
            await query.message.reply_text(f"🎲 ጨዋታው ተጀምሯል! {stake} ብር ተቀናሽ ሆኗል። ቀሪ ሒሳብዎ: {user_db[user_id]['balance']} ብር ነው። መልካም ዕድል!")

    elif query.data == "main_menu":
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get('waiting_for_phone'):
        # Save phone and give 10 ETB bonus
        phone = text.strip()
        user_db[user_id] = {
            "phone": phone,
            "balance": 10.0,  # 10 Birr welcome bonus
            "registered": True
        }
        context.user_data['waiting_for_phone'] = False
        
        keyboard = [
            [InlineKeyboardButton("🎮 Play Keno / Bingo", callback_data="play_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ በצלካ ተመዝግበዋል! ስልክ ቁጥር: {phone}\n"
            f"🎁 እንኳን ደስ አለዎት! ለአዲስ ምዝገባ **10.0 ብር** ቦነስ ተሰጥቶዎታል።\n"
            f"💳 አሁን ያለዎት ጠቅላላ ሒሳብ: 10.0 ብር ነው።",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("እባክዎ `/start` በመጫን ቦቱን ያስጀምሩ።")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
