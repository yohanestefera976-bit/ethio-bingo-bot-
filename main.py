import telebot
from telebot import types
import sqlite3

# የቦት ቶክን እና የቴሌብር መረጃ
TOKEN = "8939073259:AAH7PDuM16hoIFrpBo9laCZH2GduyyD2MDc"
bot = telebot.TeleBot(TOKEN)

# ----------------- ዳታቤዝ ማዘጋጀት -----------------
def init_db():
    conn = sqlite3.connect('bingo_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # የተጠቃሚዎች ቴብል
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')
    
    # የጨዋታ ቲኬቶች/ካርቴላዎች ቴብል
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            cartela_number INTEGER,
            stake REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# የተጠቃሚ መረጃ ማግኛ ወይም ምዝገባ
def get_or_create_user(user_id, username):
    conn = sqlite3.connect('bingo_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        cursor.execute('INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)', (user_id, username, 0.0))
        conn.commit()
        conn.close()
        return 0.0
    else:
        conn.close()
        return result[0]

def update_balance(user_id, amount):
    conn = sqlite3.connect('bingo_wallet.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

# ----------------- የቴሌግራም ትዕዛዞች -----------------

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    balance = get_or_create_user(user_id, username)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_play = types.KeyboardButton("🎮 Play Keno / Bingo")
    btn_balance = types.KeyboardButton("💰 ሒሳቤን ማየት")
    btn_deposit = types.KeyboardButton("💳 ሒሳብ መሙላት")
    btn_support = types.KeyboardButton("🛠 Contact Support")
    markup.add(btn_play, btn_balance, btn_deposit, btn_support)
    
    welcome_text = (
        f"ሰላም <b>{username}</b>! እንኳን ወደ <b>Beteseb Bingo & Keno</b> በደህና መጡ።\n\n"
        f"💳 ቀሪ ሒሳብዎ: <b>{balance} ብር</b>\n\n"
        "ከታች ያሉትን አማራጮች በመጠቀም ጨዋታውን መጀመር ይችላሉ!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "💰 ሒሳቤን ማየት")
def check_my_balance(message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    balance = get_or_create_user(user_id, username)
    bot.send_message(message.chat.id, f"💳 አሁን ያለዎት ቀሪ ሒሳብ: <b>{balance} ብር</b>", parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "💳 ሒሳብ መሙላት")
def deposit_prompt(message):
    deposit_text = (
        "<b>💳 የኪስ ቦርሳዎን ለመሙላት፦</b>\n\n"
        "እባክዎ ከታች ባለው የቴሌብር ቁጥር የሚፈልጉትን ገንዘብ ያስተላልፉ፡\n\n"
        "📱 <b>የቴሌብር ቁጥር፦</b> <code>0993727789</code>\n"
        "👤 <b>የባለቤቱ ስም፦</b> ዩሐንስ (Yohannes)\n\n"
        "⚠️ ገንዘብ ካስተላለፉ በኋላ የደረሰኝን (Screenshot) ወይም የግብይቱን <b>Transaction ID / ሪሲት</b> እዚህ ይላኩ፤ አስተዳዳሪው ያረጋግጥልዎታል።"
    )
    bot.send_message(message.chat.id, deposit_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "🎮 Play Keno / Bingo")
def play_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_stake10 = types.InlineKeyboardButton("🎮 Play 10 ETB", callback_data="stake_10")
    btn_stake20 = types.InlineKeyboardButton("🎮 Play 20 ETB", callback_data="stake_20")
    markup.add(btn_stake10, btn_stake20)
    
    bot.send_message(message.chat.id, "👇 የሚፈልጉትን የመወራረጃ መጠን (Stake) ይምረጡ፡", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("stake_"))
def handle_stake(call):
    user_id = call.from_user.id
    stake_amount = float(call.data.split("_")[1])
    current_balance = get_or_create_user(user_id, call.from_user.first_name)
    
    if current_balance >= stake_amount:
        # ከሂሳብ ላይ መቀነስ
        update_balance(user_id, -stake_amount)
        new_bal = get_or_create_user(user_id, call.from_user.first_name)
        
        bot.answer_callback_query(call.id, "Success!")
        bot.send_message(
            call.message.chat.id,
            f"✅ ውርርድዎ ተሳክቷል! <b>{stake_amount} ብር</b> ተቀናሽ ሆኗል።\n"
            f"💳 አዲስ ቀሪ ሒሳብዎ: <b>{new_bal} ብር</b>\n\n"
            "አሁን የካርቴላ ቁጥርዎን ይምረጡ (ለምሳሌ ከ 1 እስከ 400 ያሉትን ቁጥሮች ያስገቡ)፦",
            parse_mode="HTML"
        )
    else:
        bot.answer_callback_query(call.id, "Insufficient balance!", show_alert=True)
        bot.send_message(
            call.message.chat.id,
            "❌ በቂ የኪስ ቦርሳ ሒሳብ የለዎትም! እባክዎ በመጀመሪያ <b>💳 ሒሳብ መሙላት</b> የሚለውን በመንካት አካውንትዎን ይሙሉ (0993727789 - ዩሐንስ)።",
            parse_mode="HTML"
        )

@bot.message_handler(func=lambda message: message.text == "🛠 Contact Support")
def contact_support(message):
    support_text = (
        "🛠 <b>የዕርዳታ ማዕከል (Support)</b>\n\n"
        "ለማንኛውም ጥያቄ ወይም የክፍያ ማረጋገጫ እባክዎ ከታች ባለው አድራሻ ያግኙን፡\n"
        "👉 @Ethiobingokecosupport"
    )
    bot.send_message(message.chat.id, support_text, parse_mode="HTML")

# ቦቱን ማስጀመር
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
