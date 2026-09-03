import telebot
from telebot import types

TOKEN = "8939073259:AAH7PDuM16hoIFrpBo9laCZH2GduyyD2MDc"
bot = telebot.TeleBot(TOKEN)

# In-memory database: {user_id: {"phone": phone_str, "balance": float, "registered": bool}}
user_db = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if user_id not in user_db or not user_db[user_id].get("registered"):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📱 ስልክ ቁጥር ሼር አድርግ / ምዝገባ", callback_data="register_prompt")
        markup.add(btn)
        bot.send_message(
            message.chat.id,
            "ሰላም አቶ ቶቴ! እንኳን ወደ Beteseb Bingo & Keno በደህና መጡ።\n\n"
            "⚠️ ጨዋታዎችን ለመጀመር እና ለመጫወት መጀመሪያ በስልክ ቁጥርዎ መመዝገብ አለብዎት።\n"
            "🎁 ለአዲስ ተመዝጋቢዎች 10 ብር ነጻ ቦነስ ይሸለማሉ!",
            reply_markup=markup
        )
        return

    balance = user_db[user_id]["balance"]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🎮 Play Keno / Bingo", callback_data="play_menu"))
    markup.row(types.InlineKeyboardButton("💰 ሒሳብ መሞላት", callback_data="deposit"), types.InlineKeyboardButton("📊 ሒሳብ ማየት", callback_data="balance"))
    
    bot.send_message(
        message.chat.id,
        f"ሰላም አቶ ቶቴ! እንኳን ወደ Beteseb Bingo & Keno በደህና መጡ።\n\n"
        f"💳 ቀሪ ሒሳብዎ: {balance} ብር\n\n"
        f"ከዚህ በታች ያሉትን አማራጮች በመጠቀም ጨዋታውን መጀመር ይችላሉ!",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    
    if call.data == "register_prompt":
        bot.send_message(call.message.chat.id, "እባክዎ ለመመዝገብ ስልክ ቁጥርዎን ይጻፉ (ለምሳሌ: 0911223344)።")
        bot.register_next_step_handler(call.message, process_phone)

    elif call.data == "play_menu":
        if user_id not in user_db or not user_db[user_id].get("registered"):
            bot.answer_callback_query(call.id, "❌ እባክዎ በመጀመሪያ ስልክ ቁጥርዎን ይመዝገቡ!", show_alert=True)
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Play 10 ETB", callback_data="stake_10"), types.InlineKeyboardButton("Play 20 ETB", callback_data="stake_20"))
        markup.row(types.InlineKeyboardButton("🔙 ወደ ዋናው ምናሌ", callback_data="main_menu"))
        bot.edit_message_text("🟡 የሚፈልጉትን የመውረጪ መጠን (Stake) ይምረጡ:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "balance":
        balance = user_db.get(user_id, {}).get("balance", 0.0)
        bot.answer_callback_query(call.id, f"📊 የእርስዎ የሒሳብ መጠን: {balance} ብር", show_alert=True)

    elif call.data == "deposit":
        bot.send_message(call.message.chat.id, "💳 አካውንት ለመሞላት እባክዎ በሰጠነው ቁጥር (0993727789 - ዮሐንስ) በባንክ ወይም በቴሌብር ያስተላልፉ።")

    elif call.data.startswith("stake_"):
        stake = float(call.data.split("_")[1])
        if user_db[user_id]["balance"] < stake:
            bot.send_message(
                call.message.chat.id,
                f"❌ በቂ የሂሳብ ቀሪ የለዎትም! አሁን ያለዎት ሒሳብ: {user_db[user_id]['balance']} ብር ነው።\n"
                "እባክዎ በመጀመሪያ ➖ ሒሳብ መሞላት ይሙሉ።\n(0993727789 - ዮሐንስ)"
            )
        else:
            user_db[user_id]["balance"] -= stake
            bot.send_message(call.message.chat.id, f"🎲 ጨዋታው ተጀምሯል! {stake} ብር ተቀናሽ ሆኗል። ቀሪ ሒሳብዎ: {user_db[user_id]['balance']} ብር ነው። መልካም ዕድል!")

    elif call.data == "main_menu":
        send_welcome(call.message)

def process_phone(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    user_db[user_id] = {
        "phone": phone,
        "balance": 10.0,  # 10 Birr welcome bonus
        "registered": True
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🎮 Play Keno / Bingo", callback_data="play_menu"))
    
    bot.send_message(
        message.chat.id,
        f"✅ በအောင်မြင်ነት ተመዝግበዋል! ስልክ ቁጥር: {phone}\n"
        f"🎁 እንኳን ደስ አለዎት! ለአዲስ ምዝገባ **10.0 ብር** ቦነስ ተሰጥቶዎታል።\n"
        f"💳 አሁን ያለዎት ጠቅላላ ሒሳብ: 10.0 ብር ነው።",
        reply_markup=markup,
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
          
